"""Google Gemini AI Provider with structured outputs and graceful fallback."""

import json
from typing import List, Optional
import httpx

from .base import AIProvider, AIStructuredOutput, AIFinding, AITestCase
from .mock_provider import MockAIProvider
from .prompt_templates import SYSTEM_PROMPT, JSON_SCHEMA_INSTRUCTION
from ..config import settings
from ..logging import logger
from ..schemas.findings import FindingSchema, SeverityEnum, CategoryEnum
from ..security.sanitization import build_safe_prompt_envelope


class GeminiAIProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self._fallback_provider = MockAIProvider()

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def health_check(self) -> bool:
        return bool(self.api_key)

    async def analyze_code(
        self,
        code: str,
        language: str,
        static_findings: List[FindingSchema],
    ) -> AIStructuredOutput:
        if not self.api_key:
            logger.info("Gemini API key not configured; falling back to deterministic mock provider.")
            return await self._fallback_provider.analyze_code(code, language, static_findings)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        safe_envelope = build_safe_prompt_envelope(code, language)
        user_prompt = f"{JSON_SCHEMA_INSTRUCTION}\n\nAnalyze this untrusted code snippet:\n{safe_envelope}"

        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "max_output_tokens": 4096,
                "temperature": 0.2,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code != 200:
                    logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}. Falling back to mock provider.")
                    return await self._fallback_provider.analyze_code(code, language, static_findings)

                data = resp.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(raw_text)

                findings = [
                    AIFinding(
                        severity=SeverityEnum(f.get("severity", "info").lower()),
                        category=CategoryEnum(f.get("category", "maintainability").lower()),
                        title=f.get("title", "Observation"),
                        explanation=f.get("explanation", ""),
                        suggestion=f.get("suggestion"),
                        line_start=max(1, int(f.get("line_start", 1))),
                        line_end=max(1, int(f.get("line_end", 1))),
                        confidence=float(f.get("confidence", 0.85)),
                    )
                    for f in parsed.get("findings", [])
                ]

                tests = [
                    AITestCase(
                        test_framework=t.get("test_framework", "generic"),
                        test_code=t.get("test_code", ""),
                        explanation=t.get("explanation"),
                    )
                    for t in parsed.get("suggested_tests", [])
                ]

                return AIStructuredOutput(
                    summary=parsed.get("summary", "Analysis completed."),
                    findings=findings,
                    suggested_refactor=parsed.get("suggested_refactor"),
                    suggested_tests=tests,
                    limitations=parsed.get(
                        "limitations",
                        ["AI suggestions are advisory recommendations and must be verified by developers."],
                    ),
                )
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}. Falling back to mock provider.")
            return await self._fallback_provider.analyze_code(code, language, static_findings)
