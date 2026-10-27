"""Schema-valid sample outputs used when no API key is configured."""

def safety():
    return {"overall_risk": "High", "summary": "Sample result (mock mode): workers at height without visible fall protection; loose materials near edge.",
            "hazards": [{"type": "Fall from height", "description": "Open edge on upper level with no guardrail visible.", "severity": "High", "location_hint": "Upper floor edge", "corrective_action": "Install guardrails or use a certified fall-arrest system before work resumes."},
                        {"type": "Housekeeping", "description": "Loose bricks and debris on walkway.", "severity": "Medium", "location_hint": "Ground walkway", "corrective_action": "Clear and stack materials; mark walkways."}],
            "ppe": [{"item": "Hard hat", "status": "worn", "note": ""}, {"item": "Safety harness", "status": "missing", "note": "Not visible"}, {"item": "High-visibility vest", "status": "unclear", "note": "Partly hidden"}],
            "immediate_actions": ["Stop work at open edge", "Issue harnesses", "Clear walkway debris"], "image_quality_note": "", "confidence": 0.7}

def crack():
    return {"crack_detected": True, "crack_type": "diagonal", "severity": "Medium", "estimated_width_mm": "1-3 mm (estimate)",
            "probable_causes": ["Differential settlement", "Thermal movement", "Shrinkage during curing"],
            "recommended_actions": ["Mark crack ends with dated pencil lines and monitor for 2-4 weeks", "Install a tell-tale gauge", "Have a structural engineer inspect if width grows"],
            "urgent_inspection": False, "summary": "Sample result (mock mode): diagonal crack of moderate severity near an opening.", "image_quality_note": "", "confidence": 0.65}

def valuation(currency="INR"):
    return {"estimated_value": {"low": 5200000, "high": 6100000, "currency": currency}, "price_per_sqft": 4700,
            "factors": [{"factor": "Location", "impact": "positive", "note": "Good access to roads and services."},
                        {"factor": "Building age", "impact": "negative", "note": "Older construction lowers value."},
                        {"factor": "Condition", "impact": "neutral", "note": "Average finishing."}],
            "assumptions": ["Mock mode: figures are illustrative only", "Freehold title assumed"],
            "summary": "Sample valuation range based on the supplied inputs.", "confidence": 0.5}

def plan(currency="INR", floors=2):
    mats = [("Cement (OPC 53)", 900, "bags", 400), ("Steel (TMT bars)", 6.5, "tonnes", 62000), ("Bricks", 28000, "pcs", 9), ("River sand", 40, "tonnes", 1600)]
    m = [{"name": n, "quantity": q, "unit": u, "unit_cost": c, "total_cost": round(q * c, 2)} for n, q, u, c in mats]
    mt = sum(x["total_cost"] for x in m)
    lab, cont = round(mt * 0.6), round(mt * 0.08)
    return {"summary": "Sample plan (mock mode).", "materials": m,
            "cost_summary": {"materials": mt, "labour": lab, "contingency": cont, "total": mt + lab + cont, "currency": currency},
            "schedule": [{"task": "Site prep & excavation", "start_day": 1, "duration_days": 10, "depends_on": []},
                         {"task": "Foundation", "start_day": 11, "duration_days": 20, "depends_on": ["Site prep & excavation"]},
                         {"task": "Structure & slabs", "start_day": 31, "duration_days": 60, "depends_on": ["Foundation"]},
                         {"task": "Masonry & services", "start_day": 91, "duration_days": 45, "depends_on": ["Structure & slabs"]},
                         {"task": "Finishing", "start_day": 136, "duration_days": 50, "depends_on": ["Masonry & services"]}],
            "total_duration_days": 185,
            "visualization": {"description": "Compact rectangular plan with central staircase and front verandah.", "floors": floors, "key_spaces": ["Living room", "Kitchen", "3 bedrooms", "Staircase"], "elevation_notes": "Simple flat-roof elevation with a projecting balcony."},
            "risks": ["Monsoon delays to foundation work", "Steel price volatility"]}

def daily():
    return {"priorities": ["Complete column shuttering on grid B", "Receive cement delivery"], "checklist": ["Toolbox talk at 8:00", "Check scaffold tags", "Verify concrete cube samples"], "risks": ["Heavy vehicle movement near excavation"], "notes": "Sample result (mock mode)."}

def weather(w):
    return {"weather": w, "work_suitability": "Caution", "summary": "Sample advisory (mock mode).",
            "favourable_activities": ["Interior finishing", "Steel fixing"], "activities_to_avoid": ["Concrete pouring if rain starts", "Crane lifts in high wind"],
            "recommendations": ["Cover fresh concrete", "Secure loose sheets and scaffolding"]}

def knowledge(q):
    return {"answer": f"Sample answer (mock mode) to: {q}", "key_points": ["Follow the relevant IS/IBC code", "Verify with a licensed engineer"],
            "standards_or_references": ["IS 456:2000 (RCC)", "IS 875 (loads)"], "follow_up_questions": ["What is the soil bearing capacity at your site?"]}
