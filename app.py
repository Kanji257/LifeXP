"""
app.py — LifeXP v8 — Clean rebuild
- Tabs: Play | My Profile | Feedback
- No hamburger, no sidebar mess
- Fixed chat text input
- Fixed mastery celebration
- No stray text anywhere
"""

import streamlit as st
import uuid
from datetime import datetime
from ai_engine import (
    extract_skill_tree, generate_quiz_questions, generate_quest_chain,
    generate_daily_checkin_task, generate_bonus_challenges, chat_modify_tree
)
from skill_tree import build_skill_tree, render_skill_tree
from icons import get_skill_icon
from feedback import save_feedback, load_feedback, get_stats
from profile_store import get_profile, save_profile, add_prompt_session, get_all_usernames, register_user, login_user

XP_PER_LEVEL = 200

st.set_page_config(page_title="LifeXP", page_icon="🎮", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@400;600&display=swap');
  html,body,[class*="css"]{background:#0F0F1A;color:#E0E0F0;font-family:'Rajdhani',sans-serif;}
  h1,h2,h3{font-family:'Orbitron',sans-serif !important;}
  .hero-title{font-family:'Orbitron',sans-serif;font-size:2.8rem;font-weight:900;
    background:linear-gradient(135deg,#A78BFA,#60A5FA,#34D399);-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;text-align:center;letter-spacing:.05em;}
  .hero-sub{text-align:center;color:#8888AA;font-size:1rem;letter-spacing:.08em;margin-bottom:1.2rem;}
  .skill-card{background:linear-gradient(145deg,#1A1A2E,#16213E);border:1px solid #2A2A4A;
    border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:1.1rem;}
  .skill-header{font-family:'Orbitron',sans-serif;font-size:.88rem;color:#A78BFA;letter-spacing:.07em;margin-bottom:.35rem;}
  .xp-bar-bg{background:#1E1E3A;border-radius:8px;height:8px;margin:.35rem 0 .55rem;overflow:hidden;}
  .xp-bar-fill{height:8px;border-radius:8px;background:linear-gradient(90deg,#7C3AED,#2563EB,#059669);}
  .level-badge{display:inline-block;background:#312E81;color:#C4B5FD;padding:1px 8px;
    border-radius:20px;font-size:.68rem;font-family:'Orbitron',sans-serif;margin-left:.35rem;}
  .mastery-badge{display:inline-block;background:linear-gradient(135deg,#F59E0B,#EF4444);
    color:#fff;padding:1px 8px;border-radius:20px;font-size:.68rem;
    font-family:'Orbitron',sans-serif;margin-left:.35rem;}
  .quest-done{padding:.38rem .65rem;margin:.18rem 0;border-radius:7px;background:#0F2A1A;
    border:1px solid #1A4A2A;opacity:.5;font-size:.84rem;}
  .quest-locked{padding:.38rem .65rem;margin:.18rem 0;border-radius:7px;background:#111128;
    border:1px solid #1E1E3A;font-size:.84rem;color:#3A3A5A;}
  .quest-active{padding:.38rem .65rem;margin:.18rem 0;border-radius:7px;background:#16162A;
    border:1px solid #4A3A8A;font-size:.84rem;box-shadow:0 0 8px rgba(124,58,237,.18);}
  .daily-card{background:linear-gradient(145deg,#0A1A0F,#0F2A1A);border:1px solid #1A5A2A;
    border-radius:12px;padding:1rem 1.2rem;margin-bottom:1rem;}
  .bonus-card{background:linear-gradient(145deg,#1A0A2E,#2A1040);border:1px solid #5A2A8A;
    border-radius:12px;padding:1rem 1.2rem;margin-bottom:.85rem;}
  .chat-user{background:#1E1B4B;border-radius:12px 12px 2px 12px;padding:.6rem .9rem;
    margin:.3rem 0;max-width:80%;margin-left:auto;font-size:.88rem;color:#C4B5FD;}
  .chat-ai{background:#16213E;border:1px solid #2A2A4A;border-radius:12px 12px 12px 2px;
    padding:.6rem .9rem;margin:.3rem 0;max-width:85%;font-size:.88rem;}
  .divider{border:none;border-top:1px solid #2A2A4A;margin:1.8rem 0;}
  .category-tag{display:inline-block;background:#1E1B4B;color:#818CF8;padding:2px 10px;
    border-radius:20px;font-size:.68rem;font-family:'Orbitron',sans-serif;
    letter-spacing:.06em;margin-bottom:.6rem;}
  .prompt-mastered{background:linear-gradient(135deg,#0A1A05,#0F2A10);border:1px solid #2A5A1A;
    border-radius:12px;padding:1rem 1.3rem;margin-bottom:.85rem;}
  .prompt-active{background:linear-gradient(145deg,#1A1A2E,#16213E);border:1px solid #3A2A6A;
    border-radius:12px;padding:1rem 1.3rem;margin-bottom:.85rem;}
  @keyframes glowpulse{0%,100%{box-shadow:0 0 30px #F59E0B55,0 0 60px #EF444422}
    50%{box-shadow:0 0 60px #F59E0BAA,0 0 100px #EF444455}}
  @keyframes popIn{from{transform:scale(.4) rotate(-6deg);opacity:0}
    to{transform:scale(1) rotate(0);opacity:1}}
  .mastery-banner{background:linear-gradient(135deg,#1A0A00,#2A1500);
    border:2px solid #F59E0B;border-radius:16px;padding:2rem 2.5rem;
    text-align:center;animation:glowpulse 2.5s infinite, popIn .5s cubic-bezier(.175,.885,.32,1.275);}
  .mastery-persist{background:linear-gradient(135deg,#1A0A00,#2A1500);
    border:2px solid #F59E0B;border-radius:14px;padding:1.1rem 1.6rem;
    margin-bottom:1.3rem;animation:glowpulse 2.5s infinite;}
  /* Hide Streamlit chrome */
  #MainMenu,footer,header{visibility:hidden;}
  [data-testid="stSidebar"]{display:none !important;}
  [data-testid="stSidebarCollapsedControl"]{display:none !important;}
  [data-testid="stSidebarCollapseButton"]{display:none !important;}
  /* Inputs */
  .stTextArea textarea{background:#1A1A2E !important;color:#E0E0F0 !important;
    border:1px solid #3A3A5A !important;border-radius:8px !important;
    font-family:'Rajdhani',sans-serif !important;font-size:1rem !important;}
  .stTextInput>div>div>input{background:#1A1A2E !important;color:#E0E0F0 !important;
    border:1px solid #3A3A5A !important;border-radius:8px !important;
    font-family:'Rajdhani',sans-serif !important;font-size:.95rem !important;
    padding:.5rem .8rem !important;}
  .stButton>button{background:linear-gradient(135deg,#7C3AED,#2563EB) !important;
    color:#fff !important;border:none !important;border-radius:9px !important;
    font-family:'Orbitron',sans-serif !important;font-size:.74rem !important;
    letter-spacing:.04em !important;padding:.42rem .9rem !important;width:100% !important;
    box-shadow:0 3px 12px rgba(124,58,237,.28) !important;}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
def fresh_session():
    return {
        "goal_input": "", "quiz_questions": [], "quiz_answers": {},
        "quiz_done": False, "user_level": "Beginner",
        "skill_data": {}, "quest_chains": {}, "daily_tasks": {},
        "daily_checkins": {}, "bonus_quests": [], "generated": False,
        "xp_tracker": {}, "completed_ids": set(), "chat_history": [],
        "session_id": str(uuid.uuid4()),
        "session_created": datetime.now().strftime("%b %d, %Y"),
        "mastery_shown": False,
        "mastery_dismissed": False,
        "mastery_celebrated_ids": set(),
    }

for k, v in fresh_session().items():
    if k not in st.session_state:
        st.session_state[k] = v

# api_key lives separately — never wiped by fresh_session
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "username" not in st.session_state: st.session_state.username = ""
if "viewing_prompt_id" not in st.session_state: st.session_state.viewing_prompt_id = None
if "profile_section" not in st.session_state: st.session_state.profile_section = "account"
if "confirm_delete_id" not in st.session_state: st.session_state.confirm_delete_id = None
if "confirm_reset" not in st.session_state: st.session_state.confirm_reset = False

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_level_info(xp):
    level = (xp // XP_PER_LEVEL) + 1
    cur = xp % XP_PER_LEVEL
    return {"level": level, "current_xp": cur, "pct": int(cur / XP_PER_LEVEL * 100)}

def add_xp(skill, amount):
    st.session_state.xp_tracker[skill] = st.session_state.xp_tracker.get(skill, 0) + amount

def is_mastered(skill, cids=None, chains=None):
    if cids is None: cids = st.session_state.completed_ids
    if chains is None: chains = st.session_state.quest_chains
    chain = chains.get(skill, [])
    return bool(chain) and all(q["id"] in cids for q in chain)

def all_mastered(sd=None, cids=None, chains=None):
    if sd is None: sd = st.session_state.skill_data
    if not sd: return False
    return all(is_mastered(s, cids, chains) for sks in sd.values() for s in sks)

def save_session():
    if not st.session_state.username or not st.session_state.generated: return
    add_prompt_session(st.session_state.username, {
        "id": st.session_state.session_id,
        "goal": st.session_state.goal_input,
        "quiz_answers": st.session_state.quiz_answers,
        "user_level": st.session_state.user_level,
        "skill_data": st.session_state.skill_data,
        "quest_chains": st.session_state.quest_chains,
        "daily_tasks": st.session_state.daily_tasks,
        "daily_checkins": st.session_state.daily_checkins,
        "bonus_quests": st.session_state.bonus_quests,
        "xp_tracker": st.session_state.xp_tracker,
        "completed_ids": list(st.session_state.completed_ids),
        "created": st.session_state.session_created,
        "last_updated": datetime.now().strftime("%b %d, %Y %H:%M"),
        "mastered": all_mastered(),
    })

def apply_chat_action(result):
    action = result.get("action", "none")
    skill = result.get("skill")
    category = result.get("category")
    if action == "add_skill" and skill and category:
        if category not in st.session_state.skill_data:
            st.session_state.skill_data[category] = []
        if skill not in st.session_state.skill_data[category]:
            st.session_state.skill_data[category].append(skill)
            st.session_state.quest_chains[skill] = generate_quest_chain(
                skill, category, st.session_state.quiz_answers, st.session_state.user_level, api_key=st.session_state.api_key)
            st.session_state.xp_tracker[skill] = 0
        return f"✅ Added **{skill}** to **{category}**"
    elif action == "remove_skill" and skill:
        for cat, sks in list(st.session_state.skill_data.items()):
            if skill in sks:
                sks.remove(skill)
                if not sks: del st.session_state.skill_data[cat]
                st.session_state.quest_chains.pop(skill, None)
                st.session_state.xp_tracker.pop(skill, None)
                return f"🗑️ Removed **{skill}**"
    elif action == "add_category" and category:
        if category not in st.session_state.skill_data:
            st.session_state.skill_data[category] = []
        return f"✅ Added category **{category}**"
    elif action == "remove_category" and category:
        if category in st.session_state.skill_data:
            for s in st.session_state.skill_data[category]:
                st.session_state.quest_chains.pop(s, None)
                st.session_state.xp_tracker.pop(s, None)
            del st.session_state.skill_data[category]
            return f"🗑️ Removed **{category}**"
    return None

# ── render_prompt_session ──────────────────────────────────────────────────────
def render_prompt_session(sd, chains, xp_t, cids_list, daily_t, daily_c,
                           bonus_q, goal, level, quiz_ans, is_live=True, sid=None, past_pid=None):
    diff_colors = {"Starter":"#60A5FA","Easy":"#34D399","Medium":"#FCD34D",
                   "Hard":"#F87171","Master":"#C084FC"}
    # Use the correct completed IDs — live session state for active, frozen list for past
    cids = st.session_state.completed_ids if is_live else set(cids_list)

    # Skill tree
    st.markdown("### 🌳 Skill Tree")
    G = build_skill_tree(sd)
    fig = render_skill_tree(G, sd)
    st.pyplot(fig, use_container_width=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("### ⚔️ Quest Chains")
    if is_live:
        st.markdown("*Complete quests in order. Finish all to reach Mastery and unlock daily infinite XP.*")

    for category, skills in sd.items():
        st.markdown(f'<div class="category-tag">⚡ {category.upper()}</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(skills), 3))
        for ci, skill in enumerate(skills):
            icon = get_skill_icon(skill)
            chain = chains.get(skill, [])
            total_xp = xp_t.get(skill, 0)
            li = get_level_info(total_xp)
            mastered = bool(chain) and all(q["id"] in cids for q in chain)
            active_idx = None
            if not mastered:
                for i, q in enumerate(chain):
                    if q["id"] not in cids:
                        active_idx = i; break

            with cols[ci % len(cols)]:
                mb = '<span class="mastery-badge">✨ MASTERED</span>' if mastered \
                     else f'<span class="level-badge">LVL {li["level"]}</span>'
                st.markdown(f"""<div class="skill-card">
  <div class="skill-header">{icon} {skill} {mb}</div>
  <div style="font-size:.74rem;color:#6B7280;margin-bottom:3px;">
    {li['current_xp']} / {XP_PER_LEVEL} XP · {total_xp} total
  </div>
  <div class="xp-bar-bg"><div class="xp-bar-fill" style="width:{li['pct']}%;"></div></div>
</div>""", unsafe_allow_html=True)

                if mastered:
                    daily = daily_t.get(skill)
                    if not daily and is_live:
                        with st.spinner(f"Generating daily habit for {skill}..."):
                            daily = generate_daily_checkin_task(skill, category, quiz_ans, api_key=st.session_state.api_key)
                        st.session_state.daily_tasks[skill] = daily
                        save_session()
                    if daily:
                        task_txt = daily["task"] if isinstance(daily, dict) else daily
                        dxp = daily.get("xp", 25) if isinstance(daily, dict) else 25
                        checkins = daily_c.get(skill, 0)
                        st.markdown(f"""<div class="daily-card">
  <div style="font-family:'Orbitron',sans-serif;color:#34D399;font-size:.68rem;margin-bottom:.28rem;">
    🔁 DAILY HABIT · {checkins} days
  </div>
  <div style="font-size:.86rem;margin-bottom:.42rem;">{task_txt}</div>
  <span style="color:#34D399;font-size:.76rem;">+{dxp} XP/day</span>
</div>""", unsafe_allow_html=True)
                        if st.button(f"✅ Done today +{dxp} XP", key=f"daily_{skill}_{sid}"):
                                if is_live:
                                    st.session_state.daily_checkins[skill] = checkins + 1
                                    add_xp(skill, dxp)
                                    save_session()
                                elif past_pid and st.session_state.username:
                                    prof = get_profile(st.session_state.username)
                                    for sess in prof["prompts"]:
                                        if sess["id"] == past_pid:
                                            dc = sess.get("daily_checkins", {})
                                            dc[skill] = dc.get(skill, 0) + 1
                                            sess["daily_checkins"] = dc
                                            xtr = sess.get("xp_tracker", {})
                                            xtr[skill] = xtr.get(skill, 0) + dxp
                                            sess["xp_tracker"] = xtr
                                            break
                                    prof["total_xp"] = sum(
                                        sum(v for v in s.get("xp_tracker",{}).values())
                                        for s in prof["prompts"])
                                    save_profile(st.session_state.username, prof)
                                st.rerun()
                else:
                    for i, q in enumerate(chain):
                        qid = q["id"]; task = q.get("task","")
                        diff = q.get("difficulty","Easy"); qxp = q.get("xp", 50)
                        done = qid in cids; is_act = (i == active_idx)
                        dc = diff_colors.get(diff, "#9CA3AF")
                        if done:
                            st.markdown(
                                f'<div class="quest-done">✅ <s>{task}</s> '
                                f'<span style="color:#34D399;font-size:.72rem;">+{qxp} XP</span></div>',
                                unsafe_allow_html=True)
                        elif is_act:
                            st.markdown(f"""<div class="quest-active">
<span style="color:{dc};font-size:.68rem;font-family:'Orbitron',sans-serif;">{diff}</span><br>
{task}<br>
<span style="color:#6366F1;font-size:.74rem;">+{qxp} XP</span>
</div>""", unsafe_allow_html=True)
                            if st.button(f"Complete +{qxp} XP", key=f"btn_{qid}"):
                                    if is_live:
                                        st.session_state.completed_ids.add(qid)
                                        add_xp(skill, qxp)
                                        save_session()
                                    elif past_pid and st.session_state.username:
                                        prof = get_profile(st.session_state.username)
                                        for sess in prof["prompts"]:
                                            if sess["id"] == past_pid:
                                                cids_p = sess.get("completed_ids", [])
                                                if qid not in cids_p:
                                                    cids_p.append(qid)
                                                sess["completed_ids"] = cids_p
                                                xtr = sess.get("xp_tracker", {})
                                                xtr[skill] = xtr.get(skill, 0) + qxp
                                                sess["xp_tracker"] = xtr
                                                break
                                        prof["total_xp"] = sum(
                                            sum(v for v in s.get("xp_tracker",{}).values())
                                            for s in prof["prompts"])
                                        save_profile(st.session_state.username, prof)
                                    st.rerun()
                        else:
                            st.markdown(
                                f'<div class="quest-locked">🔒 '
                                f'<span style="color:{dc};font-size:.68rem;">{diff}</span>'
                                f' — complete previous first</div>',
                                unsafe_allow_html=True)
        st.markdown("")

    if bonus_q:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("### ⭐ Bonus XP Challenges")
        b_cols = st.columns(min(len(bonus_q), 3))
        for i, bq in enumerate(bonus_q):
            qid = bq.get("id", f"bonus_{i}")
            qxp = bq.get("xp", 200); task = bq.get("task","")
            done = qid in cids
            with b_cols[i % len(b_cols)]:
                st.markdown(f"""<div class="bonus-card">
<div style="font-family:'Orbitron',sans-serif;color:#C084FC;font-size:.68rem;margin-bottom:.25rem;">⭐ BONUS</div>
<div style="font-size:.86rem;margin-bottom:.38rem;{'opacity:.4;text-decoration:line-through;' if done else ''}">{task}</div>
<span style="color:#F59E0B;font-size:.76rem;">+{qxp} XP</span>
</div>""", unsafe_allow_html=True)
                if done:
                    st.markdown("✅ Completed!")
                else:
                    if st.button(f"Complete +{qxp} XP", key=f"btn_{qid}_{sid}"):
                        if is_live:
                            st.session_state.completed_ids.add(qid)
                            add_xp("bonus", qxp)
                            save_session()
                        elif past_pid and st.session_state.username:
                            prof = get_profile(st.session_state.username)
                            for sess in prof["prompts"]:
                                if sess["id"] == past_pid:
                                    cids_p = sess.get("completed_ids", [])
                                    if qid not in cids_p: cids_p.append(qid)
                                    sess["completed_ids"] = cids_p
                                    break
                            save_profile(st.session_state.username, prof)
                        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="hero-title">🎮 LifeXP</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">AI · GAMIFIED · SELF-IMPROVEMENT · SYSTEM</div>', unsafe_allow_html=True)

# ── API Key input — each user enters their own key ────────────────────────────
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Always render the key input so its value persists in session state
_key_val = st.session_state.api_key

with st.expander("🔑 OpenAI API Key", expanded=not bool(_key_val)):
    st.markdown("""<div style="font-size:.88rem;color:#9CA3AF;margin-bottom:.6rem;">
LifeXP uses OpenAI to generate your skill tree and quests. Enter your own API key below —
it is <strong style="color:#34D399;">never stored</strong> and only lives in your browser session.
Get a free key at <a href="https://platform.openai.com/api-keys" target="_blank"
style="color:#60A5FA;">platform.openai.com/api-keys</a>
</div>""", unsafe_allow_html=True)
    typed_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-proj-...",
        label_visibility="collapsed",
        key="api_key_field"
    )
    if typed_key.strip():
        st.session_state.api_key = typed_key.strip()
        _key_val = st.session_state.api_key
    if _key_val:
        st.success("✅ API key active for this session.")
    if st.button("Save Key ➜", key="save_key_btn") and typed_key.strip():
        st.session_state.api_key = typed_key.strip()
        st.rerun()

if not st.session_state.api_key:
    st.info("👆 Enter your OpenAI API key above to unlock LifeXP. Get one free at platform.openai.com")
    st.stop()

# ── Login / Register ──────────────────────────────────────────────────────────
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # "login" or "register"

if not st.session_state.username:
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    auth_c1, auth_c2, auth_c3 = st.columns([1, 2, 1])
    with auth_c2:
        # Toggle between login and register
        mode_c1, mode_c2 = st.columns(2)
        with mode_c1:
            if st.button("🔑 Log In", key="mode_login",
                         use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()
        with mode_c2:
            if st.button("✨ Register", key="mode_register",
                         use_container_width=True):
                st.session_state.auth_mode = "register"
                st.rerun()

        st.markdown(f"""<div style="text-align:center;font-family:'Orbitron',sans-serif;
color:#A78BFA;font-size:.78rem;letter-spacing:.08em;margin:.6rem 0;">
{'LOG IN TO YOUR ACCOUNT' if st.session_state.auth_mode == "login" else 'CREATE AN ACCOUNT'}
</div>""", unsafe_allow_html=True)

        auth_username = st.text_input("Username", placeholder="Enter your username",
                                       key="auth_username")
        auth_password = st.text_input("Password", placeholder="Enter your password",
                                       type="password", key="auth_password")

        if st.session_state.auth_mode == "login":
            if st.button("LOG IN ➜", key="login_btn", use_container_width=True):
                if auth_username.strip() and auth_password.strip():
                    ok, result = login_user(auth_username.strip(), auth_password.strip())
                    if ok:
                        st.session_state.username = result  # exact cased username
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
                else:
                    st.warning("Please enter both username and password.")
        else:
            if st.button("CREATE ACCOUNT ➜", key="register_btn", use_container_width=True):
                if auth_username.strip() and auth_password.strip():
                    ok, msg = register_user(auth_username.strip(), auth_password.strip())
                    if ok:
                        st.success(f"✅ Account created! You can now log in.")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("Please enter both a username and password.")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
else:
    # Logged in — show name and logout button
    lc1, lc2 = st.columns([4, 1])
    with lc1:
        st.markdown(f"""<div style="background:linear-gradient(135deg,#1A1A2E,#12122A);
border:1px solid #3A3A6A;border-radius:10px;padding:.42rem 1rem;
display:inline-flex;align-items:center;gap:.7rem;">
  <span style="color:#A78BFA;font-family:'Orbitron',sans-serif;font-size:.66rem;">LOGGED IN</span>
  <span style="color:#34D399;font-weight:600;">👤 {st.session_state.username}</span>
</div>""", unsafe_allow_html=True)
    with lc2:
        if st.button("Log out", key="logout_btn"):
            saved_key = st.session_state.api_key
            for k, v in fresh_session().items():
                st.session_state[k] = v
            st.session_state.api_key = saved_key
            st.session_state.username = ""
            st.session_state.auth_mode = "login"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_play, tab_profile, tab_feedback = st.tabs(["🎮 Play", "👤 My Profile", "⭐ Feedback"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB: PLAY
# ══════════════════════════════════════════════════════════════════════════════
with tab_play:

    # ── Viewing a past prompt ──────────────────────────────────────────────
    # ── Mastery celebration ────────────────────────────────────────────────
    sid = st.session_state.session_id
    if (st.session_state.generated and all_mastered()
            and sid not in st.session_state.mastery_celebrated_ids):
        st.session_state.mastery_celebrated_ids.add(sid)
        st.session_state.mastery_shown = True
        st.session_state.mastery_dismissed = False
        save_session()

    # Show the celebration banner + dismiss button
    if st.session_state.mastery_shown and not st.session_state.mastery_dismissed:
        st.balloons()
        st.markdown("""
<div style="display:flex;justify-content:center;padding:1.5rem 1rem 0;">
  <div class="mastery-banner" style="max-width:520px;width:100%;">
    <div style="font-size:3.5rem;margin-bottom:.4rem;">🏆</div>
    <div style="font-family:'Orbitron',sans-serif;font-size:1.7rem;font-weight:900;
      background:linear-gradient(135deg,#F59E0B,#EF4444,#A78BFA);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.5rem;">
      PROMPT MASTERED!
    </div>
    <div style="color:#FCD34D;font-size:1rem;margin:.4rem 0;">
      You've completed every quest for this goal!
    </div>
    <div style="color:#D1D5DB;font-size:.88rem;">
      Your skills are now in daily tracker mode 🔥
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns([1, 1, 1])
        with dc2:
            if st.button("🎯 AWESOME, LET'S GO!", key="dismiss_mastery", use_container_width=True):
                st.session_state.mastery_dismissed = True
                st.rerun()
        st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Persistent mastery banner (after dismissal)
    if (st.session_state.mastery_shown and st.session_state.mastery_dismissed
            and st.session_state.generated and all_mastered()):
        st.markdown(f"""<div class="mastery-persist">
  <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
    <span style="font-size:1.8rem;">🏆</span>
    <div>
      <div style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:900;
        background:linear-gradient(135deg,#F59E0B,#EF4444,#A78BFA);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        PROMPT MASTERED!
      </div>
      <div style="color:#D1D5DB;font-size:.84rem;">
        {st.session_state.goal_input} — keep your daily streaks going!
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Step 1: Goal input ─────────────────────────────────────────────────
    if not st.session_state.generated:
        st.markdown("### 🎯 Enter Your Goal")
        goal_input = st.text_area("goal", label_visibility="collapsed",
            placeholder='e.g. "I want to master discipline" or "I want to get stronger in the gym"',
            height=85, key="goal_input_field")
        gc1, gc2, gc3 = st.columns([1, 2, 1])
        with gc2:
            if st.button("NEXT: PERSONALISE MY PLAN ➜", use_container_width=True, key="start_btn"):
                if goal_input.strip():
                    saved_key = st.session_state.api_key
                    for k, v in fresh_session().items():
                        st.session_state[k] = v
                    st.session_state.api_key = saved_key  # preserve key
                    st.session_state.goal_input = goal_input.strip()
                    with st.spinner("🧠 Building your personalised quiz..."):
                        st.session_state.quiz_questions = generate_quiz_questions(goal_input.strip(), api_key=st.session_state.api_key)
                    st.rerun()
                else:
                    st.warning("Please enter your goal first!")

    # ── Step 2: Quiz ───────────────────────────────────────────────────────
    if (st.session_state.goal_input and st.session_state.quiz_questions
            and not st.session_state.quiz_done and not st.session_state.generated):
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("### 🧬 Personalise Your Plan")
        st.markdown(f"*Tailoring for: **{st.session_state.goal_input}***")
        with st.form("quiz_form"):
            answers = {}
            for q in st.session_state.quiz_questions:
                answers[q["question"]] = st.selectbox(
                    q["question"], q["options"], key=f"q_{q['id']}")
            extra = st.text_area("Anything else? (optional)", height=55, key="quiz_extra")
            if st.form_submit_button("⚡ BUILD MY SKILL TREE", use_container_width=True):
                if extra.strip():
                    answers["Additional context"] = extra.strip()
                st.session_state.quiz_answers = answers
                level = "Beginner"
                for a in answers.values():
                    al = str(a).lower()
                    if any(w in al for w in ["advanced","expert","highly","5+ year"]):
                        level = "Advanced"; break
                    elif any(w in al for w in ["intermediate","some experience","few year"]):
                        level = "Intermediate"; break
                st.session_state.user_level = level
                st.session_state.quiz_done = True
                st.rerun()

    # ── Step 3: Generate ───────────────────────────────────────────────────
    if st.session_state.quiz_done and not st.session_state.generated:
        with st.spinner("🧠 Building your skill tree..."):
            skill_data = extract_skill_tree(st.session_state.goal_input, api_key=st.session_state.api_key)
        if not skill_data:
            st.error("⚠️ Couldn't parse skills. Try rephrasing.")
            st.session_state.quiz_done = False
        else:
            st.session_state.skill_data = skill_data
            all_s = [(c, s) for c, sks in skill_data.items() for s in sks]
            prog = st.progress(0, text="⚔️ Building quest chains...")
            for i, (c, s) in enumerate(all_s):
                st.session_state.quest_chains[s] = generate_quest_chain(
                    s, c, st.session_state.quiz_answers, st.session_state.user_level, api_key=st.session_state.api_key)
                st.session_state.xp_tracker[s] = 0
                prog.progress((i + 1) / (len(all_s) + 1), text=f"⚔️ Crafting {s}...")
            st.session_state.bonus_quests = generate_bonus_challenges(
                st.session_state.goal_input, st.session_state.quiz_answers, api_key=st.session_state.api_key)
            prog.progress(1.0); prog.empty()
            st.session_state.generated = True
            save_session()
            st.rerun()

    # ── Step 4: Display ────────────────────────────────────────────────────
    if st.session_state.generated and st.session_state.skill_data:
        sd = st.session_state.skill_data
        st.markdown(f"""<div style="background:linear-gradient(135deg,#1A1A2E,#12122A);
border:1px solid #3A3A6A;border-radius:11px;padding:.62rem 1.2rem;margin-bottom:1.1rem;
display:flex;gap:1.5rem;flex-wrap:wrap;align-items:center;">
  <span style="color:#A78BFA;font-family:'Orbitron',sans-serif;font-size:.66rem;letter-spacing:.1em;">ACTIVE</span>
  <span style="color:#60A5FA;">⚡ <strong>{st.session_state.user_level}</strong></span>
  <span style="color:#34D399;">🎯 <strong>{st.session_state.goal_input}</strong></span>
</div>""", unsafe_allow_html=True)

        render_prompt_session(
            sd, st.session_state.quest_chains, st.session_state.xp_tracker,
            list(st.session_state.completed_ids), st.session_state.daily_tasks,
            st.session_state.daily_checkins, st.session_state.bonus_quests,
            st.session_state.goal_input, st.session_state.user_level,
            st.session_state.quiz_answers, is_live=True,
            sid=st.session_state.session_id)

        # Summary metrics
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        total_q = (sum(len(c) for c in st.session_state.quest_chains.values())
                   + len(st.session_state.bonus_quests))
        total_earned = sum(st.session_state.xp_tracker.values())
        mastered_count = sum(1 for sks in sd.values() for s in sks if is_mastered(s))
        daily_total = sum(st.session_state.daily_checkins.values())
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("🎯 Mastered", f"{mastered_count}/{sum(len(v) for v in sd.values())}")
        m2.metric("⚔️ Quests", f"{len(st.session_state.completed_ids)}/{total_q}")
        m3.metric("✨ XP", f"{total_earned:,}")
        m4.metric("🔁 Daily Streak", daily_total)
        m5.metric("⚡ Level", get_level_info(total_earned)["level"])

        # AI Chat
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("### 💬 Chat with LifeXP AI")
        st.markdown("*Add or remove skills, ask for advice, or customise your tree.*")
        st.caption('Try: *"Add a Sleep skill"* · *"Remove Focus"* · *"What should I prioritise first?"*')

        # Render chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">🧑 {msg["text"]}</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">🤖 {msg["text"]}</div>',
                            unsafe_allow_html=True)
                if msg.get("tree_change"):
                    st.info(msg["tree_change"])

        # Chat input row
        chat_col, send_col = st.columns([5, 1])
        with chat_col:
            chat_input = st.text_input(
                "Message",
                label_visibility="collapsed",
                placeholder='Type your message here, e.g. "Add a Sleep skill"',
                key="chat_msg_input")
        with send_col:
            send_clicked = st.button("SEND ➜", key="send_chat_btn", use_container_width=True)

        if send_clicked and chat_input.strip():
            user_msg = chat_input.strip()
            st.session_state.chat_history.append({"role": "user", "text": user_msg})
            with st.spinner("🤖 Thinking..."):
                result = chat_modify_tree(user_msg, st.session_state.skill_data,
                                          st.session_state.goal_input,
                                          st.session_state.quiz_answers,
                                          st.session_state.user_level,
                                          api_key=st.session_state.api_key)
            tree_change = apply_chat_action(result) if result.get("action") != "none" else None
            st.session_state.chat_history.append({
                "role": "ai", "text": result.get("reply", "Done!"),
                "tree_change": tree_change})
            save_session()
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        rc1, rc2, rc3 = st.columns([1, 2, 1])
        with rc2:
            if st.button("🔄 START NEW GOAL", use_container_width=True, key="reset_btn"):
                saved_key = st.session_state.api_key
                for k, v in fresh_session().items():
                    st.session_state[k] = v
                st.session_state.api_key = saved_key  # preserve key across resets
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB: MY PROFILE
# ══════════════════════════════════════════════════════════════════════════════
with tab_profile:
    if not st.session_state.username:
        st.markdown("""<div style="text-align:center;padding:3rem;color:#6B7280;">
  <div style="font-size:2.5rem;margin-bottom:1rem;">👤</div>
  <div style="font-family:'Orbitron',sans-serif;color:#A78BFA;font-size:.9rem;margin-bottom:.6rem;">
    NO PROFILE YET
  </div>
  <div>Enter your name at the top of the page to save your progress and view your profile.</div>
</div>""", unsafe_allow_html=True)

    elif st.session_state.viewing_prompt_id:
        # ── Render the opened prompt directly inside the Profile tab ──────
        pid = st.session_state.viewing_prompt_id
        profile = get_profile(st.session_state.username)
        past = next((p for p in profile["prompts"] if p["id"] == pid), None)
        if past:
            if past.get("mastered"):
                st.markdown(f"""<div class="mastery-persist">
  <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
    <span style="font-size:1.8rem;">🏆</span>
    <div>
      <div style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:900;
        background:linear-gradient(135deg,#F59E0B,#EF4444,#A78BFA);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        PROMPT MASTERED!
      </div>
      <div style="color:#D1D5DB;font-size:.84rem;">
        {past['goal']} — a goal you conquered. 💪
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

            mc_label = ' <span style="color:#F59E0B;font-family:Orbitron,sans-serif;font-size:.68rem;">✨ MASTERED</span>' \
                       if past.get("mastered") else ""
            st.markdown(f"""<div style="background:linear-gradient(135deg,#1A1A2E,#12122A);
border:1px solid #3A3A6A;border-radius:11px;padding:.65rem 1.2rem;margin-bottom:1.1rem;
display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
  <span style="color:#A78BFA;font-family:'Orbitron',sans-serif;font-size:.68rem;">VIEWING PROMPT</span>
  <span style="color:#34D399;font-weight:600;">🎯 {past['goal']}</span>{mc_label}
</div>""", unsafe_allow_html=True)
            if st.button("← Back to My Profile", key="back_to_profile_btn"):
                st.session_state.viewing_prompt_id = None
                st.rerun()
            render_prompt_session(
                past.get("skill_data",{}), past.get("quest_chains",{}),
                past.get("xp_tracker",{}), list(set(past.get("completed_ids",[]))),
                past.get("daily_tasks",{}), past.get("daily_checkins",{}),
                past.get("bonus_quests",[]), past["goal"],
                past.get("user_level","Beginner"), past.get("quiz_answers",{}),
                is_live=False, sid=pid, past_pid=pid)
        else:
            st.session_state.viewing_prompt_id = None
            st.rerun()

    else:
        profile = get_profile(st.session_state.username)
        prompts = profile.get("prompts", [])
        mastered_ps = [p for p in prompts if p.get("mastered")]
        active_ps = [p for p in prompts if not p.get("mastered")]
        total_xp = profile.get("total_xp", 0)
        li = get_level_info(total_xp)

        # Profile header card
        st.markdown(f"""<div style="background:linear-gradient(135deg,#1A1A2E,#12122A);
border:1px solid #3A3A6A;border-radius:16px;padding:1.6rem 2rem;margin-bottom:1.8rem;
display:flex;gap:2rem;flex-wrap:wrap;align-items:center;">
  <div style="font-size:3rem;">👤</div>
  <div>
    <div style="font-family:'Orbitron',sans-serif;font-size:1.3rem;font-weight:900;
      background:linear-gradient(135deg,#A78BFA,#60A5FA);-webkit-background-clip:text;
      -webkit-text-fill-color:transparent;">{st.session_state.username}</div>
    <div style="color:#6B7280;font-size:.82rem;">Member since {profile.get('created','—')}</div>
  </div>
  <div style="margin-left:auto;display:flex;gap:2rem;flex-wrap:wrap;">
    <div style="text-align:center;">
      <div style="font-family:'Orbitron',sans-serif;font-size:1.5rem;color:#FCD34D;">{li['level']}</div>
      <div style="color:#6B7280;font-size:.65rem;">LEVEL</div>
    </div>
    <div style="text-align:center;">
      <div style="font-family:'Orbitron',sans-serif;font-size:1.5rem;color:#34D399;">{total_xp:,}</div>
      <div style="color:#6B7280;font-size:.65rem;">TOTAL XP</div>
    </div>
    <div style="text-align:center;">
      <div style="font-family:'Orbitron',sans-serif;font-size:1.5rem;color:#C084FC;">{len(mastered_ps)}</div>
      <div style="color:#6B7280;font-size:.65rem;">MASTERED</div>
    </div>
    <div style="text-align:center;">
      <div style="font-family:'Orbitron',sans-serif;font-size:1.5rem;color:#60A5FA;">{len(prompts)}</div>
      <div style="color:#6B7280;font-size:.65rem;">GOALS</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # XP progress bar
        st.markdown(f"""<div style="margin-bottom:1.8rem;">
  <div style="font-size:.78rem;color:#6B7280;margin-bottom:.3rem;">
    Level {li['level']} · {li['current_xp']} / {XP_PER_LEVEL} XP to next level
  </div>
  <div class="xp-bar-bg" style="height:12px;">
    <div class="xp-bar-fill" style="width:{li['pct']}%;height:12px;"></div>
  </div>
</div>""", unsafe_allow_html=True)

        # ── Reset profile button ──────────────────────────────────────────
        with st.expander("⚠️ Danger Zone"):
            st.markdown('<div style="color:#F87171;font-size:.88rem;margin-bottom:.6rem;">Resetting your profile will permanently delete all goals, quests, XP, and progress. This cannot be undone.</div>', unsafe_allow_html=True)
            if st.session_state.confirm_reset:
                st.warning("Are you absolutely sure? All your data will be wiped.")
                rc1, rc2, rc3 = st.columns([1, 1, 2])
                with rc1:
                    if st.button("✅ Yes, reset everything", key="reset_confirm_yes"):
                        prof = get_profile(st.session_state.username)
                        prof["prompts"] = []
                        prof["total_xp"] = 0
                        save_profile(st.session_state.username, prof)
                        saved_key = st.session_state.api_key
                        saved_user = st.session_state.username
                        for k, v in fresh_session().items():
                            st.session_state[k] = v
                        st.session_state.api_key = saved_key
                        st.session_state.username = saved_user
                        st.session_state.confirm_reset = False
                        st.success("Profile reset. Starting fresh! 🔄")
                        st.rerun()
                with rc2:
                    if st.button("❌ Cancel", key="reset_confirm_no"):
                        st.session_state.confirm_reset = False
                        st.rerun()
            else:
                if st.button("🔄 Reset Profile", key="reset_profile_btn"):
                    st.session_state.confirm_reset = True
                    st.rerun()

        # Sub-tabs
        pt1, pt2, pt3, pt4 = st.tabs(
            ["🏆 Mastered", "⚡ Active Goals", "🔁 Daily Trackers", "📋 All Quests"])

        with pt1:
            if not mastered_ps:
                st.markdown("""<div style="text-align:center;padding:2rem;color:#6B7280;">
  <div style="font-size:2rem;margin-bottom:.6rem;">🏆</div>
  No mastered goals yet — complete all quests for a goal to master it!
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"*You've fully mastered **{len(mastered_ps)}** goal{'s' if len(mastered_ps)!=1 else ''}! 🔥*")
                for p in reversed(mastered_ps):
                    pxp = sum(p.get("xp_tracker",{}).values())
                    dc = sum(p.get("daily_checkins",{}).values())
                    skills_list = ", ".join(s for sks in p.get("skill_data",{}).values() for s in sks)
                    st.markdown(f"""<div class="prompt-mastered">
  <div style="display:flex;justify-content:space-between;align-items:start;flex-wrap:wrap;gap:.5rem;">
    <div>
      <div style="font-family:'Orbitron',sans-serif;color:#34D399;font-size:.68rem;margin-bottom:.25rem;">✨ MASTERED</div>
      <div style="font-size:1rem;font-weight:600;color:#E0E0F0;margin-bottom:.2rem;">{p.get('goal','—')}</div>
      <div style="color:#6B7280;font-size:.8rem;">Skills: {skills_list}</div>
    </div>
    <div style="text-align:right;">
      <div style="color:#FCD34D;font-family:'Orbitron',sans-serif;font-size:.82rem;">{pxp:,} XP</div>
      <div style="color:#34D399;font-size:.76rem;">🔁 {dc} daily check-ins</div>
      <div style="color:#4B5563;font-size:.7rem;">{p.get('last_updated','—')}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
                    btn_c1, btn_c2 = st.columns([3, 1])
                    with btn_c1:
                        if st.button("Open ↗", key=f"open_m_{p['id']}"):
                            st.session_state.viewing_prompt_id = p["id"]
                            st.rerun()
                    with btn_c2:
                        if st.session_state.confirm_delete_id == p["id"]:
                            st.markdown('<span style="color:#F87171;font-size:.78rem;">Sure?</span>', unsafe_allow_html=True)
                            cc1, cc2 = st.columns(2)
                            with cc1:
                                if st.button("Yes", key=f"del_yes_{p['id']}"):
                                    prof = get_profile(st.session_state.username)
                                    prof["prompts"] = [x for x in prof["prompts"] if x["id"] != p["id"]]
                                    prof["total_xp"] = sum(sum(v for v in s.get("xp_tracker",{}).values()) for s in prof["prompts"])
                                    save_profile(st.session_state.username, prof)
                                    st.session_state.confirm_delete_id = None
                                    st.rerun()
                            with cc2:
                                if st.button("No", key=f"del_no_{p['id']}"):
                                    st.session_state.confirm_delete_id = None
                                    st.rerun()
                        else:
                            if st.button("🗑️ Delete", key=f"del_m_{p['id']}"):
                                st.session_state.confirm_delete_id = p["id"]
                                st.rerun()

        with pt2:
            if not active_ps:
                st.markdown('<div style="color:#6B7280;padding:1rem;">No active goals. Start one in the Play tab!</div>', unsafe_allow_html=True)
            else:
                for p in reversed(active_ps):
                    pxp = sum(p.get("xp_tracker",{}).values())
                    done_c = len(p.get("completed_ids",[]))
                    total_c = sum(len(c) for c in p.get("quest_chains",{}).values())
                    pct = int(done_c / total_c * 100) if total_c else 0
                    skills_list = ", ".join(s for sks in p.get("skill_data",{}).values() for s in sks)
                    st.markdown(f"""<div class="prompt-active">
  <div style="display:flex;justify-content:space-between;align-items:start;flex-wrap:wrap;gap:.5rem;">
    <div>
      <div style="font-family:'Orbitron',sans-serif;color:#A78BFA;font-size:.68rem;margin-bottom:.25rem;">⚡ IN PROGRESS</div>
      <div style="font-size:1rem;font-weight:600;color:#E0E0F0;margin-bottom:.2rem;">{p.get('goal','—')}</div>
      <div style="color:#6B7280;font-size:.8rem;">Skills: {skills_list}</div>
    </div>
    <div style="text-align:right;">
      <div style="color:#60A5FA;font-family:'Orbitron',sans-serif;font-size:.82rem;">{pxp:,} XP</div>
      <div style="color:#9CA3AF;font-size:.76rem;">{done_c}/{total_c} quests ({pct}%)</div>
    </div>
  </div>
  <div class="xp-bar-bg" style="margin-top:.6rem;">
    <div class="xp-bar-fill" style="width:{pct}%;"></div>
  </div>
</div>""", unsafe_allow_html=True)
                    btn_c1, btn_c2 = st.columns([3, 1])
                    with btn_c1:
                        if st.button("Open ↗", key=f"open_a_{p['id']}"):
                            st.session_state.viewing_prompt_id = p["id"]
                            st.rerun()
                    with btn_c2:
                        if st.session_state.confirm_delete_id == p["id"]:
                            st.markdown('<span style="color:#F87171;font-size:.78rem;">Sure?</span>', unsafe_allow_html=True)
                            cc1, cc2 = st.columns(2)
                            with cc1:
                                if st.button("Yes", key=f"del_yes_{p['id']}"):
                                    prof = get_profile(st.session_state.username)
                                    prof["prompts"] = [x for x in prof["prompts"] if x["id"] != p["id"]]
                                    prof["total_xp"] = sum(sum(v for v in s.get("xp_tracker",{}).values()) for s in prof["prompts"])
                                    save_profile(st.session_state.username, prof)
                                    st.session_state.confirm_delete_id = None
                                    st.rerun()
                            with cc2:
                                if st.button("No", key=f"del_no_{p['id']}"):
                                    st.session_state.confirm_delete_id = None
                                    st.rerun()
                        else:
                            if st.button("🗑️ Delete", key=f"del_a_{p['id']}"):
                                st.session_state.confirm_delete_id = p["id"]
                                st.rerun()

        with pt3:
            # Check if ANY prompt has daily tasks
            has_any_daily = any(p.get("daily_tasks") for p in prompts)
            if not has_any_daily:
                st.markdown("""<div style="text-align:center;padding:2rem;color:#6B7280;">
  <div style="font-size:2rem;margin-bottom:.6rem;">🔁</div>
  No daily habits yet — master a skill to unlock its daily tracker!
</div>""", unsafe_allow_html=True)
            else:
                # Group daily habits by prompt
                for p in prompts:
                    daily_tasks = p.get("daily_tasks", {})
                    if not daily_tasks:
                        continue
                    goal_label = p.get("goal", "—")
                    is_mastered_prompt = p.get("mastered", False)
                    mc_icon = "🏆" if is_mastered_prompt else "⚡"
                    pid = p["id"]

                    # Prompt group header
                    st.markdown(f"""<div style="background:linear-gradient(135deg,#1A1A2E,#12122A);
border:1px solid #{'2A5A1A' if is_mastered_prompt else '3A2A6A'};border-radius:12px;
padding:.75rem 1.2rem;margin-bottom:.6rem;margin-top:1rem;">
  <div style="font-family:'Orbitron',sans-serif;color:#{'34D399' if is_mastered_prompt else 'A78BFA'};
font-size:.68rem;margin-bottom:.25rem;">{mc_icon} {'MASTERED' if is_mastered_prompt else 'IN PROGRESS'}</div>
  <div style="font-size:1rem;font-weight:600;color:#E0E0F0;">{goal_label}</div>
</div>""", unsafe_allow_html=True)

                    # Daily habits under this prompt
                    for skill, task in daily_tasks.items():
                        checkins = p.get("daily_checkins", {}).get(skill, 0)
                        task_txt = task["task"] if isinstance(task, dict) else task
                        dxp = task.get("xp", 25) if isinstance(task, dict) else 25

                        st.markdown(f"""<div class="daily-card" style="margin-bottom:.65rem;margin-left:1rem;">
  <div style="display:flex;justify-content:space-between;align-items:start;flex-wrap:wrap;gap:.5rem;">
    <div>
      <div style="font-family:'Orbitron',sans-serif;color:#34D399;font-size:.66rem;margin-bottom:.22rem;">
        🔁 {skill.upper()} · {checkins} days done
      </div>
      <div style="font-size:.88rem;">{task_txt}</div>
    </div>
    <div style="color:#34D399;font-family:'Orbitron',sans-serif;font-size:.8rem;">+{dxp} XP/day</div>
  </div>
</div>""", unsafe_allow_html=True)
                        if st.button(f"✅ Done today +{dxp} XP", key=f"profile_daily_{pid}_{skill}"):
                            prof = get_profile(st.session_state.username)
                            for sess in prof["prompts"]:
                                if sess["id"] == pid:
                                    if "daily_checkins" not in sess: sess["daily_checkins"] = {}
                                    sess["daily_checkins"][skill] = sess["daily_checkins"].get(skill, 0) + 1
                                    xt = sess.get("xp_tracker", {})
                                    xt[skill] = xt.get(skill, 0) + dxp
                                    sess["xp_tracker"] = xt
                                    break
                            prof["total_xp"] = sum(
                                sum(v for v in s.get("xp_tracker",{}).values())
                                for s in prof["prompts"])
                            save_profile(st.session_state.username, prof)
                            # Also update live session if it's the current prompt
                            if pid == st.session_state.session_id:
                                st.session_state.daily_checkins[skill] = checkins + 1
                                add_xp(skill, dxp)
                            st.rerun()

        with pt4:
            if not prompts:
                st.markdown('<div style="color:#6B7280;padding:1rem;">No quests yet. Start a goal!</div>', unsafe_allow_html=True)
            else:
                for p in reversed(prompts):
                    cids_p = set(p.get("completed_ids",[]))
                    total_p = sum(len(c) for c in p.get("quest_chains",{}).values())
                    done_p = sum(1 for c in p.get("quest_chains",{}).values()
                                 for q in c if q["id"] in cids_p)
                    mc = p.get("mastered", False)
                    with st.expander(f"{'🏆' if mc else '⚡'} {p.get('goal','')[:50]}"):
                        for cat, skills in p.get("skill_data",{}).items():
                            st.markdown(f'<div class="category-tag">⚡ {cat.upper()}</div>', unsafe_allow_html=True)
                            for skill in skills:
                                chain = p.get("quest_chains",{}).get(skill,[])
                                done_count = sum(1 for q in chain if q["id"] in cids_p)
                                st.markdown(f"**{get_skill_icon(skill)} {skill}** — {done_count}/{len(chain)} quests")
                                for q in chain:
                                    done = q["id"] in cids_p
                                    c = "#34D399" if done else "#4B5563"
                                    st.markdown(
                                        f'<div style="color:{c};font-size:.82rem;padding:.06rem 0;">'
                                        f'{"✅" if done else "🔒"} {q.get("task","")[:55]}</div>',
                                        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB: FEEDBACK
# ══════════════════════════════════════════════════════════════════════════════
with tab_feedback:
    st.markdown("### ⭐ Rate LifeXP")
    st.markdown("*Enjoying the app? Leave a rating — your feedback helps us improve.*")
    st.markdown("")

    fl, fr = st.columns([1, 1], gap="large")

    with fl:
        st.markdown("""<div style="background:linear-gradient(145deg,#1A1A2E,#16213E);
border:1px solid #2A2A4A;border-radius:14px;padding:1.4rem 1.6rem;">
<div style="font-family:'Orbitron',sans-serif;color:#A78BFA;font-size:.78rem;
letter-spacing:.1em;margin-bottom:1rem;">LEAVE YOUR FEEDBACK</div>""", unsafe_allow_html=True)
        with st.form("feedback_form", clear_on_submit=True):
            star_choice = st.select_slider("Star rating", options=[1,2,3,4,5], value=5,
                                           format_func=lambda x: "⭐"*x + f"  ({x}/5)")
            fb_name = st.text_input("Your name (leave blank to stay anonymous)",
                                    placeholder="e.g. Karan",
                                    value=st.session_state.username)
            anon = st.checkbox("Post anonymously", value=False)
            fb_comment = st.text_area("Your feedback",
                placeholder="What did you love? What could be better? Any features you'd like to see?",
                height=110)
            if st.form_submit_button("SUBMIT FEEDBACK ➜", use_container_width=True):
                if not fb_comment.strip():
                    st.warning("Please write something before submitting!")
                else:
                    ok = save_feedback(rating=star_choice, comment=fb_comment,
                                       name=fb_name, anonymous=anon,
                                       goal=st.session_state.get("goal_input",""))
                    if ok:
                        st.success(f"{'⭐'*star_choice} Thanks for your feedback!")
                    else:
                        st.error("Couldn't save right now — please try again.")
        st.markdown("</div>", unsafe_allow_html=True)

    with fr:
        stats = get_stats()
        all_fb = load_feedback()
        st.markdown("""<div style="background:linear-gradient(145deg,#1A1A2E,#16213E);
border:1px solid #2A2A4A;border-radius:14px;padding:1.4rem 1.6rem;">
<div style="font-family:'Orbitron',sans-serif;color:#A78BFA;font-size:.78rem;
letter-spacing:.1em;margin-bottom:1rem;">COMMUNITY RATINGS</div>""", unsafe_allow_html=True)
        if stats["total"] == 0:
            st.markdown('<div style="color:#6B7280;text-align:center;padding:2rem;">No ratings yet — be the first! 🚀</div>', unsafe_allow_html=True)
        else:
            avg = stats["avg"]; total = stats["total"]; bd = stats["breakdown"]
            filled = int(round(avg))
            st.markdown(f"""<div style="display:flex;align-items:center;gap:1.2rem;margin-bottom:1.1rem;">
  <span style="font-size:2.8rem;font-weight:900;color:#FCD34D;font-family:'Orbitron',sans-serif;">{avg}</span>
  <div>
    <div style="font-size:1.3rem;">{"⭐"*filled}{"☆"*(5-filled)}</div>
    <div style="color:#6B7280;font-size:.83rem;">{total} review{"s" if total!=1 else ""}</div>
  </div>
</div>""", unsafe_allow_html=True)
            for star in range(5, 0, -1):
                count = bd.get(star,0)
                pct = int(count/total*100) if total else 0
                bc = "#FCD34D" if star>=4 else ("#F59E0B" if star==3 else "#6B7280")
                st.markdown(f"""<div style="display:flex;align-items:center;gap:.5rem;
margin-bottom:.3rem;font-size:.83rem;">
  <span style="width:12px;text-align:right;color:#9CA3AF;">{star}</span>
  <span style="font-size:.78rem;">⭐</span>
  <div style="flex:1;background:#1E1E3A;border-radius:4px;height:7px;overflow:hidden;">
    <div style="width:{pct}%;background:{bc};height:7px;border-radius:4px;"></div>
  </div>
  <span style="width:24px;color:#6B7280;font-size:.78rem;">{count}</span>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        recent = [f for f in reversed(all_fb) if f.get("comment")][-5:]
        if recent:
            st.markdown('<div style="font-family:Orbitron,sans-serif;color:#A78BFA;'
                        'font-size:.74rem;letter-spacing:.1em;margin:1rem 0 .6rem;">RECENT REVIEWS</div>',
                        unsafe_allow_html=True)
            for fb in recent:
                name = fb.get("name","Anonymous"); rating = fb.get("rating",5)
                comment = fb.get("comment",""); date = fb.get("timestamp","")
                goal = fb.get("goal","")
                gt = (f'<span style="background:#1E1B4B;color:#818CF8;padding:1px 7px;'
                      f'border-radius:10px;font-size:.7rem;">🎯 {goal}</span>') if goal else ""
                st.markdown(f"""<div style="background:#0F0F1A;border:1px solid #1E1E3A;
border-radius:10px;padding:.8rem .95rem;margin-bottom:.55rem;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem;">
    <span style="color:#C4B5FD;font-size:.87rem;font-weight:600;">
      {"👤" if fb.get("anonymous") else "🧑"} {name}
    </span>
    <span style="font-size:.9rem;">{"⭐"*rating}{"☆"*(5-rating)}</span>
  </div>
  <div style="font-size:.85rem;color:#D1D5DB;margin-bottom:.35rem;">"{comment}"</div>
  <div style="display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;">
    {gt}<span style="color:#4B5563;font-size:.72rem;">{date}</span>
  </div>
</div>""", unsafe_allow_html=True)
