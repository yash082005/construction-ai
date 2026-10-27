# AI-Powered Multimodal Construction Intelligence Platform

React (Vite) frontend + FastAPI backend + Google Gemini multimodal LLM, with strict JSON contracts.

## Features
| Module | Endpoint | Input |
|---|---|---|
| Site safety & PPE | `POST /api/safety` | photos + notes |
| Crack detection | `POST /api/cracks` | photos + element + notes |
| Real estate valuation | `POST /api/valuation` | property details |
| Project planning (materials, cost, schedule, visualization) | `POST /api/plan` | project details |
| Daily site assistant | `POST /api/daily` | stage, crew |
| Weather-aware advisory (live Open-Meteo data) | `POST /api/weather` | city, activity |
| Construction knowledge assistant | `POST /api/knowledge` | question |

## Architecture
```
React UI ──/api──▶ FastAPI ──▶ Gemini (text + images)
                     │             │
                     │      raw JSON reply
                     ▼             ▼
              Pydantic schemas (schemas.py) validate every reply, retry once,
              else return {"error","detail"} — the UI never sees a bad shape.
```

## Setup
**Backend** (Python 3.9+)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add GEMINI_API_KEY (empty = demo mode with sample data)
uvicorn main:app --reload --port 8000
```
**Frontend** (Node 18+)
```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173 (proxies /api to :8000)
```
Interactive API docs: http://localhost:8000/docs

## Testing
```bash
cd backend && pytest -q                  # functional + edge cases (runs in mock mode)
cd frontend && npm run build             # frontend build check
```
Edge cases covered: no image, empty file, wrong file type, oversize image, zero/negative area, too-short question,
invalid AI JSON (retry then clean error), backend offline (UI message), blurry/unrelated images (lower confidence + `image_quality_note`).

## Deployment notes
- Set `ALLOWED_ORIGINS` to your frontend URL; keep the API key only in backend env vars.
- `npm run build` outputs `frontend/dist`; serve it with any static host and proxy `/api` to the backend.

## Known limitations
- Cost/valuation figures are AI estimates, not certified quotes or valuations.
- Crack width and hazard detection from photos are approximate; critical findings need an on-site engineer.
- Weather uses Open-Meteo current conditions only (no forecast window).
- No authentication or database in this version.
