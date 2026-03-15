"""
icons.py — Skill icon mapping for LifeXP
Maps self-improvement skills to emoji icons.
"""

SKILL_ICONS = {
    # Physical
    "strength": "💪",
    "endurance": "🏃",
    "fitness": "🏋️",
    "health": "❤️",
    "nutrition": "🥗",
    "flexibility": "🤸",
    "speed": "⚡",
    "stamina": "🔋",
    "recovery": "🛌",
    # Mental
    "focus": "🧠",
    "discipline": "🥋",
    "mindset": "🌅",
    "meditation": "🧘",
    "memory": "💡",
    "learning": "📚",
    "critical thinking": "🔍",
    "problem solving": "🧩",
    "creativity": "🎨",
    "reading": "📖",
    "writing": "✍️",
    # Financial
    "entrepreneurship": "🚀",
    "sales": "💰",
    "marketing": "📣",
    "investing": "📈",
    "budgeting": "💵",
    "finance": "🏦",
    "business": "🏢",
    "negotiation": "🤝",
    "networking": "🌐",
    # Social
    "communication": "🗣️",
    "leadership": "👑",
    "empathy": "💙",
    "public speaking": "🎤",
    "relationships": "🤝",
    "social skills": "😊",
    "teamwork": "👥",
    "influence": "⭐",
    # Spiritual / Personal
    "purpose": "🌟",
    "gratitude": "🙏",
    "resilience": "🛡️",
    "confidence": "🦁",
    "habits": "📅",
    "productivity": "⚙️",
    "time management": "⏰",
    "goal setting": "🎯",
    "self-awareness": "🪞",
    "emotional intelligence": "💜",
}

DEFAULT_ICON = "⭐"


def get_skill_icon(skill_name: str) -> str:
    """
    Return the emoji icon for a given skill name.
    Falls back to DEFAULT_ICON if skill not found.

    Args:
        skill_name: The name of the skill to look up.

    Returns:
        Emoji string for the skill.
    """
    return SKILL_ICONS.get(skill_name.lower().strip(), DEFAULT_ICON)
