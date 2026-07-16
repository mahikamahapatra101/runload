# RunLoad API

A FastAPI backend that takes my run logs and turns them into a
training-load trend and an injury-risk signal. The core idea comes
from sports science: the **Acute:Chronic Workload Ratio (ACWR)**,
which compares how much I've trained this week against my longer-term
average, since spikes in training load are a known injury risk factor.

## The math behind it

Each run gets a load score using the session-RPE method:
`load = duration_min * rpe`, where rpe is how hard the run felt on a
1-10 scale. I picked this over pace-based load because it doesn't
need GPS data or a watch, just duration and how it felt.

From there:
- **Acute load** = 7-day rolling average (how much I've trained recently)
- **Chronic load** = 28-day rolling average (my baseline fitness)
- **ACWR** = acute / chronic

Risk bands, based on Gabbett's 2016 research (a commonly cited model,
not a medical diagnosis, just a reasonable rule of thumb):

| ACWR        | Label           |
|-------------|-----------------|
| < 0.8       | undertrained    |
| 0.8 – 1.3   | sweet spot      |
| 1.3 – 1.5   | moderate risk   |
| > 1.5       | high risk       |

## Running it locally

\`\`\`bash
pip install -r requirements.txt --break-system-packages
uvicorn app.main:app --reload
\`\`\`

Then go to http://127.0.0.1:8000/docs to test everything through
Swagger's UI without writing a frontend first.

## Endpoints

| Method | Path              | What it does                                      |
|--------|-------------------|----------------------------------------------------|
| GET    | `/`                | Health check                                       |
| POST   | `/sessions`        | Log one run manually                               |
| GET    | `/sessions`        | List all logged runs                               |
| DELETE | `/sessions`        | Wipe all data (for testing/demoing)                |
| POST   | `/upload-csv`      | Bulk-import training history from a CSV            |
| GET    | `/training-load`   | Full day-by-day load/ACWR/risk series (for a chart)|
| GET    | `/risk/current`    | Today's risk status + a recommendation             |

## CSV format for `/upload-csv`

\`\`\`
date,distance_mi,duration_min,rpe,notes
2026-05-01,5.9,32.6,4.6,easy run
2026-05-02,4.7,29.3,5.4,
\`\`\`

- `date`: YYYY-MM-DD
- `distance_mi`: optional, can leave blank
- `duration_min`: required, in minutes
- `rpe`: required, 1-10
- `notes`: optional

`sample_data.csv` has 35 days of made-up training that ramps into a
load spike near the end, so uploading it is a quick way to see
`/risk/current` actually flag "high risk."

## Getting real data in

- Exported my own history from Strava and reshaped it into this CSV
  format — it's my data, so no issue using it directly.
- Kaggle also has open running/marathon datasets if I want more volume
  to test against later.

## Project structure

\`\`\`
app/
  main.py           FastAPI app + all the endpoints
  models.py         SQLAlchemy model for a training session
  schemas.py        Pydantic request/response validation
  training_load.py  ACWR math + risk classification (the actual logic)
  database.py       SQLite setup (can swap to Postgres later, just change DATABASE_URL)
requirements.txt
sample_data.csv
\`\`\`

