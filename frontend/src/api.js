   const BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

   async function call(path, options) {
     try {
       const res = await fetch(`${BASE}/api${path}`, options);
       const body = await res.json().catch(() => null);
       if (!res.ok) return { ok: false, error: body?.error || `Request failed (${res.status})`, detail: body?.detail || body?.detail?.[0]?.msg || "" };
       return { ok: true, data: body };
     } catch {
       return { ok: false, error: "Cannot reach the server", detail: "The backend may be waking up. Wait a minute and try again." };
     }
   }
   export const postJson = (path, payload) =>
     call(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
   export const postForm = (path, files, fields = {}) => {
     const fd = new FormData();
     files.forEach((f) => fd.append("images", f));
     Object.entries(fields).forEach(([k, v]) => fd.append(k, v));
     return call(path, { method: "POST", body: fd });
   };
   export const getHealth = () => call("/health");