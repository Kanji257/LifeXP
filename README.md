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

### Core Game Loop
- **AI Skill Tree** — enter any life goal and GPT-4o-mini builds a focused, relevant skill tree
- **Personalised Quiz** — one question at a time, AI-generated specifically for your goal
- **Quest Chains** — 6 ordered quests per skill unlocking one at a time, tailored to your experience level
- **XP & Levelling** — earn XP, level up, track progress across all skills
- **Mastery System** — complete all quests to reach Mastery, then unlock a daily habit tracker with infinite XP
- **Daily Streaks** — 🔥 streak counter tracks consecutive daily habit completions
- **Interactive Skill Tree** — Plotly-powered, hoverable, zoomable — mastered skills glow gold ⭐
- **Bonus XP Challenges** — optional stretch goals for extra XP
- **AI Chat** — modify your skill tree mid-session, add/remove skills, ask for advice

### Profile & Progress
- **User Accounts** — username + password registration with optional password hint
- **Email Verification** — link your email with a 6-digit verification code
- **Login with Email or Username** — flexible authentication
- **Password Reset via Email** — time-limited 6-digit verification code
- **Profile Dashboard** — level, total XP, goals mastered, XP progress bar
- **Active Goals** — reopen any in-progress goal directly in the Play tab as a live session
- **Mastered Goals** — browse completed goals with full skill tree and daily habits
- **Quest History Log** — full timeline of every completed quest grouped by date
- **Daily Trackers** — all daily habits grouped by goal with streak counters
- **Account Settings** — change email, change password from your profile
- **Profile Reset** — wipe all data and start fresh

### Social
- **Leaderboard** — top 10 players ranked by XP with gold/silver/bronze medals
- **Feedback System** — star ratings and public reviews from all users

### UX & Polish
- **Onboarding Walkthrough** — shown once on first login explaining the full system
- **Mastery Celebration** — balloons + glowing gold banner when all quests are complete
- **Graceful Error Handling** — friendly messages for invalid API keys, no credits, rate limits
- **Persistent sessions** — all progress saved across logins and devices

---

## 🚀 How to run locally

```bash
# 1. Clone the repo
git clone https://github.com/Kanji257/lifexp.git
cd lifexp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up email credentials (for email verification + password reset)
# Create a .env file in the lifexp folder:
# GMAIL_ADDRESS=your@gmail.com
# GMAIL_APP_PASSWORD=your16charapppassword

# 4. Run
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
| OpenAI GPT-4o-mini | Skill extraction, quiz generation, quest chains, AI chat |
| NetworkX | Skill tree graph structure |
| Plotly | Interactive skill tree visualisation |
| Gmail SMTP | Email verification and password reset (swappable with SendGrid) |

---

## 📁 Project Structure

```
lifexp/
├── app.py              # Main Streamlit app — UI, tabs, all session logic
├── ai_engine.py        # OpenAI API calls with graceful error handling
├── skill_tree.py       # Interactive Plotly skill tree rendering
├── email_service.py    # Gmail SMTP email sending (swappable with SendGrid)
├── profile_store.py    # User accounts, auth, profiles, streaks, quest history
├── feedback.py         # Feedback storage and community ratings
├── icons.py            # Skill name → emoji mapping
├── utils.py            # Shared helpers
└── requirements.txt
```

---

## 💼 On AI-Augmented Development

This project was built using what is increasingly called "vibe coding" — directing an AI assistant to write and iterate on code while the developer focuses on architecture, product decisions, debugging, and UX. Rather than manually writing every line of syntax, the workflow looks like this:

- Define a feature clearly and precisely
- Review the generated code and understand how it works
- Identify what breaks, why it breaks, and how to fix it
- Iterate based on real testing and user feedback

This is a **legitimate and increasingly valued skill set**. The ability to rapidly build, ship, and iterate using AI tools — while still understanding the logic, data flow, and architecture — is exactly what startups and forward-thinking teams are looking for.

Challenges solved in this project include: multi-user profile persistence with password hashing, email verification with time-limited codes, Streamlit session state management across reruns, duplicate widget key elimination, quest chain unlock logic, interactive Plotly visualisations, streak tracking, and a full authentication system with email-based password reset.

---

## ⚠️ Notes

- `profiles_data.json` and `feedback_data.json` are created locally and listed in `.gitignore` — never committed
- `.env` file for local email credentials is also in `.gitignore` — never committed
- For the live Streamlit deployment, Gmail credentials are stored in Streamlit Secrets

---

*Built as a portfolio project demonstrating AI-augmented development, LLM integration, gamification design, and full-stack Python web development.*
