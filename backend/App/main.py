"""
RunLoad API

Takes my run logs and turns them into a training-load time series
and an injury-risk signal using ACWR (acute:chronic workload ratio).
The actual math and reasoning behind the risk bands lives in
app/training_load.py.

To run it:
    uvicorn app.main:app --reload

Then http://127.0.0.1:8000/docs gives you the interactive API docs.
"""

import csv
import io
from datetime import date as date_type

import pandas as pd
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas, training_load
from .database import engine, get_db

# Creates the tables in runload.db automatically if they don't exist yet.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RunLoad API",
    description="Training-load and injury-risk tracking for runners, based on ACWR.",
    version="1.0.0",
)

# leaving CORS wide open for now since it's just me hitting this from
# a React app on a different port. would need to lock this down to a
# real frontend URL before this ever touched actual user data.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Quick helper to format our SQLAlchemy models into a basic dict 
# so our pandas processing script can easily read it.
def _session_to_dict(s: models.TrainingSession) -> dict:
    return {"date": s.date, "load": s.load}


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "RunLoad API"}


@app.post("/sessions", response_model=schemas.SessionOut, tags=["sessions"])
def add_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):
    """log one run by hand"""
    # Calculate 'Session RPE' load = duration (mins) * how hard it felt (1-10)
    load = session.duration_min * session.rpe
    db_session = models.TrainingSession(
        date=session.date,
        distance_mi=session.distance_mi,
        duration_min=session.duration_min,
        rpe=session.rpe,
        load=load,
        notes=session.notes,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@app.get("/sessions", response_model=list[schemas.SessionOut], tags=["sessions"])
def list_sessions(db: Session = Depends(get_db)):
    """everything I've logged, oldest first"""
    return (
        db.query(models.TrainingSession)
        .order_by(models.TrainingSession.date.asc())
        .all()
    )


@app.delete("/sessions", tags=["sessions"])
def clear_sessions(db: Session = Depends(get_db)):
    """wipes everything -- useful when I want to test with a clean slate"""
    count = db.query(models.TrainingSession).delete()
    db.commit()
    return {"deleted": count}


@app.post("/upload-csv", response_model=schemas.UploadResult, tags=["sessions"])
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Bulk-imports training history from a CSV with columns:
        date,distance_mi,duration_min,rpe,notes

    - date: YYYY-MM-DD
    - distance_mi: optional, can be blank
    - duration_min: required, minutes
    - rpe: required, 1-10 (how hard the run felt)
    - notes: optional

    this is basically what convert_strava_export.py spits out --
    check sample_data.csv for a working example of the format.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Please upload a .csv file")

    raw = await file.read()
    # 'utf-8-sig' strips out the hidden byte-order mark (BOM) 
    text = raw.decode("utf-8-sig")  
    reader = csv.DictReader(io.StringIO(text))

    # Basic schema safety check before we waste time looping through data
    required_cols = {"date", "duration_min", "rpe"}
    if not required_cols.issubset(set(reader.fieldnames or [])):
        raise HTTPException(
            400,
            f"CSV must include columns: {sorted(required_cols)}. "
            f"Got: {reader.fieldnames}",
        )

    added = 0
    dates_seen = []

    for row_num, row in enumerate(reader, start=2):  # row 1 is the header
        try:
            row_date = date_type.fromisoformat(row["date"].strip())
            duration_min = float(row["duration_min"])
            rpe = float(row["rpe"])
        except (ValueError, KeyError) as e:
            raise HTTPException(400, f"Bad data on CSV row {row_num}: {e}")

        # Keep the perceived exertion scale bound to standard 1-10 Borg CR10
        if not (1 <= rpe <= 10):
            raise HTTPException(400, f"Row {row_num}: rpe must be between 1 and 10")

        distance_raw = (row.get("distance_mi") or "").strip()
        distance_mi = float(distance_raw) if distance_raw else None

        db.add(
            models.TrainingSession(
                date=row_date,
                distance_mi=distance_mi,
                duration_min=duration_min,
                rpe=rpe,
                load=duration_min * rpe,
                notes=(row.get("notes") or "").strip() or None,
            )
        )
        added += 1
        dates_seen.append(row_date)

    db.commit()

    date_range = (
        f"{min(dates_seen)} to {max(dates_seen)}" if dates_seen else "no rows"
    )
    return {"sessions_added": added, "date_range": date_range}


@app.get(
    "/training-load",
    response_model=list[schemas.DailyLoadPoint],
    tags=["analysis"],
)
def get_training_load(db: Session = Depends(get_db)):
    """
    Full day-by-day breakdown: daily load, 7-day acute, 28-day
    chronic, ACWR, risk level. this is what the frontend chart
    will end up plotting.
    """
    sessions = db.query(models.TrainingSession).all()
    series = training_load.compute_training_load_series(
        [_session_to_dict(s) for s in sessions]
    )

    if series.empty:
        return []

    def clean(value):
        """pandas uses NaN for missing values, but that's not valid JSON -- swap for None"""
        # Pandas NaN will completely crash FastAPI's automatic JSON serializer,
        # so we catch and swap NaN values out for a safe Python 'None' (null in JSON).
        if value is None:
            return None
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass
        return value

    return [
        {
            "date": row["date"].date(),
            "daily_load": clean(row["daily_load"]),
            "acute_load": clean(row["acute_load"]),
            "chronic_load": clean(row["chronic_load"]),
            "acwr": clean(row["acwr"]),
            "risk_level": clean(row["risk_level"]),
        }
        for _, row in series.iterrows()
    ]


@app.get("/risk/current", response_model=schemas.CurrentRisk, tags=["analysis"])
def get_current_risk(db: Session = Depends(get_db)):
    """today's risk status -- this is what drives the dashboard's headline card"""
    sessions = db.query(models.TrainingSession).all()
    result = training_load.get_current_risk([_session_to_dict(s) for s in sessions])
    return result