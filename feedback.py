"""
feedback.py — Feedback storage and retrieval for LifeXP.
Saves to a local JSON file so all feedback persists across sessions.
"""

import json
import os
from datetime import datetime

FEEDBACK_FILE = "feedback_data.json"


def load_feedback() -> list:
    """Load all feedback entries from disk."""
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_feedback(rating: int, comment: str, name: str, anonymous: bool, goal: str = "") -> bool:
    """Save a new feedback entry. Returns True on success."""
    try:
        all_feedback = load_feedback()
        entry = {
            "id": len(all_feedback) + 1,
            "rating": rating,
            "comment": comment.strip(),
            "name": "Anonymous" if anonymous else name.strip() or "Anonymous",
            "anonymous": anonymous,
            "goal": goal,
            "timestamp": datetime.now().strftime("%b %d, %Y"),
        }
        all_feedback.append(entry)
        with open(FEEDBACK_FILE, "w") as f:
            json.dump(all_feedback, f, indent=2)
        return True
    except Exception:
        return False


def get_stats() -> dict:
    """Return avg rating, total count, and per-star breakdown."""
    all_feedback = load_feedback()
    if not all_feedback:
        return {"avg": 0.0, "total": 0, "breakdown": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}}
    total = len(all_feedback)
    avg = sum(f["rating"] for f in all_feedback) / total
    breakdown = {i: sum(1 for f in all_feedback if f["rating"] == i) for i in range(1, 6)}
    return {"avg": round(avg, 1), "total": total, "breakdown": breakdown}
