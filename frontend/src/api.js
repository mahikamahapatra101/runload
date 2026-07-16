// points at the backend -- change this if you deploy it somewhere
// other than localhost
const API_BASE = "https://runload-api.onrender.com";

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function getCurrentRisk() {
  return handle(await fetch(`${API_BASE}/risk/current`));
}

export async function getTrainingLoad() {
  return handle(await fetch(`${API_BASE}/training-load`));
}

export async function getSessions() {
  return handle(await fetch(`${API_BASE}/sessions`));
}

export async function addSession(session) {
  return handle(
    await fetch(`${API_BASE}/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(session),
    })
  );
}

export async function uploadCsv(file) {
  const formData = new FormData();
  formData.append("file", file);
  return handle(
    await fetch(`${API_BASE}/upload-csv`, {
      method: "POST",
      body: formData,
    })
  );
}
