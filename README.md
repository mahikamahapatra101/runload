# RunLoad

A training-load and injury-risk tracker I built for my own running data. Uses ACWR (acute:chronic workload ratio), a sports-science metric that compares recent training load against a longer baseline to flag when I'm ramping up too fast.

Started as a way to fill a gap in my portfolio, no live, deployed, full-stack project, and turned into something I actually use to check my own training.

**Live at:** [runload.vercel.app](https://runload.vercel.app)

## What's here

- **backend/** -- Python (FastAPI, SQLAlchemy, pandas), deployed on Render with a Postgres database (via Neon). Calculates daily training load, rolling ACWR, and risk zone from uploaded run data.
- **frontend/** -- React + Vite dashboard, deployed on Vercel. Shows today's risk on a zone gauge, a load trend chart, and lets me log runs or upload a CSV.

Each folder has its own README with setup instructions if you want to run it locally.

## How it works, quickly

Every run gets a load score (duration * how hard it felt), then:
- **acute load** = 7-day rolling average (recent training)
- **chronic load** = 28-day rolling average (baseline fitness)
- **ACWR** = acute / chronic

Ratios outside a "sweet spot" range are associated with higher injury risk in the research this is based on (Gabbett, 2016). Not medical advice, just a training-awareness tool.

## Data

My real training data comes from my own Strava export, converted with a small script that turns Strava's CSV into the format the backend expects, since Strava doesn't track perceived effort directly. Currently running on 1,300+ of my own real runs.

## Status

This is a one-person project right now, no accounts or multi-user support. If I keep building on this, that'd be the next real feature to add.
