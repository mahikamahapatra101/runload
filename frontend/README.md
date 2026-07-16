# RunLoad Frontend

The dashboard that sits on top of the RunLoad API. Shows today's
ACWR and risk zone, a load trend chart, and lets me log runs or
upload a CSV without going through Swagger docs.

## Running it

Make sure the backend is running first (`uvicorn app.main:app --reload`
from the `runload-backend` folder, on port 8000).

Then:

```bash
npm install
npm run dev
```

Opens at http://localhost:5173. It talks to the backend at
`http://127.0.0.1:8000`,if you ever run the backend on a different
port, change `API_BASE` in `src/api.js`.

## What's actually in here

```
src/
  App.jsx                    top-level layout, pulls all the data on load
  api.js                     fetch wrappers for each backend endpoint
  components/
    RiskGauge.jsx             the zone gauge, shows where today's ACWR sits
    LoadChart.jsx             daily load bars + acute/chronic lines (recharts)
    UploadCard.jsx            CSV upload + manual run logging, toggled
    SessionsTable.jsx         last 8 logged runs
```

## Notes to self

- The gauge is fixed to a 0-2.0 scale since that covers every
  realistic ACWR value, if a ratio ever goes above 2.0 it just gets
  clamped to the edge of the bar instead of overflowing.
- CORS is wide open on the backend right now since it's just me
  hitting it locally. Would need to lock that down before this ever
  had real users.
- Build with `npm run build` outputs to `dist/`, deployable to
  Vercel or Netlify as a static site once the backend's actually
  hosted somewhere.
