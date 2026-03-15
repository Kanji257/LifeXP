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


def register_user(username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
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
