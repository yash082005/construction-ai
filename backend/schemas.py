"""Strict JSON contracts. Every AI response is validated against one of these
before it reaches the React frontend, so the UI never renders unexpected shapes."""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

Risk = Literal["Low", "Medium", "High", "Critical"]


# ---------- Safety ----------
class Hazard(BaseModel):
    type: str
    description: str
    severity: Risk
    location_hint: str = ""
    corrective_action: str


class PPEItem(BaseModel):
    item: str
    status: Literal["worn", "missing", "unclear"]
    note: str = ""


class SafetyReport(BaseModel):
    overall_risk: Risk
    summary: str
    hazards: List[Hazard]
    ppe: List[PPEItem]
    immediate_actions: List[str]
    image_quality_note: str = ""
    confidence: float = Field(ge=0, le=1)


# ---------- Cracks ----------
class CrackReport(BaseModel):
    crack_detected: bool
    crack_type: Literal["hairline", "shrinkage", "settlement", "structural", "thermal", "diagonal", "vertical", "horizontal", "map/pattern", "none", "unclear"]
    severity: Risk
    estimated_width_mm: str
    probable_causes: List[str]
    recommended_actions: List[str]
    urgent_inspection: bool
    summary: str
    image_quality_note: str = ""
    confidence: float = Field(ge=0, le=1)


# ---------- Valuation ----------
class ValueRange(BaseModel):
    low: float
    high: float
    currency: str


class Factor(BaseModel):
    factor: str
    impact: Literal["positive", "negative", "neutral"]
    note: str


class ValuationReport(BaseModel):
    estimated_value: ValueRange
    price_per_sqft: float
    factors: List[Factor]
    assumptions: List[str]
    summary: str
    confidence: float = Field(ge=0, le=1)


# ---------- Planning ----------
class Material(BaseModel):
    name: str
    quantity: float
    unit: str
    unit_cost: float
    total_cost: float


class CostSummary(BaseModel):
    materials: float
    labour: float
    contingency: float
    total: float
    currency: str


class Task(BaseModel):
    task: str
    start_day: int
    duration_days: int
    depends_on: List[str] = []


class Visualization(BaseModel):
    description: str
    floors: int
    key_spaces: List[str]
    elevation_notes: str


class PlanReport(BaseModel):
    summary: str
    materials: List[Material]
    cost_summary: CostSummary
    schedule: List[Task]
    total_duration_days: int
    visualization: Visualization
    risks: List[str]


# ---------- Daily assistant / weather / knowledge ----------
class DailyPlan(BaseModel):
    priorities: List[str]
    checklist: List[str]
    risks: List[str]
    notes: str = ""


class WeatherSnapshot(BaseModel):
    location: str
    temperature_c: Optional[float] = None
    wind_kmh: Optional[float] = None
    precipitation_mm: Optional[float] = None
    description: str = ""


class WeatherAdvisory(BaseModel):
    weather: WeatherSnapshot
    work_suitability: Literal["Good", "Caution", "Not recommended"]
    summary: str
    favourable_activities: List[str]
    activities_to_avoid: List[str]
    recommendations: List[str]


class KnowledgeAnswer(BaseModel):
    answer: str
    key_points: List[str]
    standards_or_references: List[str]
    follow_up_questions: List[str]


class ErrorBody(BaseModel):
    error: str
    detail: str = ""
