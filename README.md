# 🎮 LifeXP — AI Gamified Self-Improvement System

> Turn your life goals into a personalized RPG skill tree with AI-generated quests, XP rewards, and daily habit tracking.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red) ![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green)

**Live demo:** [lifexp-karan-prabuvel.streamlit.app](https://lifexp-karan-prabuvel.streamlit.app)

---

## 🧠 About This Project

LifeXP was built using an **AI-augmented development workflow** — using Claude as a development partner to rapidly prototype, debug, and iterate on a full-stack web application. Every feature was directed, tested, and refined through active problem-solving: defining requirements, identifying bugs, understanding the architecture, and making decisions about UX and system design.

This project demonstrates:
- **Product mindset** — the ability to take an idea from concept to working MVP
- **AI fluency** — leveraging generative AI tools to build faster without sacrificing understanding
- **Rapid prototyping** — a fully functional, multi-feature app built in a fraction of the time traditional development would require
- **Problem-solving** — debugging API errors, fixing UI rendering issues, designing data persistence, and iterating on user experience throughout

> *"It is a valuable skill to be dangerous enough to build."*

---

## ✨ Features

- **AI Skill Tree** — enter any life goal and GPT-4o-mini builds a focused skill tree
- **Personalised Quiz** — AI generates questions specific to your goal to tailor difficulty
- **Quest Chains** — 6 ordered quests per skill, unlocking one at a time from your level
- **XP & Levelling** — earn XP, level up, track progress across all skills
- **Mastery System** — complete all quests → unlock a daily habit tracker with infinite XP
- **User Profiles** — save progress across sessions, view history, open past prompts
- **AI Chat** — add/remove skills, ask for advice, customise your tree mid-session
- **Feedback System** — star ratings and public reviews from all users

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
| Streamlit | Web UI framework |
| OpenAI GPT-4o-mini | Skill extraction, quest generation, AI chat |
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

## 💼 On AI-Augmented Development

This project was built using what is increasingly called "vibe coding" — directing an AI assistant to write and iterate on code while the developer focuses on architecture, product decisions, debugging, and UX. Rather than manually writing every line of syntax, the workflow looks like this:

- Define a feature clearly and precisely
- Review the generated code and understand how it works
- Identify what breaks, why it breaks, and how to fix it
- Iterate based on real testing and user feedback

This is a **legitimate and increasingly valued skill set**. The ability to rapidly build, ship, and iterate using AI tools — while still understanding the logic, data flow, and architecture — is exactly what startups and forward-thinking teams are looking for. It demonstrates AI fluency, product thinking, and the ability to turn an idea into a working product quickly.

The challenges encountered and solved in this project included: designing a persistent multi-user profile system, fixing Streamlit's tab rendering limitations, implementing a quest chain unlock system, debugging API authentication flows, and building a real-time XP and levelling system — none of which are trivial regardless of how the code was written.

---

## ⚠️ Note on data

`profiles_data.json` and `feedback_data.json` are created locally when users interact with the app. These are listed in `.gitignore` and will never be committed to the repo.

---

*Built as a portfolio project demonstrating AI-augmented development, LLM integration, gamification design, and full-stack Python web development.*
