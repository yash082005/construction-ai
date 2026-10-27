import os
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()
import llm, mocks  # noqa: E402
from schemas import *  # noqa: E402,F401,F403

app = FastAPI(title="Multimodal Construction Intelligence Platform", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
                   allow_methods=["*"], allow_headers=["*"])

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = int(float(os.getenv("MAX_IMAGE_MB", "8")) * 1024 * 1024)


class APIError(Exception):
    def __init__(self, status: int, error: str, detail: str = ""):
        self.status, self.error, self.detail = status, error, detail


@app.exception_handler(APIError)
async def api_error(_, e: APIError):
    return JSONResponse(status_code=e.status, content=ErrorBody(error=e.error, detail=e.detail).model_dump())


@app.exception_handler(llm.LLMError)
async def llm_error(_, e: llm.LLMError):
    return JSONResponse(status_code=502, content=ErrorBody(error="AI service problem", detail=str(e)).model_dump())


async def read_images(files: Optional[List[UploadFile]], required: bool) -> List[tuple]:
    out = []
    for f in files or []:
        if not f.filename:
            continue
        if f.content_type not in ALLOWED_MIME:
            raise APIError(415, "Unsupported image type", f"{f.filename}: use JPG, PNG or WebP.")
        data = await f.read()
        if not data:
            raise APIError(400, "Empty image file", f"{f.filename} has no data.")
        if len(data) > MAX_BYTES:
            raise APIError(413, "Image too large", f"{f.filename} exceeds {MAX_BYTES // 1048576} MB.")
        out.append((data, f.content_type))
    if required and not out:
        raise APIError(400, "No image uploaded", "Attach at least one construction photo.")
    return out


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "mock" if llm.mock_mode() else "live"}


@app.post("/api/safety", response_model=SafetyReport)
async def safety(images: List[UploadFile] = File(default=None), notes: str = Form("")):
    imgs = await read_images(images, required=True)
    prompt = ("Analyse the construction-site photo(s) for hazards and PPE compliance (helmet, vest, harness, gloves, boots, eye protection). "
              f"Rate severity and give corrective actions. Site notes from user: {notes or 'none'}.")
    return await llm.generate(prompt, SafetyReport, mocks.safety(), imgs)


@app.post("/api/cracks", response_model=CrackReport)
async def cracks(images: List[UploadFile] = File(default=None), notes: str = Form(""), element: str = Form("wall")):
    imgs = await read_images(images, required=True)
    prompt = (f"Analyse the photo(s) of a {element} for cracks: type, severity, estimated width range, probable causes and corrective actions. "
              f"If no crack is visible set crack_detected=false and crack_type='none'. User notes: {notes or 'none'}.")
    return await llm.generate(prompt, CrackReport, mocks.crack(), imgs)


class ValuationIn(BaseModel):
    location: str
    property_type: str = "Residential house"
    area_sqft: float
    age_years: float = 0
    bedrooms: int = 0
    condition: str = "Average"
    amenities: str = ""
    currency: str = "INR"


@app.post("/api/valuation", response_model=ValuationReport)
async def valuation(body: ValuationIn):
    if body.area_sqft <= 0:
        raise APIError(422, "Invalid area", "Area must be greater than zero.")
    prompt = ("Estimate the market value range of this property, as a valuer would. Provide price per sqft, factors and assumptions. "
              f"Currency: {body.currency}. Property: {body.model_dump_json()}")
    return await llm.generate(prompt, ValuationReport, mocks.valuation(body.currency))


class PlanIn(BaseModel):
    project_type: str = "Residential house"
    location: str
    area_sqft: float
    floors: int = 1
    quality: str = "Standard"
    description: str = ""
    currency: str = "INR"


@app.post("/api/plan", response_model=PlanReport)
async def plan(body: PlanIn):
    if body.area_sqft <= 0 or body.floors < 1:
        raise APIError(422, "Invalid inputs", "Area and floors must be positive.")
    prompt = ("Create a construction plan: material estimate (quantities, unit costs, totals), cost summary (materials, labour, contingency, total), "
              "task schedule with start_day/duration_days/dependencies, a text architectural visualization, and risks. "
              f"Make totals arithmetically consistent. Currency: {body.currency}. Project: {body.model_dump_json()}")
    return await llm.generate(prompt, PlanReport, mocks.plan(body.currency, body.floors))


class DailyIn(BaseModel):
    site_name: str = "Site"
    stage: str
    crew_size: int = 0
    notes: str = ""


@app.post("/api/daily", response_model=DailyPlan)
async def daily(body: DailyIn):
    prompt = f"Create today's site plan: top priorities, a short checklist and risks. Input: {body.model_dump_json()}"
    return await llm.generate(prompt, DailyPlan, mocks.daily())


class WeatherIn(BaseModel):
    location: str
    activity: str = "general construction"


async def fetch_weather(place: str) -> WeatherSnapshot:
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            g = (await c.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": place, "count": 1})).json()
            if not g.get("results"):
                raise APIError(404, "Location not found", f"No match for '{place}'. Try a nearby city name.")
            r = g["results"][0]
            w = (await c.get("https://api.open-meteo.com/v1/forecast", params={
                "latitude": r["latitude"], "longitude": r["longitude"],
                "current": "temperature_2m,wind_speed_10m,precipitation"})).json()["current"]
            return WeatherSnapshot(location=f'{r["name"]}, {r.get("country", "")}', temperature_c=w["temperature_2m"],
                                   wind_kmh=w["wind_speed_10m"], precipitation_mm=w["precipitation"], description="Live data from Open-Meteo")
    except APIError:
        raise
    except Exception:
        return WeatherSnapshot(location=place, description="Live weather unavailable; advice is general.")


@app.post("/api/weather", response_model=WeatherAdvisory)
async def weather(body: WeatherIn):
    w = await fetch_weather(body.location)
    prompt = (f"Give a construction weather advisory for activity '{body.activity}'. Current weather: {w.model_dump_json()}. "
              "Return the same weather object inside 'weather'.")
    res = await llm.generate(prompt, WeatherAdvisory, mocks.weather(w.model_dump()))
    res.weather = w
    return res


class AskIn(BaseModel):
    question: str


@app.post("/api/knowledge", response_model=KnowledgeAnswer)
async def knowledge(body: AskIn):
    if len(body.question.strip()) < 3:
        raise APIError(422, "Question too short", "Ask a full question.")
    prompt = f"Answer this construction knowledge question clearly for a practising site engineer, citing relevant codes (IS, NBC, IBC) where applicable: {body.question}"
    return await llm.generate(prompt, KnowledgeAnswer, mocks.knowledge(body.question))
