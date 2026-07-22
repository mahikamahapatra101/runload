# RunLoad API

A FastAPI backend that takes my run logs and turns them into a training-load trend and an injury-risk signal. The core idea comes from sports science: the Acute:Chronic Workload Ratio (ACWR), which compares how much I've trained this week against my longer-term average, since spikes in training load are a known injury risk factor.

**Live at:** https://runload-api.onrender.com ([docs](https://runload-api.onrender.com/docs))

## The math behind it

Each run gets a load score using the session-RPE method: `load = duration_min * rpe`, where rpe is how hard the run felt on a 1-10 scale. I picked this over pace-based load because it doesn't need GPS data or a watch, just duration and how it felt.

From there:
- **Acute load** = 7-day rolling average (how much I've trained recently)
- **Chronic load** = 28-day rolling average (my baseline fitness)
- **ACWR** = acute / chronic

Risk bands, based on Gabbett's 2016 research (a commonly cited model, not a medical diagnosis, just a reasonable rule of thumb):

| ACWR | Label |
|---|---|
| < 0.8 | undertrained |
| 0.8 – 1.3 | sweet spot |
| 1.3 – 1.5 | moderate risk |
| > 1.5 | high risk |

## Running it locally

```bash
pip install -r requirements.txt --break-system-packages
uvicorn app.main:app --reload
```

Then go to http://127.0.0.1:8000/docs to test everything through Swagger's UI. Runs on SQLite by default with no setup needed. In production this points at a real Postgres database instead (see `app/database.py`), since Render's free tier wipes local files on restart, learned that one the hard way.

## Endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/` | Health check |
| POST | `/sessions` | Log one run manually |
| GET | `/sessions` | List all logged runs |
| DELETE | `/sessions` | Wipe all data (for testing/demoing) |
| POST | `/upload-csv` | Bulk-import training history from a CSV |
| GET | `/training-load` | Full day-by-day
