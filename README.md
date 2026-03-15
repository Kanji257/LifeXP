# 🎮 LifeXP — AI Gamified Self-Improvement System

> Turn your life goals into a personalized RPG skill tree with AI-generated quests, XP rewards, and daily habit tracking.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red) ![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green)

---

## ✨ Features

- **AI Skill Tree** — enter any life goal and GPT-4o-mini builds a focused skill tree
- **Personalised Quiz** — AI generates questions specific to your goal to tailor difficulty
- **Quest Chains** — 6 ordered quests per skill, unlocking one at a time from your level
- **XP & Levelling** — earn XP, level up, track progress across all skills
- **Mastery System** — complete all quests → unlock a daily habit tracker with infinite XP
- **User Profiles** — save progress across sessions, view history, open past prompts
- **AI Chat** — add/remove skills, ask for advice, customise your tree mid-session
- **Feedback System** — star ratings and reviews visible to all users

---

## 🚀 How to run locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/lifexp.git
cd lifexp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

When the app opens, enter your OpenAI API key in the field at the top.  
Get a free key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

> **Your key is never stored** — it lives only in your browser session and is wiped when you close the tab.

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| Streamlit | Web UI |
| OpenAI GPT-4o-mini | Skill extraction, quest generation, chat |
| NetworkX | Skill tree graph structure |
| Matplotlib | Skill tree visualisation |

---

## 📁 Project Structure

```
lifexp/
├── app.py            # Main Streamlit app
├── ai_engine.py      # All OpenAI API calls
├── skill_tree.py     # Graph building & rendering
├── icons.py          # Skill → emoji mapping
├── quests.py         # XP and level utilities
├── utils.py          # Shared helpers
├── feedback.py       # Feedback storage
├── profile_store.py  # User profile persistence
└── requirements.txt
```

---

## ⚠️ Note on data

`profiles_data.json` and `feedback_data.json` are created locally when users interact with the app. These are listed in `.gitignore` and will never be committed to the repo.

---

*Built as a portfolio project demonstrating LLM integration, gamification design, and full-stack Python web development.*
