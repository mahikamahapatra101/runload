import { useState } from "react";
import { uploadCsv, addSession } from "../api";

export default function UploadCard({ onDataChanged }) {
  // Simple tabs: lets the user toggle between uploading a bulk CSV or manual  form logging
  const [mode, setMode] = useState("csv"); // "csv" | "manual"
  
  // Stores success or failure notifications to display to the user
  const [status, setStatus] = useState(null);
  
  // Spin lock to prevent double clicks or race conditions during API roundtripss
  const [busy, setBusy] = useState(false);

  // Pre-populates the date field to today's local date in YYYY-MM-DD format
  const [form, setForm] = useState({
    date: new Date().toISOString().slice(0, 10),
    distance_mi: "",
    duration_min: "",
    rpe: "",
    notes: "",
  });

  /**
   * Handles the local CSV file selection and automatically pushes it to the backend.
   */
  async function handleFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    setBusy(true);
    setStatus(null);
    try {
      const result = await uploadCsv(file);
      setStatus({ ok: true, text: `Added ${result.sessions_added} runs (${result.date_range}).` });
      
      // Let the parent App component know the DB changed so it can redraw the charts
      onDataChanged();
    } catch (err) {
      setStatus({ ok: false, text: err.message });
    } finally {
      setBusy(false);
      // Reset the file input so the user can upload the same file again if they fixed errors
      e.target.value = "";
    }
  }

  /**
   * Cleans up form inputs and submits a single manual run to the API database.
   */
  async function handleManualSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setStatus(null);
    try {
      await addSession({
        date: form.date,
        // Convert string inputs from React's state into actual   floats or nulls for database validation
        distance_mi: form.distance_mi ? parseFloat(form.distance_mi) : null,
        duration_min: parseFloat(form.duration_min),
        rpe: parseFloat(form.rpe),
        notes: form.notes || null,
      });
      setStatus({ ok: true, text: "Run logged." });
      
      // Clear out numbers and text so the form is clean for the next run, but preserve the date
      setForm({ ...form, distance_mi: "", duration_min: "", rpe: "", notes: "" });
      
      // Refresh global graphs
      onDataChanged();
    } catch (err) {
      setStatus({ ok: false, text: err.message });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <div className="card-head">
        <h2>Log training</h2>
        {/* Simple segmented control container */}
        <div className="toggle">
          <button
            className={mode === "csv" ? "toggle-btn toggle-btn--active" : "toggle-btn"}
            onClick={() => setMode("csv")}
          >
            CSV upload
          </button>
          <button
            className={mode === "manual" ? "toggle-btn toggle-btn--active" : "toggle-btn"}
            onClick={() => setMode("manual")}
          >
            Log a run
          </button>
        </div>
      </div>

      {mode === "csv" ? (
        // Mode A: CSV Drag & Drop / Selection area
        <div className="upload-zone">
          <label className="upload-label">
            <input type="file" accept=".csv" onChange={handleFile} disabled={busy} />
            {busy ? "Uploading..." : "Choose a CSV file"}
          </label>
          <p className="hint">Columns: date, distance_mi, duration_min, rpe, notes</p>
        </div>
      ) : (
        // Mode B: Interactive Manual Input Form
        <form className="manual-form" onSubmit={handleManualSubmit}>
          <div className="field-row">
            <label>
              Date
              <input
                type="date"
                value={form.date}
                onChange={(e) => setForm({ ...form, date: e.target.value })}
                required
              />
            </label>
            <label>
              Distance (mi)
              <input
                type="number"
                step="0.1"
                value={form.distance_mi}
                onChange={(e) => setForm({ ...form, distance_mi: e.target.value })}
                placeholder="optional"
              />
            </label>
          </div>
          <div className="field-row">
            <label>
              Duration (min)
              <input
                type="number"
                step="0.1"
                value={form.duration_min}
                onChange={(e) => setForm({ ...form, duration_min: e.target.value })}
                required
              />
            </label>
            <label>
              RPE (1-10)
              <input
                type="number"
                step="0.5"
                min="1"
                max="10"
                value={form.rpe}
                onChange={(e) => setForm({ ...form, rpe: e.target.value })}
                required
              />
            </label>
          </div>
          <label>
            Notes
            <input
              type="text"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              placeholder="optional"
            />
          </label>
          <button type="submit" className="btn-primary" disabled={busy}>
            {busy ? "Saving..." : "Log run"}
          </button>
        </form>
      )}

      {/* Render validation and API response states if they exist */}
      {status && (
        <p className={status.ok ? "status status--ok" : "status status--error"}>{status.text}</p>
      )}
    </div>
  );
}