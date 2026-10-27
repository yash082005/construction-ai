import React, { useEffect, useState } from "react";

export const money = (n, cur = "INR") =>
  new Intl.NumberFormat(cur === "INR" ? "en-IN" : "en-US", { style: "currency", currency: cur, maximumFractionDigits: 0 }).format(n ?? 0);

export function Field({ label, children }) {
  return <label className="field"><span>{label}</span>{children}</label>;
}

export function Badge({ level }) {
  return <span className={`badge b-${String(level).toLowerCase().replace(/\s/g, "")}`}>{level}</span>;
}

export function List({ items }) {
  if (!items?.length) return <p className="muted">Nothing reported.</p>;
  return <ul className="list">{items.map((t, i) => <li key={i}>{t}</li>)}</ul>;
}

export function Block({ title, children }) {
  return <section className="block"><h3>{title}</h3>{children}</section>;
}

export function Confidence({ value }) {
  const pct = Math.round((value ?? 0) * 100);
  return (
    <div className="conf" title="How sure the AI is about this result">
      <div className="conf-bar"><i style={{ width: `${pct}%` }} /></div>
      <span>{pct}% confidence{pct < 50 ? " — retake the photo or add details" : ""}</span>
    </div>
  );
}

export function Result({ state }) {
  if (state.loading) return <div className="result empty"><div className="spin" />Analysing…</div>;
  if (state.error)
    return <div className="result err"><strong>{state.error}</strong><p>{state.detail}</p></div>;
  return null;
}

export function useRunner() {
  const [state, setState] = useState({ loading: false, data: null, error: "", detail: "" });
  const run = async (fn) => {
    setState({ loading: true, data: null, error: "", detail: "" });
    const r = await fn();
    setState(r.ok ? { loading: false, data: r.data, error: "", detail: "" } : { loading: false, data: null, error: r.error, detail: r.detail });
  };
  return [state, run];
}

export function ImagePicker({ files, setFiles }) {
  const [urls, setUrls] = useState([]);
  useEffect(() => {
    const u = files.map((f) => URL.createObjectURL(f));
    setUrls(u);
    return () => u.forEach(URL.revokeObjectURL);
  }, [files]);
  return (
    <div>
      <label className="drop">
        <input type="file" accept="image/jpeg,image/png,image/webp" multiple
          onChange={(e) => setFiles([...e.target.files].slice(0, 4))} />
        <b>Choose photos</b><span>JPG, PNG or WebP · up to 4 images</span>
      </label>
      {urls.length > 0 && <div className="thumbs">{urls.map((u) => <img key={u} src={u} alt="Selected site photo" />)}</div>}
    </div>
  );
}
