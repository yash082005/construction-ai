"""Multimodal LLM layer (Google Gemini via REST). Returns validated Pydantic models.
Falls back to MOCK mode when GEMINI_API_KEY is not set."""
import base64, json, os, re
from typing import List, Optional, Tuple, Type, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)
SYSTEM = (
    "You are a senior construction engineer, safety officer and real-estate analyst. "
    "Respond with ONE JSON object only, matching the provided JSON schema exactly. "
    "No markdown, no commentary. If an image is blurry, partial or unrelated, still return valid JSON, "
    "lower the confidence, and explain in image_quality_note. Never invent precise measurements you cannot see; use ranges."
)


class LLMError(Exception):
    pass


def mock_mode() -> bool:
    return not os.getenv("GEMINI_API_KEY")


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, flags=re.S)
        if not m:
            raise
        return json.loads(m.group(0))


async def generate(prompt: str, model: Type[T], mock: dict,
                   images: Optional[List[Tuple[bytes, str]]] = None) -> T:
    if mock_mode():
        return model.model_validate(mock)

    key, name = os.environ["GEMINI_API_KEY"], os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    schema = json.dumps(model.model_json_schema())
    parts = [{"text": f"{prompt}\n\nJSON schema to follow:\n{schema}"}]
    for data, mime in images or []:
        parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(data).decode()}})
    body = {
        "system_instruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{name}:generateContent"
    last_err = ""
        async with httpx.AsyncClient(timeout=90) as client:
            for attempt in range(2):  # one retry if JSON fails validation
                try:
                    r = await client.post(url, params={"key": key}, json=body)
                    r.raise_for_status()
                    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return model.model_validate(_extract_json(text))

                except (ValidationError, json.JSONDecodeError, KeyError, IndexError) as e:
                    last_err = f"AI returned an invalid structure: {str(e)[:200]}"
                    body["contents"][0]["parts"][0]["text"] += (
                        "\n\nYour previous reply was invalid. Return valid JSON matching the schema."
                    )

                except httpx.HTTPStatusError as e:
                    raise LLMError(
                        f"AI service error {e.response.status_code}: "
                        f"{e.response.text[:1000]}"
                    ) from e

        except httpx.HTTPError as e:
            raise LLMError(
                f"Could not reach the AI service: {type(e).__name__}: {str(e)}"
            ) from e

    raise LLMError(last_err)
```
