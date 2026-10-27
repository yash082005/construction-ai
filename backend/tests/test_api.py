import io, os, sys
os.environ.pop("GEMINI_API_KEY", None)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from main import app

c = TestClient(app)
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 50


def test_health():
    assert c.get("/api/health").json()["mode"] == "mock"

def test_safety_ok():
    r = c.post("/api/safety", files=[("images", ("a.png", io.BytesIO(PNG), "image/png"))])
    assert r.status_code == 200 and r.json()["overall_risk"] in {"Low", "Medium", "High", "Critical"}

def test_safety_no_image():
    r = c.post("/api/safety")
    assert r.status_code == 400 and "error" in r.json()

def test_bad_type():
    r = c.post("/api/cracks", files=[("images", ("a.txt", io.BytesIO(b"x"), "text/plain"))])
    assert r.status_code == 415

def test_empty_image():
    r = c.post("/api/cracks", files=[("images", ("a.png", io.BytesIO(b""), "image/png"))])
    assert r.status_code == 400

def test_plan_and_valuation():
    p = c.post("/api/plan", json={"location": "X", "area_sqft": 1200, "floors": 2}).json()
    assert p["cost_summary"]["total"] > 0 and len(p["schedule"]) > 0
    assert c.post("/api/valuation", json={"location": "X", "area_sqft": 0}).status_code == 422
    assert c.post("/api/valuation", json={"location": "X", "area_sqft": 900}).status_code == 200

def test_knowledge_and_daily():
    assert c.post("/api/knowledge", json={"question": "Min cover for slab?"}).status_code == 200
    assert c.post("/api/knowledge", json={"question": "?"}).status_code == 422
    assert c.post("/api/daily", json={"stage": "Foundation"}).status_code == 200
