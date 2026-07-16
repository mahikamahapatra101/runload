import { useEffect, useState, useCallback } from "react";
import RiskGauge from "./components/RiskGauge";
import LoadChart from "./components/LoadChart";
import UploadCard from "./components/UploadCard";
import SessionsTable from "./components/SessionsTable";
import { getCurrentRisk, getTrainingLoad, getSessions } from "./api";

export default function App() {
  // Simple, and straightforward state management for storing API payloads
  const [risk, setRisk] = useState(null);
  const [loadSeries, setLoadSeries] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  /**
   * This fetches all required data from our local FastAPI backend in one go.
   * Wrapped in useCallback so React doesn't recreate this function on every render,
   * which would otherwise trigger an infinite loop inside the useEffect block below.
   */
  const refresh = useCallback(async () => {
    setError(null);
    try {
      // Fetching all three API endpoints in parallel using Promise.all
      // to avoid request "waterfalling" and keep page loads snappy.
      const [riskData, loadData, sessionData] = await Promise.all([
        getCurrentRisk(),
        getTrainingLoad(),
        getSessions(),
      ]);
      setRisk(riskData);
      setLoadSeries(loadData);
      setSessions(sessionData);
    } catch (err) {
      // Friendly fallback alert pointing straight to the local backend startup command
      setError(
        "Can't reach the backend. Make sure it's running at http://127.0.0.1:8000 (uvicorn app.main:app --reload)."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial mount:  load up all our data as soon as the app opens
  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="app">
      <header className="app-header">
        <div className="wordmark">
          RUN<span className="wordmark-accent">LOAD</span>
        </div>
        <p className="tagline">Training load &amp; injury-risk tracking</p>
      </header>

      {/* Renders global connection error banners at the very top of the page */}
      {error && <div className="error-banner">{error}</div>}

      <section className="hero">
        {loading ? (
          <p className="hint">Loading...</p>
        ) : risk && risk.acwr !== null ? (
          // we have computed data! Show the primary headline, recommendation, and linear gauge
          <>
            <div className="hero-top">
              <div>
                <div className="hero-eyebrow">Today's ACWR</div>
                <div className="hero-value">{risk.acwr.toFixed(2)}</div>
                <div className={`hero-risk-label hero-risk-label--${riskClass(risk.risk_level)}`}>
                  {risk.risk_level}
                </div>
              </div>
              <p className="hero-recommendation">{risk.recommendation}</p>
            </div>
            <RiskGauge acwr={risk.acwr} riskLevel={risk.risk_level} />
          </>
        ) : (
          // Graceful fallback for brand-new users who haven't loaded 14+ days of training history yet
          <div className="hero-empty">
            <p className="hero-eyebrow">
              {risk?.risk_level === "insufficient data" ? "Building your baseline" : "No data yet"}
            </p>
            <p className="hero-recommendation">
              {risk?.recommendation ||
                "Upload your training history or log a run to see your risk status."}
            </p>
          </div>
        )}
      </section>

      {/* Main interactive Recharts trend visualizer */}
      <section className="card">
        <div className="card-head">
          <h2>Training load trend</h2>
        </div>
        <LoadChart data={loadSeries} />
        <div className="legend">
          <span><i className="dot dot--bar" /> Daily load</span>
          <span><i className="dot dot--acute" /> Acute (7d avg)</span>
          <span><i className="dot dot--chronic" /> Chronic (28d avg)</span>
        </div>
      </section>

      {/* Handles CSV uploads and calls our refresh function to reload the graphs on success */}
      <UploadCard onDataChanged={refresh} />

      {/* Tabular breakdown of the actual runs stored in our database */}
      <section className="card">
        <div className="card-head">
          <h2>Recent runs</h2>
        </div>
        <SessionsTable sessions={sessions} />
      </section>

      <footer className="app-footer">
        <p>Risk bands based on Gabbett (2016) — a training-awareness tool, not medical advice.</p>
      </footer>
    </div>
  );
}

/**
 * small utility function to sanitize our backend risk strings (e.g. "sweett spot" or "high risk")
 * into standard lowercase, hyphenated class names (e.g. "sweet-spot", "high-risk") for CSS styling.
 */
function riskClass(level) {
  if (!level) return "unknown";
  return level.replace(/\s+/g, "-");
}