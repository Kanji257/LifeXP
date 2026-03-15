"""
quests.py — Quest display and XP tracking logic for LifeXP.
"""

from utils import xp_to_level

XP_PER_LEVEL = 200

DIFFICULTY_COLORS = {
    "Easy":   "🟢",
    "Medium": "🟡",
    "Hard":   "🔴",
}


def get_difficulty_badge(difficulty: str) -> str:
    """Return colored badge for quest difficulty."""
    return DIFFICULTY_COLORS.get(difficulty, "⚪")


def format_quest_display(quest: dict) -> str:
    """
    Format a single quest for display.

    Args:
        quest: Dict with keys task, difficulty, xp.

    Returns:
        Formatted string for the quest.
    """
    badge = get_difficulty_badge(quest.get("difficulty", "Easy"))
    task = quest.get("task", "Complete this quest")
    diff = quest.get("difficulty", "Easy")
    xp = quest.get("xp", 40)
    return f"{badge} **{task}** — *{diff}* · `+{xp} XP`"


def calculate_skill_xp(quests: list[dict]) -> int:
    """
    Sum total XP from a list of quests (simulating partial completion).

    Args:
        quests: List of quest dicts.

    Returns:
        Total XP integer.
    """
    # For demo: simulate that the first quest is already completed
    if not quests:
        return 0
    return quests[0].get("xp", 40)


def get_level_info(xp: int) -> dict:
    """
    Return level info dict for display.

    Args:
        xp: Total accumulated XP.

    Returns:
        Dict with level, current_xp, xp_per_level, progress_pct.
    """
    level, current_xp = xp_to_level(xp, XP_PER_LEVEL)
    return {
        "level": level,
        "current_xp": current_xp,
        "xp_per_level": XP_PER_LEVEL,
        "progress_pct": int((current_xp / XP_PER_LEVEL) * 100),
    }
