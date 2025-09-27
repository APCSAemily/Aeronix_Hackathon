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
    """Generate base plan and enhance with LLM commentary."""
    base = generate_plan_offline(entities)  # keep deterministic steps
    api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        from openai import OpenAI
    except Exception:
        return base
    
    if not api_key:
        return base

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(entities)
                 + "\n\nImprove clarity and add short safety/DFT notes. Keep it concise."}
            ],
            temperature=temperature,
        )
        md = resp.choices[0].message.content or ""
        base.notes = (base.notes or "") + "\n\nLLM Enhancements:\n" + md
        return base
    except Exception:
        # Any error -> return base plan
        return base
