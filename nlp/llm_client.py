from __future__ import annotations
import os
from typing import Optional
from core.models import ParsedEntities, TestPlan
from core.generator import generate_plan_offline

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # library not installed; we'll fall back

from nlp.prompting import SYSTEM_PROMPT, build_user_prompt


def generate_plan_llm(entities: ParsedEntities) -> TestPlan:
    """Attempt an LLM-enhanced plan; fall back to offline if no API key or client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if OpenAI is None or not api_key:
        return generate_plan_offline(entities)

    client = OpenAI(api_key=api_key)
    user_prompt = build_user_prompt(entities)

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        md = resp.choices[0].message.content or ""
        # We return as a TestPlan with only Markdown notes (keep pipeline uniform)
        return TestPlan(title=f"Bring-Up & Test Plan — {entities.title}", steps=[], notes=md)
    except Exception:
        # Any error -> offline deterministic plan
        return generate_plan_offline(entities)
