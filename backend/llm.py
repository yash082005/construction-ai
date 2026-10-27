"""Multimodal LLM layer (Google Gemini via REST).
Falls back to MOCK mode when GEMINI_API_KEY is not set.
"""

import base64
import json
import os
import re
from typing import List, Optional, Tuple, Type, TypeVar

import httpx
from pydantic import BaseModel, ValidationError


T = TypeVar("T", bound=BaseModel)

SYSTEM = (
    "You are a senior construction engineer, safety officer and real-estate analyst. "
    "Respond with ONE JSON object only, matching the provided JSON schema exactly. "
    "No markdown, no commentary. If an image is blurry, partial or unrelated, "
    "still return valid JSON, lower the confidence, and explain in image_quality_note. "
    "Never invent precise measurements you cannot see; use ranges."
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
        match = re.search(r"\{.*\}", text, flags=re.S)

        if not match:
            raise

        return json.loads(match.group(0))


async def generate(
    prompt: str,
    model: Type[T],
    mock: dict,
    images: Optional[List[Tuple[bytes, str]]] = None,
) -> T:

    # Return mock data when no Gemini API key is configured.
    if mock_mode():
        return model.model_validate(mock)

    key = os.environ["GEMINI_API_KEY"]
    name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    schema = json.dumps(model.model_json_schema())

    parts = [
        {
            "text": (
                f"{prompt}\n\n"
                f"JSON schema to follow:\n{schema}"
            )
        }
    ]

    # Add uploaded construction images to the request.
    for data, mime in images or []:
        parts.append(
            {
                "inline_data": {
                    "mime_type": mime,
                    "data": base64.b64encode(data).decode("utf-8"),
                }
            }
        )

    body = {
        "system_instruction": {
            "parts": [{"text": SYSTEM}]
        },
        "contents": [
            {
                "role": "user",
                "parts": parts,
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
        },
    }

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{name}:generateContent"
    )

    last_err = "AI returned an invalid response."

    try:
        timeout = httpx.Timeout(
            connect=20.0,
            read=180.0,
            write=30.0,
            pool=20.0,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            last_err = "Gemini request failed."

            for attempt in range(3):
                try:
                    response = await client.post(
                        url,
                        params={"key": key},
                        json=body,
                    )

                    if response.status_code in (429, 500, 502, 503, 504):
                        if attempt < 2:
                            await asyncio.sleep(2 ** (attempt + 1))
                            continue

                    response.raise_for_status()
                    response_data = response.json()

                    candidates = response_data.get("candidates", [])
                    if not candidates:
                        raise LLMError(
                            "Gemini returned no candidates. "
                            f"Response: {str(response_data)[:1000]}"
                        )

                    parts = (
                        candidates[0]
                        .get("content", {})
                        .get("parts", [])
                    )

                    text = "".join(
                        part.get("text", "")
                        for part in parts
                        if isinstance(part, dict)
                    )

                    if not text.strip():
                        raise LLMError("Gemini returned an empty response.")

                    result = _extract_json(text)
                    return model.model_validate(result)

                except httpx.TimeoutException as exc:
                    last_err = (
                        f"Gemini request timed out: {type(exc).__name__}"
                    )
                    if attempt < 2:
                        await asyncio.sleep(2 ** (attempt + 1))
                        continue
                    raise LLMError(last_err) from exc

                except httpx.HTTPStatusError as exc:
                    status = exc.response.status_code
                    details = exc.response.text[:1000]

                    if status in (429, 500, 502, 503, 504) and attempt < 2:
                        last_err = f"Gemini API returned HTTP {status}"
                        await asyncio.sleep(2 ** (attempt + 1))
                        continue

                    raise LLMError(
                        f"Gemini API error {status}: {details}"
                    ) from exc

                except httpx.HTTPError as exc:
                    last_err = (
                        f"Gemini connection error: {type(exc).__name__}"
                    )
                    if attempt < 2:
                        await asyncio.sleep(2 ** (attempt + 1))
                        continue
                    raise LLMError(last_err) from exc

                except LLMError:
                    raise

               

       

                   

                 
