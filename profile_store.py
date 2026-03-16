"""
profile_store.py — Persistent user profile storage for LifeXP.
Includes password hashing for secure login/register.
"""

import json
import os
import hashlib
from datetime import datetime

PROFILES_FILE = "profiles_data.json"


def _hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_all_profiles() -> dict:
    if not os.path.exists(PROFILES_FILE):
        return {}
    try:
        with open(PROFILES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_all_profiles(data: dict):
    with open(PROFILES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def username_exists(username: str) -> bool:
    """Check if a username is already registered (case-insensitive)."""
    all_p = load_all_profiles()
    return username.lower() in [u.lower() for u in all_p.keys()]


def register_user(username: str, password: str, password_hint: str = "") -> tuple[bool, str]:
    """
    Register a new user with an optional password hint.
    Returns (success, message).
    """
    if not username.strip():
        return False, "Username cannot be empty."
    if not password.strip():
        return False, "Password cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    if username_exists(username):
        return False, f'Username "{username}" is already taken. Please choose a different one.'

    all_p = load_all_profiles()
    all_p[username] = {
        "username": username,
        "password_hash": _hash_password(password),
        "password_hint": password_hint.strip() if password_hint else "",
        "created": datetime.now().strftime("%b %d, %Y"),
        "prompts": [],
        "total_xp": 0,
    }
    save_all_profiles(all_p)
    return True, "Account created successfully!"


def login_user(username: str, password: str) -> tuple[bool, str]:
    """
    Attempt to log in.
    Returns (success, message).
    """
    if not username.strip() or not password.strip():
        return False, "Please enter both username and password."

    all_p = load_all_profiles()

    # Case-insensitive username lookup
    matched_key = next((k for k in all_p if k.lower() == username.lower()), None)
    if not matched_key:
        return False, "Username not found. Please register first."

    profile = all_p[matched_key]

    # Handle legacy profiles with no password (set during migration)
    if "password_hash" not in profile:
        return False, "This account needs a password reset. Please register a new account."

    if profile["password_hash"] != _hash_password(password):
        return False, "Incorrect password. Please try again."

    return True, matched_key  # return the exact cased username


def get_password_hint(username: str) -> str:
    """Return the password hint for a username, or empty string if none."""
    all_p = load_all_profiles()
    matched_key = next((k for k in all_p if k.lower() == username.lower()), None)
    if not matched_key:
        return ""
    return all_p[matched_key].get("password_hint", "")


def log_quest_completion(username: str, prompt_id: str, skill: str,
                          quest_task: str, xp: int, difficulty: str):
    """Append a quest completion event to the user's history log."""
    all_p = load_all_profiles()
    # Case-insensitive key match
    matched_key = next((k for k in all_p if k.lower() == username.lower()), None)
    if not matched_key:
        return
    username = matched_key
    profile = all_p[username]
    if "quest_history" not in profile:
        profile["quest_history"] = []
    profile["quest_history"].append({
        "date": datetime.now().strftime("%b %d, %Y"),
        "time": datetime.now().strftime("%H:%M"),
        "skill": skill,
        "task": quest_task,
        "xp": xp,
        "difficulty": difficulty,
        "prompt_id": prompt_id,
    })
    # Keep last 200 entries max
    profile["quest_history"] = profile["quest_history"][-200:]
    all_p[username] = profile
    save_all_profiles(all_p)


def get_quest_history(username: str) -> list:
    """Return quest completion history for a user, newest first."""
    all_p = load_all_profiles()
    matched_key = next((k for k in all_p if k.lower() == username.lower()), None)
    if not matched_key:
        return []
    return list(reversed(all_p[matched_key].get("quest_history", [])))


def get_profile(username: str) -> dict:
    all_p = load_all_profiles()
    if username not in all_p:
        all_p[username] = {
            "username": username,
            "created": datetime.now().strftime("%b %d, %Y"),
            "prompts": [],
            "total_xp": 0,
        }
        save_all_profiles(all_p)
    return all_p[username]


def save_profile(username: str, profile: dict):
    all_p = load_all_profiles()
    all_p[username] = profile
    save_all_profiles(all_p)


def add_prompt_session(username: str, session: dict):
    """Add or update a prompt session in the user's profile."""
    profile = get_profile(username)
    existing_ids = [p["id"] for p in profile["prompts"]]
    if session["id"] in existing_ids:
        idx = existing_ids.index(session["id"])
        profile["prompts"][idx] = session
    else:
        profile["prompts"].append(session)
    profile["total_xp"] = sum(
        sum(v for v in s.get("xp_tracker", {}).values())
        for s in profile["prompts"]
    )
    save_profile(username, profile)


def get_all_usernames() -> list:
    return list(load_all_profiles().keys())


def _recompute_mastered(p: dict) -> bool:
    """Recompute mastery from completed_ids vs quest_chains (don't rely on saved flag)."""
    if p.get("mastered"):
        return True
    cids = set(p.get("completed_ids", []))
    chains = p.get("quest_chains", {})
    sd = p.get("skill_data", {})
    if not sd or not cids:
        return False
    return all(
        bool(chains.get(s)) and all(q["id"] in cids for q in chains.get(s, []))
        for sks in sd.values() for s in sks
    )


def get_leaderboard(limit: int = 10) -> list:
    """
    Return top users sorted by total_xp.
    Returns list of {username, total_xp, level, mastered_count}.
    """
    all_p = load_all_profiles()
    board = []
    for username, profile in all_p.items():
        # Skip system/internal keys
        if not isinstance(profile, dict) or "created" not in profile:
            continue
        xp = profile.get("total_xp", 0)
        prompts = profile.get("prompts", [])
        mastered = sum(1 for p in prompts if _recompute_mastered(p))
        level = (xp // 200) + 1
        board.append({
            "username": username,
            "total_xp": xp,
            "level": level,
            "mastered_count": mastered,
        })
    board.sort(key=lambda x: x["total_xp"], reverse=True)
    return board[:limit]


def update_streak(username: str, skill: str, prompt_id: str) -> int:
    """
    Update the streak for a daily habit.
    Stores last_checkin date and current streak count.
    Returns the new streak count.
    """
    from datetime import date
    all_p = load_all_profiles()
    if username not in all_p:
        return 1

    profile = all_p[username]
    if "streaks" not in profile:
        profile["streaks"] = {}

    key = f"{prompt_id}_{skill}"
    today = str(date.today())
    streak_data = profile["streaks"].get(key, {"count": 0, "last_date": ""})

    last_date = streak_data.get("last_date", "")
    count = streak_data.get("count", 0)

    if last_date == today:
        # Already checked in today — don't increment
        return count
    elif last_date == str(date.today().replace(day=date.today().day - 1) if date.today().day > 1 else date.today()):
        # Consecutive day
        count += 1
    else:
        # Streak broken or first time
        from datetime import date, timedelta
        yesterday = str(date.today() - timedelta(days=1))
        if last_date == yesterday:
            count += 1
        else:
            count = 1

    profile["streaks"][key] = {"count": count, "last_date": today}
    all_p[username] = profile
    save_all_profiles(all_p)
    return count


def get_streak(username: str, skill: str, prompt_id: str) -> dict:
    """Get current streak info for a skill."""
    from datetime import date, timedelta
    all_p = load_all_profiles()
    if username not in all_p:
        return {"count": 0, "active": False}

    profile = all_p[username]
    streaks = profile.get("streaks", {})
    key = f"{prompt_id}_{skill}"
    streak_data = streaks.get(key, {"count": 0, "last_date": ""})

    count = streak_data.get("count", 0)
    last_date = streak_data.get("last_date", "")
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))

    # Streak is active if checked in today or yesterday
    active = last_date in (today, yesterday)
    return {"count": count, "active": active, "last_date": last_date}
