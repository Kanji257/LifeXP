"""
utils.py — Shared utility functions for LifeXP
"""

import json
import re


def parse_json_response(text: str) -> dict:
    """
    Safely parse a JSON response from the LLM.
    Strips markdown code fences if present.

    Args:
        text: Raw LLM response text.

    Returns:
        Parsed dict, or empty dict on failure.
    """
    # Strip markdown fences
    cleaned = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object within the text
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return {}
        return {}


def xp_to_level(xp: int, xp_per_level: int = 200) -> tuple[int, int]:
    """
    Convert raw XP to (level, xp_in_current_level).

    Args:
        xp: Total XP accumulated.
        xp_per_level: XP required per level.

    Returns:
        Tuple of (level, current_xp_in_level).
    """
    level = (xp // xp_per_level) + 1
    current = xp % xp_per_level
    return level, current
