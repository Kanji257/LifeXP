"""
profile_store.py — Persistent user profile storage for LifeXP.
Saves all prompts, quest chains, completions, and daily trackers to a JSON file per user.
"""

import json
import os
from datetime import datetime

PROFILES_FILE = "profiles_data.json"


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


def get_profile(username: str) -> dict:
    all_p = load_all_profiles()
    if username not in all_p:
        all_p[username] = {
            "username": username,
            "created": datetime.now().strftime("%b %d, %Y"),
            "prompts": [],          # list of prompt sessions
            "total_xp": 0,
        }
        save_all_profiles(all_p)
    return all_p[username]


def save_profile(username: str, profile: dict):
    all_p = load_all_profiles()
    all_p[username] = profile
    save_all_profiles(all_p)


def add_prompt_session(username: str, session: dict):
    """
    Add or update a prompt session to the user's profile.
    session = {
      id, goal, quiz_answers, user_level, skill_data,
      quest_chains, daily_tasks, daily_checkins,
      xp_tracker, completed_ids, bonus_quests,
      created, last_updated, mastered
    }
    """
    profile = get_profile(username)
    # Update existing session if same id exists
    existing_ids = [p["id"] for p in profile["prompts"]]
    if session["id"] in existing_ids:
        idx = existing_ids.index(session["id"])
        profile["prompts"][idx] = session
    else:
        profile["prompts"].append(session)
    # Recalculate total XP
    profile["total_xp"] = sum(
        sum(v for v in s.get("xp_tracker", {}).values())
        for s in profile["prompts"]
    )
    save_profile(username, profile)


def get_all_usernames() -> list:
    return list(load_all_profiles().keys())
