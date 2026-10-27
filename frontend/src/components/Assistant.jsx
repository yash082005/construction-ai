import React, { useState } from "react";
import { postJson } from "../api";
import { Block, Field, List, Result, useRunner } from "./ui";

function Daily() {
  const [f, setF] = useState({ site_name: "", stage: "Foundation", crew_size: 10, notes: "" });
  const [st, run] = useRunner();
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const d = st.data;
  return (
    <div className="split">
      <form className="panel" onSubmit={(e) => { e.preventDefault(); run(() => postJson("/daily", { ...f, crew_size: +f.crew_size })); }}>
        <h2>Daily site plan</h2>
        <Field label="Site name"><input value={f.site_name} onChange={set("site_name")} /></Field>
        <div className="two">
          <Field label="Stage"><select value={f.stage} onChange={set("stage")}>{["Excavation", "Foundation", "Structure", "Masonry", "Plumbing & electrical", "Plastering", "Finishing"].map((x) => <option key={x}>{x}</option>)}</select></Field>
          <Field label="Crew size"><input type="number" min="0" value={f.crew_size} onChange={set("crew_size")} /></Field>
        </div>
        <Field label="Notes (optional)"><textarea rows={3} value={f.notes} onChange={set("notes")} placeholder="Deliveries expected, issues from yesterday" /></Field>
        <button className="primary" disabled={st.loading}>Plan today</button>
      </form>
      <div>
        <Result state={st} />
        {!st.loading && !st.error && !d && <div className="result empty">Today's plan appears here.</div>}
        {d && <div className="result">
          <Block title="Priorities"><List items={d.priorities} /></Block>
          <Block title="Checklist">{d.checklist.map((c, i) => <label className="check" key={i}><input type="checkbox" /> {c}</label>)}</Block>
          <Block title="Risks"><List items={d.risks} /></Block>
          {d.notes && <p className="note">{d.notes}</p>}
        </div>}
      </div>
    </div>
  );
}

function Weather() {
  const [f, setF] = useState({ location: "", activity: "Concrete pouring" });
  const [st, run] = useRunner();
  const d = st.data;
  return (
    <div className="split">
      <form className="panel" onSubmit={(e) => { e.preventDefault(); run(() => postJson("/weather", f)); }}>
        <h2>Weather advisory</h2>
        <Field label="Site city"><input required value={f.location} onChange={(e) => setF({ ...f, location: e.target.value })} /></Field>
        <Field label="Planned activity"><select value={f.activity} onChange={(e) => setF({ ...f, activity: e.target.value })}>{["Concrete pouring", "Crane lifting", "Excavation", "Roofing", "Painting / plastering", "Steel fixing", "General work"].map((x) => <option key={x}>{x}</option>)}</select></Field>
        <button className="primary" disabled={st.loading}>Check conditions</button>
      </form>
      <div>
        <Result state={st} />
        {!st.loading && !st.error && !d && <div className="result empty">The advisory appears here.</div>}
        {d && <div className="result">
          <div className="head"><h2>{d.weather.location}</h2><span className={`badge s-${d.work_suitability.replace(/\s/g, "").toLowerCase()}`}>{d.work_suitability}</span></div>
          <div className="stats">
            <div><b>{d.weather.temperature_c ?? "–"}°C</b><span>Temperature</span></div>
            <div><b>{d.weather.wind_kmh ?? "–"} km/h</b><span>Wind</span></div>
            <div><b>{d.weather.precipitation_mm ?? "–"} mm</b><span>Rain now</span></div>
          </div>
          <p>{d.summary}</p>
          <Block title="Go ahead with"><List items={d.favourable_activities} /></Block>
          <Block title="Avoid"><List items={d.activities_to_avoid} /></Block>
          <Block title="Recommendations"><List items={d.recommendations} /></Block>
        </div>}
      </div>
    </div>
  );
}

function Knowledge() {
  const [q, setQ] = useState("");
  const [st, run] = useRunner();
  const d = st.data;
  return (
    <div className="split">
      <form className="panel" onSubmit={(e) => { e.preventDefault(); run(() => postJson("/knowledge", { question: q })); }}>
        <h2>Ask the knowledge assistant</h2>
        <Field label="Your question"><textarea rows={5} required minLength={3} value={q} onChange={(e) => setQ(e.target.value)} placeholder="What is the minimum clear cover for a slab in a moderate exposure?" /></Field>
        <button className="primary" disabled={st.loading || q.trim().length < 3}>Ask</button>
      </form>
      <div>
        <Result state={st} />
        {!st.loading && !st.error && !d && <div className="result empty">The answer appears here.</div>}
        {d && <div className="result">
          <p className="lead">{d.answer}</p>
          <Block title="Key points"><List items={d.key_points} /></Block>
          <Block title="Standards"><List items={d.standards_or_references} /></Block>
          <Block title="Ask next">{d.follow_up_questions.map((x) => <button className="link" key={x} onClick={() => setQ(x)}>{x}</button>)}</Block>
        </div>}
      </div>
    </div>
  );
}

export default function Assistant() {
  const [tab, setTab] = useState("daily");
  const tabs = { daily: "Daily plan", weather: "Weather", knowledge: "Knowledge" };
  return (
    <div>
      <div className="subtabs">{Object.entries(tabs).map(([k, v]) => <button key={k} className={tab === k ? "on" : ""} onClick={() => setTab(k)}>{v}</button>)}</div>
      {tab === "daily" ? <Daily /> : tab === "weather" ? <Weather /> : <Knowledge />}
    </div>
  );
}
