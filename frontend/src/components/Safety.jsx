import React, { useState } from "react";
import { postForm } from "../api";
import { Badge, Block, Confidence, Field, ImagePicker, List, Result, useRunner } from "./ui";

export default function Safety({ mode = "safety" }) {
  const crack = mode === "cracks";
  const [files, setFiles] = useState([]);
  const [notes, setNotes] = useState("");
  const [element, setElement] = useState("wall");
  const [st, run] = useRunner();
  const d = st.data;

  return (
    <div className="split">
      <form className="panel" onSubmit={(e) => { e.preventDefault(); run(() => postForm(crack ? "/cracks" : "/safety", files, crack ? { notes, element } : { notes })); }}>
        <h2>{crack ? "Crack detection" : "Site safety check"}</h2>
        <p className="muted">{crack ? "Upload a close, well-lit photo of the cracked surface." : "Upload site photos to check hazards and protective equipment."}</p>
        <ImagePicker files={files} setFiles={setFiles} />
        {crack && <Field label="Structural element">
          <select value={element} onChange={(e) => setElement(e.target.value)}>
            {["wall", "column", "beam", "slab / ceiling", "foundation / plinth", "floor"].map((x) => <option key={x}>{x}</option>)}
          </select></Field>}
        <Field label="Notes (optional)"><textarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder={crack ? "Age of building, when you first noticed it" : "Work being done, number of workers"} /></Field>
        <button className="primary" disabled={st.loading || !files.length}>{crack ? "Analyse crack" : "Run safety check"}</button>
        {!files.length && <p className="hint">Add at least one photo to continue.</p>}
      </form>

      <div>
        <Result state={st} />
        {!st.loading && !st.error && !d && <div className="result empty">Results appear here.</div>}
        {d && !crack && (
          <div className="result">
            <div className="head"><h2>Overall risk</h2><Badge level={d.overall_risk} /></div>
            <p>{d.summary}</p>
            <Confidence value={d.confidence} />
            {d.image_quality_note && <p className="note">Image note: {d.image_quality_note}</p>}
            <Block title="Hazards">
              {d.hazards.length === 0 ? <p className="muted">No hazards identified.</p> : d.hazards.map((h, i) => (
                <div className="row" key={i}>
                  <div className="head"><strong>{h.type}</strong><Badge level={h.severity} /></div>
                  <p>{h.description}{h.location_hint && <em> — {h.location_hint}</em>}</p>
                  <p className="fix">Fix: {h.corrective_action}</p>
                </div>))}
            </Block>
            <Block title="Protective equipment">
              <table><tbody>{d.ppe.map((p, i) => <tr key={i}><td>{p.item}</td><td><span className={`ppe ${p.status}`}>{p.status}</span></td><td className="muted">{p.note}</td></tr>)}</tbody></table>
            </Block>
            <Block title="Do now"><List items={d.immediate_actions} /></Block>
          </div>
        )}
        {d && crack && (
          <div className="result">
            <div className="head"><h2>{d.crack_detected ? `${d.crack_type} crack` : "No crack found"}</h2><Badge level={d.severity} /></div>
            <p>{d.summary}</p>
            <Confidence value={d.confidence} />
            {d.urgent_inspection && <p className="alert">Urgent: have a structural engineer inspect this before further loading.</p>}
            {d.image_quality_note && <p className="note">Image note: {d.image_quality_note}</p>}
            <Block title="Estimated width"><p>{d.estimated_width_mm}</p></Block>
            <Block title="Probable causes"><List items={d.probable_causes} /></Block>
            <Block title="Recommended actions"><List items={d.recommended_actions} /></Block>
          </div>
        )}
      </div>
    </div>
  );
}
