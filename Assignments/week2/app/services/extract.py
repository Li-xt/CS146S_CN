from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

# Load Assignments/.env (same layout as week1 scripts).
load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

BASE_URL = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
MODEL_NAME = os.getenv("OPENAI_MODEL", "qwen-plus")
OPENAI_API_KEY = (
    os.getenv("OPENAI_API_ALI_KEY")
    or os.getenv("OPENAI_API_KEY")
    or os.getenv("OPENAI_API_KIMI_KEY")
)

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)

_EXTRACTION_SYSTEM = """You extract actionable todo items from meeting notes or free-form text.
Return ONLY a JSON array of strings. Each string is one concrete, imperative action item.
No markdown fences, no commentary. If there are no clear actions, return [].
Example: ["Book the room for Tuesday", "Send slides to the team"]"""


def _parse_json_string_array(raw: str) -> List[str]:
    """Parse model output into a list of non-empty strings (week1-style JSON handling)."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("Model output must be a JSON array")
    out: List[str] = []
    for x in data:
        if isinstance(x, str) and x.strip():
            out.append(x.strip())
    return out


def extract_action_items_llm(text: str) -> List[str]:
    """Extract action items using OpenAI-compatible chat API (same client setup as week1)."""
    if not text.strip():
        return []
    if not OPENAI_API_KEY:
        raise ValueError(
            "Missing API key. Set OPENAI_API_ALI_KEY (or OPENAI_API_KEY / OPENAI_API_KIMI_KEY)."
        )
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=BASE_URL)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": _EXTRACTION_SYSTEM},
            {"role": "user", "content": text.strip()},
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content or "[]"
    return _parse_json_string_array(content)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
