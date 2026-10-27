import React, { useState } from "react";
import { postJson } from "../api";
import { Block, Field, List, Result, money, useRunner } from "./ui";

export default function Planner() {
  const [f, setF] = useState({ project_type: "Residential house", location: "", area_sqft: 1200, floors: 2, quality: "Standard", description: "", currency: "INR" });
  const [st, run] = useRunner();
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const d = st.data;
  const total = d?.total_duration_days || 1;

  return (
    <div className="split">
      <form className="panel" onSubmit={(e) => { e.preventDefault(); run(() => postJson("/plan", { ...f, area_sqft: +f.area_sqft, floors: +f.floors })); }}>
        <h2>Project planning</h2>
        <p className="muted">Get a material list, cost estimate, schedule and a text visualization.</p>
        <Field label="Project type"><select value={f.project_type} onChange={set("project_type")}>{["Residential house", "Apartment block", "Commercial shop", "Warehouse", "Boundary wall / compound"].map((x) => <option key={x}>{x}</option>)}</select></Field>
        <Field label="Location (city)"><input required value={f.location} onChange={set("location")} placeholder="e.g. Pune" /></Field>
        <div className="two">
          <Field label="Built-up area (sq ft)"><input type="number" min="1" required value={f.area_sqft} onChange={set("area_sqft")} /></Field>
          <Field label="Floors"><input type="number" min="1" max="20" required value={f.floors} onChange={set("floors")} /></Field>
        </div>
        <div className="two">
          <Field label="Finish quality"><select value={f.quality} onChange={set("quality")}>{["Economy", "Standard", "Premium"].map((x) => <option key={x}>{x}</option>)}</select></Field>
          <Field label="Currency"><select value={f.currency} onChange={set("currency")}><option>INR</option><option>USD</option></select></Field>
        </div>
        <Field label="Requirements (optional)"><textarea rows={3} value={f.description} onChange={set("description")} placeholder="3 bedrooms, parking, solar roof…" /></Field>
        <button className="primary" disabled={st.loading}>Create plan</button>
      </form>

      <div>
        <Result state={st} />
        {!st.loading && !st.error && !d && <div className="result empty">Your plan appears here.</div>}
        {d && (
          <div className="result">
            <h2>Estimated total {money(d.cost_summary.total, d.cost_summary.currency)}</h2>
            <p>{d.summary}</p>
            <Block title="Cost breakdown">
              <table><tbody>
                {["materials", "labour", "contingency"].map((k) => <tr key={k}><td>{k[0].toUpperCase() + k.slice(1)}</td><td className="num">{money(d.cost_summary[k], d.cost_summary.currency)}</td></tr>)}
                <tr className="sum"><td>Total</td><td className="num">{money(d.cost_summary.total, d.cost_summary.currency)}</td></tr>
              </tbody></table>
            </Block>
            <Block title="Materials">
              <div className="scroll"><table>
                <thead><tr><th>Item</th><th className="num">Qty</th><th className="num">Unit cost</th><th className="num">Total</th></tr></thead>
                <tbody>{d.materials.map((m, i) => <tr key={i}><td>{m.name}</td><td className="num">{m.quantity} {m.unit}</td><td className="num">{money(m.unit_cost, d.cost_summary.currency)}</td><td className="num">{money(m.total_cost, d.cost_summary.currency)}</td></tr>)}</tbody>
              </table></div>
            </Block>
            <Block title={`Schedule · ${d.total_duration_days} days`}>
              {d.schedule.map((t, i) => (
                <div className="gantt" key={i} title={t.depends_on?.length ? `After: ${t.depends_on.join(", ")}` : "Can start first"}>
                  <span>{t.task}</span>
                  <div className="track"><i style={{ left: `${((t.start_day - 1) / total) * 100}%`, width: `${Math.max((t.duration_days / total) * 100, 2)}%` }} /></div>
                  <small>{t.duration_days}d</small>
                </div>))}
            </Block>
            <Block title="Architectural visualization">
              <p>{d.visualization.description}</p>
              <p className="muted">{d.visualization.floors} floor(s) · {d.visualization.elevation_notes}</p>
              <div className="chips">{d.visualization.key_spaces.map((s) => <span key={s}>{s}</span>)}</div>
            </Block>
            <Block title="Risks"><List items={d.risks} /></Block>
          </div>
        )}
      </div>
    </div>
  );
}
