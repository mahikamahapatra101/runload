// Pointing directly to our FastAPI backend. If we deploy the backend to a real server later,
// we just need to update this base URL in one place.
const API_BASE = "http://127.0.0.1:8000";

/**
 * Generic helper to handle API responses.
 * Automatically catches HTTP errors, extracts the FastAPI error detail (if any),
 * and bubbles it up so our UI components can show clear error messages.
 */
async function handle(res) {
  if (!res.ok) {
    // If the response isn't 2xx, try to read the JSON error payload safely.
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

// GET /risk/current -> Feeds the header card and the ACWR gauge on the dashboard.
export async function getCurrentRisk() {
  return handle(await fetch(`${API_BASE}/risk/current`));
}

// GET /training-load -> Pulls the full daily history for our charts.
export async function getTrainingLoad() {
  return handle(await fetch(`${API_BASE}/training-load`));
}

// GET /sessions -> Retrieves the raw run logs to show in our activity table.
export async function getSessions() {
  return handle(await fetch(`${API_BASE}/sessions`));
}

// POST /sessions -> Submits a single manually logged run.
export async function addSession(session) {
  return handle(
    await fetch(`${API_BASE}/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(session),
    })
  );
}

// POST /upload-csv -> Handles the multi-part file upload for bulk Strava/CSV importing.
export async function uploadCsv(file) {
  const formData = new FormData();
  // Appending the raw file object. Browser fetch automatically configures 
  // the correct multipart/form-data headers and boundaries for us.
  formData.append("file", file);
  return handle(
    await fetch(`${API_BASE}/upload-csv`, {
      method: "POST",
      body: formData,
    })
  );
}