# RunLoad

A training-load and injury-risk tracker I built for my own running data.
Uses ACWR (acute:chronic workload ratio), a sports-science metric that
compares recent training load against a longer baseline to flag when
I'm ramping up too fast.

Started as a way to fill a gap in my portfolio, no live, deployed,
full-stack project, and turned into something I actually use to
check my own training.

## What's here

- **[`backend/`](./backend)** -- Python (FastAPI, SQLAlchemy, pandas). Calculates
  daily training load, rolling ACWR, and risk zone from uploaded run data.
- **[`frontend/`](./frontend)** -- React + Vite dashboard. Shows today's risk on
  a zone gauge, a load trend chart, and lets me log runs or upload a CSV.

Each folder has its own README with setup instructions.

## How it works, quickly

Every run gets a load score (`duration * how hard it felt`), then:
- **acute load** = 7-day rolling average (recent training)
- **chronic load** = 28-day rolling average (baseline fitness)
- **ACWR** = acute / chronic

Ratios outside a "sweet spot" range are associated with higher injury
risk in the research this is based on (Gabbett, 2016). Not medical
advice, just a training-awareness tool.

## Data

My real training data comes from my own Strava export, converted with
a small script that turns Strava's CSV into the format the backend
expects, since Strava doesn't track perceived effort directly.
