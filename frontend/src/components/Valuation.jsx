import React, { useState } from "react";
import { postJson } from "../api";
import { Block, Confidence, Field, List, Result, money, useRunner } from "./ui";

export default function Valuation() {
  const [f, setF] = useState({ location: "", property_type: "Residential house", area_sqft: 1000, age_years: 5, bedrooms: 2, condition: "Average", amenities: "", currency: "INR" });
  const [st, run] = useRunner();
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const d = st.data;
  return (
    <div className="split">
      <form className="panel" onSubmit={(e) => { e.preventDefault(); run(() => postJson("/valuation", { ...f, area_sqft: +f.area_sqft, age_years: +f.age_years, bedrooms: +f.bedrooms })); }}>
        <h2>Real estate valuation</h2>
        <p className="muted">An indicative market range. Not a certified valuation.</p>
        <Field label="Location (area, city)"><input required value={f.location} onChange={set("location")} placeholder="e.g. Baner, Pune" /></Field>
        <Field label="Property type"><select value={f.property_type} onChange={set("property_type")}>{["Residential house", "Apartment", "Plot with structure", "Commercial shop", "Office"].map((x) => <option key={x}>{x}</option>)}</select></Field>
        <div className="two">
          <Field label="Area (sq ft)"><input type="number" min="1" required value={f.area_sqft} onChange={set("area_sqft")} /></Field>
          <Field label="Age (years)"><input type="number" min="0" value={f.age_years} onChange={set("age_years")} /></Field>
        </div>
        <div className="two">
          <Field label="Bedrooms"><input type="number" min="0" value={f.bedrooms} onChange={set("bedrooms")} /></Field>
          <Field label="Condition"><select value={f.condition} onChange={set("condition")}>{["Poor", "Average", "Good", "Excellent"].map((x) => <option key={x}>{x}</option>)}</select></Field>
        </div>
        <Field label="Amenities (optional)"><input value={f.amenities} onChange={set("amenities")} placeholder="Parking, lift, garden" /></Field>
        <Field label="Currency"><select value={f.currency} onChange={set("currency")}><option>INR</option><option>USD</option></select></Field>
        <button className="primary" disabled={st.loading}>Estimate value</button>
      </form>
      <div>
        <Result state={st} />
        {!st.loading && !st.error && !d && <div className="result empty">Your estimate appears here.</div>}
        {d && (
          <div className="result">
            <h2>{money(d.estimated_value.low, d.estimated_value.currency)} – {money(d.estimated_value.high, d.estimated_value.currency)}</h2>
            <p>About {money(d.price_per_sqft, d.estimated_value.currency)} per sq ft. {d.summary}</p>
            <Confidence value={d.confidence} />
            <Block title="What moves the price">
              {d.factors.map((x, i) => <div className="row" key={i}><div className="head"><strong>{x.factor}</strong><span className={`impact ${x.impact}`}>{x.impact}</span></div><p>{x.note}</p></div>)}
            </Block>
            <Block title="Assumptions"><List items={d.assumptions} /></Block>
          </div>
        )}
      </div>
    </div>
  );
}
