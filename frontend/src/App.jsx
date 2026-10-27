import React, { useEffect, useState } from "react";
import { getHealth } from "./api";
import Safety from "./components/Safety";
import Planner from "./components/Planner";
import Valuation from "./components/Valuation";
import Assistant from "./components/Assistant";

const MODULES = [
  { id: "safety", label: "Site safety", view: <Safety mode="safety" /> },
  { id: "cracks", label: "Crack detection", view: <Safety mode="cracks" /> },
  { id: "plan", label: "Project planning", view: <Planner /> },
  { id: "value", label: "Valuation", view: <Valuation /> },
  { id: "assist", label: "Site assistant", view: <Assistant /> },
];

export default function App() {
  const [active, setActive] = useState("safety");
  const [mode, setMode] = useState("");
  useEffect(() => { getHealth().then((r) => setMode(r.ok ? r.data.mode : "offline")); }, []);
  const current = MODULES.find((m) => m.id === active);

  return (
    <div className="app">
      <aside>
        <div className="brand"><b>Site Intelligence</b><span>Multimodal construction platform</span></div>
        <nav>{MODULES.map((m) => <button key={m.id} className={active === m.id ? "on" : ""} onClick={() => setActive(m.id)}>{m.label}</button>)}</nav>
        {mode && <div className={`status ${mode}`}>{mode === "live" ? "AI connected" : mode === "mock" ? "Demo mode: sample data" : "Backend offline"}</div>}
      </aside>
      <main key={current.id}>{current.view}</main>
    </div>
  );
}
