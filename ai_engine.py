"""
ai_engine.py — LifeXP AI Engine
All functions accept api_key from user session. Includes graceful error handling.
"""

import json
import re
from openai import OpenAI, AuthenticationError, RateLimitError, APIError


def parse_json(text: str):
    cleaned = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"[\[{].*[\]}]", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None


def get_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)


def safe_call(func):
    """
    Decorator that wraps AI calls with friendly error handling.
    Returns (result, error_message). error_message is None on success.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs), None
        except AuthenticationError:
            return None, "❌ Invalid API key. Please check your key and try again."
        except RateLimitError:
            return None, "❌ Your OpenAI account has no credits. Add credits at platform.openai.com/settings/billing"
        except APIError as e:
            return None, f"❌ OpenAI API error: {str(e)[:120]}"
        except Exception as e:
            return None, f"❌ Unexpected error: {str(e)[:120]}"
    return wrapper


@safe_call
def extract_skill_tree(goals: str, api_key: str) -> dict:
    client = get_client(api_key)
    prompt = f"""You are a self-improvement expert building a focused skill tree.

User's goal: "{goals}"

Instructions:
- Extract ONLY skills and categories DIRECTLY relevant to this specific goal
- Do NOT add generic categories unless explicitly mentioned
- Keep it focused: 1-3 categories max, 2-4 skills each
- Skills should be specific and actionable

Return ONLY valid JSON:
{{"Category": ["Skill1", "Skill2"]}}"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6, max_tokens=400,
    )
    result = parse_json(resp.choices[0].message.content)
    return result if isinstance(result, dict) else {}


@safe_call
def generate_quiz_questions(goals: str, api_key: str) -> list:
    client = get_client(api_key)
    prompt = f"""You are building a personalisation quiz for a self-improvement app.

The user's goal is: "{goals}"

Generate exactly 5 quiz questions DIRECTLY relevant to this goal.
These help personalise the quest difficulty and starting point for the user.

Rules:
- All questions must be specific to this goal
- Include one question about current experience level
- Include one about biggest challenge related to this goal
- Include one about how much time they can commit per day
- Options should reveal where the user is NOW

Return ONLY valid JSON:
[
  {{
    "id": "q1",
    "question": "Question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"]
  }}
]"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7, max_tokens=800,
    )
    result = parse_json(resp.choices[0].message.content)
    if isinstance(result, list):
        return result
    return [
        {"id": "q1", "question": "What is your current experience level?",
         "options": ["Complete beginner", "Some experience", "Intermediate", "Advanced"]},
        {"id": "q2", "question": "How much time can you commit daily?",
         "options": ["Under 15 mins", "15-30 mins", "30-60 mins", "1+ hour"]},
    ]


@safe_call
def generate_quest_chain(skill: str, category: str, quiz_answers: dict,
                          user_level: str, api_key: str) -> list:
    client = get_client(api_key)
    context = "\n".join(f"- {k}: {v}" for k, v in quiz_answers.items() if v)

    prompt = f"""You are designing a progressive quest chain for LifeXP.

USER PROFILE:
{context}
Experience Level: {user_level}

Design a progressive quest chain for the skill "{skill}" (category: {category}).
Generate exactly 6 quests ordered from easiest to hardest.
Quest 1 should match where the user IS RIGHT NOW.

Return ONLY a JSON list:
[
  {{"task": "Quest description", "difficulty": "Starter", "xp": 30, "order": 1}},
  {{"task": "Quest description", "difficulty": "Easy", "xp": 50, "order": 2}},
  {{"task": "Quest description", "difficulty": "Easy", "xp": 70, "order": 3}},
  {{"task": "Quest description", "difficulty": "Medium", "xp": 100, "order": 4}},
  {{"task": "Quest description", "difficulty": "Hard", "xp": 140, "order": 5}},
  {{"task": "Quest description", "difficulty": "Master", "xp": 200, "order": 6}}
]"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8, max_tokens=700,
    )
    result = parse_json(resp.choices[0].message.content)
    if isinstance(result, list) and len(result) > 0:
        for i, q in enumerate(result):
            q["id"] = f"{skill}_{i}"
            q["completed"] = False
        return result
    return [
        {"task": f"Spend 10 minutes learning about {skill}", "difficulty": "Starter", "xp": 30, "order": 1, "id": f"{skill}_0", "completed": False},
        {"task": f"Practice {skill} for 20 minutes", "difficulty": "Easy", "xp": 50, "order": 2, "id": f"{skill}_1", "completed": False},
        {"task": f"Complete a {skill} challenge", "difficulty": "Medium", "xp": 100, "order": 3, "id": f"{skill}_2", "completed": False},
        {"task": f"Teach someone about {skill}", "difficulty": "Hard", "xp": 150, "order": 4, "id": f"{skill}_3", "completed": False},
        {"task": f"Build a consistent {skill} practice for 7 days", "difficulty": "Master", "xp": 200, "order": 5, "id": f"{skill}_4", "completed": False},
    ]


@safe_call
def generate_daily_checkin_task(skill: str, category: str,
                                 quiz_answers: dict, api_key: str) -> dict:
    client = get_client(api_key)
    context = "\n".join(f"- {k}: {v}" for k, v in quiz_answers.items() if v)

    prompt = f"""A user has fully mastered the skill "{skill}" in category "{category}".
Profile: {context}
Create ONE daily maintenance task achievable in under 30 minutes.
Return ONLY valid JSON: {{"task": "Daily task description", "xp": 25}}"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7, max_tokens=200,
    )
    result = parse_json(resp.choices[0].message.content)
    if isinstance(result, dict) and "task" in result:
        return result
    return {"task": f"Practise {skill} for 15 minutes", "xp": 25}


@safe_call
def generate_bonus_challenges(goals: str, quiz_answers: dict, api_key: str) -> list:
    client = get_client(api_key)
    context = "\n".join(f"- {k}: {v}" for k, v in quiz_answers.items() if v)

    prompt = f"""Generate 3 bonus stretch challenges for goal: "{goals}"
Profile: {context}
Return ONLY a JSON list:
[
  {{"task": "Bonus challenge", "difficulty": "Bonus", "xp": 200}},
  {{"task": "Bonus challenge", "difficulty": "Bonus", "xp": 250}},
  {{"task": "Bonus challenge", "difficulty": "Bonus", "xp": 300}}
]"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9, max_tokens=400,
    )
    result = parse_json(resp.choices[0].message.content)
    if isinstance(result, list):
        for i, q in enumerate(result):
            q["id"] = f"bonus_{i}"
        return result
    return []


@safe_call
def chat_modify_tree(user_message: str, current_skill_data: dict, goals: str,
                     quiz_answers: dict, user_level: str, api_key: str) -> dict:
    client = get_client(api_key)
    tree_summary = json.dumps(current_skill_data, indent=2)
    context = "\n".join(f"- {k}: {v}" for k, v in quiz_answers.items() if v)

    prompt = f"""You are the LifeXP AI assistant helping customise a skill tree.
Goal: "{goals}" | Level: {user_level}
Profile: {context}
Current tree: {tree_summary}
User message: "{user_message}"

Return ONLY valid JSON:
{{
  "reply": "Friendly 1-2 sentence response",
  "action": "add_skill" | "remove_skill" | "add_category" | "remove_category" | "none",
  "skill": "SkillName or null",
  "category": "CategoryName or null"
}}"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7, max_tokens=300,
    )
    result = parse_json(resp.choices[0].message.content)
    if isinstance(result, dict):
        return result
    return {"reply": "I couldn't process that. Could you rephrase?",
            "action": "none", "skill": None, "category": None}
