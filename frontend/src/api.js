// Single place that talks to FastAPI. Always resolves to {ok, data|error}.
// Connect the React frontend to the deployed FastAPI backend
const API_BASE_URL = "https://construction-ai-1.onrender.com";

async function call(path, options = {}) {
  try {
    const res = await fetch(
      `${API_BASE_URL}/api${path}`,
      options
    );

    const body = await res.json().catch(() => ({}));

    if (!res.ok) {
      return {
        ok: false,
        error: body.error || `Request failed (${res.status})`,
        detail: body.detail || ""
      };
    }

    return { ok: true, data: body };
  } catch (error) {
    return {
      ok: false,
      error: "Cannot reach the server",
      detail: error.message
    };
  }
}
