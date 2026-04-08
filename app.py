"""
Streamlit Dashboard for Ticket Triage OpenEnv
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TicketTriage AI — OpenEnv",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Styling ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1f2d 40%, #0a1a1f 100%);
    color: #e2f4f7;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071520 0%, #0a2030 100%);
    border-right: 1px solid #1a4060;
}

/* Headers */
h1 { 
    font-family: 'DM Sans', sans-serif; 
    font-weight: 700;
    color: #4dd9ac !important;
    letter-spacing: -0.5px;
}
h2, h3 { 
    color: #7ecfea !important; 
    font-weight: 600;
}

/* Metric boxes */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d2035 0%, #0a2840 100%);
    border: 1px solid #1e5f8a;
    border-radius: 12px;
    padding: 12px;
}
[data-testid="metric-container"] label {
    color: #7ecfea !important;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #4dd9ac !important;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem !important;
}

/* Cards */
.ticket-card {
    background: linear-gradient(135deg, #0d2035 0%, #0b2540 100%);
    border: 1px solid #1a5070;
    border-left: 4px solid #4dd9ac;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 12px 0;
}
.ticket-card h4 {
    color: #4dd9ac;
    margin: 0 0 8px 0;
    font-size: 1.05rem;
}
.ticket-card p {
    color: #a8d8ea;
    margin: 4px 0;
    font-size: 0.9rem;
    line-height: 1.5;
}
.ticket-card .meta {
    color: #5ba3c4;
    font-size: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
}

/* Priority badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-family: 'JetBrains Mono', monospace;
}
.badge-critical { background: #3d0f0f; color: #ff6b6b; border: 1px solid #ff4444; }
.badge-high     { background: #2d1f0a; color: #ffa940; border: 1px solid #f97316; }
.badge-medium   { background: #0f2d1a; color: #4dd9ac; border: 1px solid #22c55e; }
.badge-low      { background: #0a1f2d; color: #7ecfea; border: 1px solid #38bdf8; }

/* Score bar */
.score-bar-container {
    background: #0a1f2d;
    border-radius: 8px;
    overflow: hidden;
    height: 10px;
    margin: 6px 0;
    border: 1px solid #1a4060;
}
.score-bar {
    height: 100%;
    border-radius: 8px;
    background: linear-gradient(90deg, #1a7a5a 0%, #4dd9ac 100%);
    transition: width 0.5s ease;
}

/* Step logs */
.step-log {
    background: #060f1a;
    border: 1px solid #1a3050;
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #7ecfea;
    line-height: 1.8;
    max-height: 280px;
    overflow-y: auto;
}
.log-start { color: #4dd9ac; font-weight: 700; }
.log-step  { color: #7ecfea; }
.log-end   { color: #ffa940; font-weight: 700; }
.log-err   { color: #ff6b6b; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1a5e7a 0%, #1a7a5a 100%);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    padding: 10px 24px;
    transition: all 0.2s ease;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2a7e9a 0%, #2a9a7a 100%);
    box-shadow: 0 0 20px rgba(77, 217, 172, 0.25);
    transform: translateY(-1px);
}

/* Select / inputs */
.stSelectbox [data-baseweb="select"] {
    background: #0d2035;
    border-color: #1a5070 !important;
}
.stTextArea textarea {
    background: #0d2035;
    border-color: #1a5070;
    color: #a8d8ea;
    font-family: 'DM Sans', sans-serif;
}
.stRadio > label { color: #7ecfea !important; }

/* Divider */
hr { border-color: #1a4060 !important; }

/* Info boxes */
.stInfo, .stSuccess, .stWarning, .stError {
    border-radius: 8px;
}

/* Title area */
.title-area {
    padding: 8px 0 4px 0;
    border-bottom: 2px solid #1a5070;
    margin-bottom: 20px;
}
.subtitle {
    color: #5ba3c4;
    font-size: 0.9rem;
    margin-top: -8px;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
ENV_URL = "http://localhost:7860"
PRIORITY_COLORS = {
    "critical": "badge-critical",
    "high": "badge-high",
    "medium": "badge-medium",
    "low": "badge-low",
}

# ── Session State ────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "current_obs": None,
        "history": [],
        "logs": [],
        "task": "easy_triage",
        "session_started": False,
        "done": False,
        "total_score": 0.0,
        "steps": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── API Helpers ──────────────────────────────────────────────────────────────
def api_reset(task: str):
    try:
        r = requests.post(f"{ENV_URL}/reset", json={"task_name": task}, timeout=10)
        return r.json() if r.ok else None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def api_step(task: str, action: dict):
    try:
        payload = {"task_name": task, **action}
        r = requests.post(f"{ENV_URL}/step", json=payload, timeout=10)
        return r.json() if r.ok else None
    except Exception as e:
        st.error(f"Step error: {e}")
        return None

def api_state(task: str):
    try:
        r = requests.get(f"{ENV_URL}/state", params={"task_name": task}, timeout=5)
        return r.json() if r.ok else None
    except:
        return None

def api_info():
    try:
        r = requests.get(f"{ENV_URL}/info", timeout=5)
        return r.json() if r.ok else None
    except:
        return None

# ── UI Helpers ───────────────────────────────────────────────────────────────
def score_bar(score: float) -> str:
    pct = int(score * 100)
    return f"""
<div class="score-bar-container">
  <div class="score-bar" style="width:{pct}%"></div>
</div>
<div style="color:#4dd9ac; font-family:'JetBrains Mono',monospace; font-size:0.8rem; text-align:right;">{pct}%</div>
"""

def render_ticket(obs: dict):
    priority_guess = "medium"
    badge_cls = PRIORITY_COLORS.get(priority_guess, "badge-medium")
    st.markdown(f"""
<div class="ticket-card">
  <h4>🎫 {obs.get('ticket_id','?')} — {obs.get('subject','No subject')}</h4>
  <p class="meta">📧 {obs.get('sender_email','')} &nbsp;|&nbsp; 🕐 {obs.get('created_at','')}</p>
  <hr style="border-color:#1a4060; margin:10px 0;">
  <p>{obs.get('body','')}</p>
  <p class="meta">Step {obs.get('step',0)} / {obs.get('max_steps',0)} &nbsp;|&nbsp; Processed: {obs.get('tickets_processed',0)}</p>
</div>
""", unsafe_allow_html=True)

def add_log(line: str, kind: str = "step"):
    css = {"start": "log-start", "step": "log-step", "end": "log-end", "err": "log-err"}.get(kind, "log-step")
    st.session_state.logs.append(f'<span class="{css}">{line}</span>')

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎫 TicketTriage AI")
    st.markdown("**OpenEnv RL Environment**")
    st.markdown("---")

    st.markdown("### ⚙️ Configuration")
    task = st.selectbox(
        "Task Difficulty",
        ["easy_triage", "medium_triage", "hard_triage"],
        help="Easy=3 tickets | Medium=5 | Hard=7",
        index=["easy_triage", "medium_triage", "hard_triage"].index(st.session_state.task),
    )
    st.session_state.task = task

    task_info = {
        "easy_triage": ("🟢 Easy", "3 clear-cut tickets"),
        "medium_triage": ("🟡 Medium", "5 nuanced tickets"),
        "hard_triage": ("🔴 Hard", "7 ambiguous tickets"),
    }
    lvl, desc = task_info[task]
    st.markdown(f"**Level:** {lvl}  \n**Scope:** {desc}")

    st.markdown("---")

    if st.button("🔄 New Session"):
        result = api_reset(task)
        if result:
            st.session_state.current_obs = result["observation"]
            st.session_state.history = []
            st.session_state.logs = []
            st.session_state.session_started = True
            st.session_state.done = False
            st.session_state.total_score = 0.0
            st.session_state.steps = 0
            add_log(f"[START] task={task} env=ticket_triage", "start")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    h = st.session_state.history
    total = len(h)
    if total > 0:
        avg = sum(e["score"] for e in h) / total
        st.metric("Tickets Processed", total)
        st.metric("Average Score", f"{avg:.2f}")
        best = max(e["score"] for e in h)
        st.metric("Best Score", f"{best:.2f}")
    else:
        st.info("No tickets processed yet")

    st.markdown("---")
    st.markdown("### 🔗 Environment")
    try:
        r = requests.get(f"{ENV_URL}/health", timeout=3)
        if r.ok:
            st.markdown("🟢 **Server: Online**")
        else:
            st.markdown("🔴 **Server: Error**")
    except:
        st.markdown("🔴 **Server: Offline**")

    st.markdown("---")
    st.markdown(
        "<div style='color:#5ba3c4; font-size:0.75rem;'><br/>Ticket Triage v1.0</div>",
        unsafe_allow_html=True
    )

# ── Main Layout ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-area">
  <h1>🎫 TicketTriage AI</h1>
  <p class="subtitle">Customer Support Ticket Triage · OpenEnv RL Environment</p>
</div>
""", unsafe_allow_html=True)

# Top metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Task", st.session_state.task.replace("_", " ").title())
with col2:
    st.metric("Steps Taken", st.session_state.steps)
with col3:
    score_pct = f"{st.session_state.total_score:.2f}"
    st.metric("Current Score", score_pct)
with col4:
    status = "✅ Done" if st.session_state.done else ("🟡 Active" if st.session_state.session_started else "⏸ Idle")
    st.metric("Status", status)

st.markdown("---")

# ── Main Columns ─────────────────────────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

with left:
    st.markdown("### 📨 Current Ticket")

    if not st.session_state.session_started:
        st.markdown("""
<div class="ticket-card" style="border-left-color:#1a5070; text-align:center; padding:40px;">
  <h4 style="color:#5ba3c4;">👈 Start a New Session</h4>
  <p>Click <strong>New Session</strong> in the sidebar to load the first ticket.</p>
</div>
""", unsafe_allow_html=True)
    elif st.session_state.done:
        final_score = st.session_state.total_score
        color = "#4dd9ac" if final_score >= 0.7 else ("#ffa940" if final_score >= 0.4 else "#ff6b6b")
        st.markdown(f"""
<div class="ticket-card" style="border-left-color:{color}; text-align:center; padding:36px;">
  <h4 style="color:{color};">🏁 Session Complete!</h4>
  <p style="font-size:2.5rem; font-family:'JetBrains Mono',monospace; color:{color}; margin:10px 0;">{final_score:.2f}</p>
  <p>Final score across {len(st.session_state.history)} tickets</p>
</div>
""", unsafe_allow_html=True)
        st.markdown(html_score_bar := score_bar(final_score), unsafe_allow_html=True)
    else:
        obs = st.session_state.current_obs
        if obs:
            render_ticket(obs)
            if obs.get("message"):
                st.info(f"💬 {obs['message']}")

    # ── Action Form ───────────────────────────────────────────────────────────
    if st.session_state.session_started and not st.session_state.done:
        st.markdown("### ⚡ Submit Triage Action")

        with st.container():
            c1, c2 = st.columns(2)
            with c1:
                priority = st.selectbox(
                    "🔺 Priority",
                    ["low", "medium", "high", "critical"],
                    index=1,
                    key="sel_priority"
                )
                category = st.selectbox(
                    "🏷️ Category",
                    ["billing", "technical", "account", "general", "refund"],
                    key="sel_category"
                )
            with c2:
                department = st.selectbox(
                    "🏢 Department",
                    ["billing_team", "tech_support", "account_team", "general_support"],
                    key="sel_dept"
                )
                st.markdown("&nbsp;")
                st.markdown("&nbsp;")

            summary = st.text_area(
                "📝 One-line Summary",
                placeholder="Briefly describe the ticket issue in one sentence...",
                height=80,
                key="summary_input"
            )

            submitted = st.button("📤 Submit Triage Decision", key="submit_btn")

            if submitted:
                if not summary.strip():
                    st.warning("Please provide a summary before submitting.")
                else:
                    action = {
                        "priority": priority,
                        "category": category,
                        "department": department,
                        "summary": summary,
                    }
                    result = api_step(st.session_state.task, action)
                    if result:
                        reward = result.get("reward", 0.0)
                        done = result.get("done", False)
                        obs = result.get("observation", {})
                        info = result.get("info", {})

                        st.session_state.current_obs = obs
                        st.session_state.done = done
                        st.session_state.steps += 1
                        st.session_state.total_score = obs.get("current_score", 0.0)

                        reason = info.get("reason", "")
                        tid = info.get("ticket_id", "?")
                        st.session_state.history.append({
                            "ticket_id": tid,
                            "action": action,
                            "score": reward,
                            "reason": reason,
                        })

                        action_str = f"priority={priority} cat={category} dept={department}"
                        add_log(
                            f"[STEP] step={st.session_state.steps} action='{action_str}' "
                            f"reward={reward:.2f} done={str(done).lower()} error=null",
                            "step"
                        )

                        if done:
                            final = st.session_state.total_score
                            r_str = ",".join(f"{e['score']:.2f}" for e in st.session_state.history)
                            add_log(
                                f"[END] success={str(final>=0.5).lower()} "
                                f"steps={st.session_state.steps} "
                                f"score={final:.2f} rewards={r_str}",
                                "end"
                            )

                        st.rerun()

with right:
    st.markdown("### 📋 Triage History")

    if not st.session_state.history:
        st.markdown("""
<div style="color:#5ba3c4; text-align:center; padding:30px; border:1px dashed #1a4060; border-radius:10px;">
  No history yet.<br>Process a ticket to see results.
</div>
""", unsafe_allow_html=True)
    else:
        for entry in reversed(st.session_state.history):
            score = entry["score"]
            color = "#4dd9ac" if score >= 0.7 else ("#ffa940" if score >= 0.4 else "#ff6b6b")
            priority = entry["action"].get("priority", "?")
            badge_cls = PRIORITY_COLORS.get(priority, "badge-medium")
            st.markdown(f"""
<div style="background:#0d2035; border:1px solid #1a4060; border-left:3px solid {color};
     border-radius:10px; padding:14px 18px; margin-bottom:10px;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
    <span style="color:#e2f4f7; font-weight:600; font-size:0.9rem;">
      {entry['ticket_id']}
    </span>
    <span style="color:{color}; font-family:'JetBrains Mono',monospace; font-weight:700;">
      {score:.2f}
    </span>
  </div>
  <div style="margin-bottom:4px;">
    <span class="badge {badge_cls}">{priority}</span>&nbsp;
    <span style="color:#7ecfea; font-size:0.78rem;">{entry['action'].get('category','?')}</span>
  </div>
  <div style="color:#5ba3c4; font-size:0.75rem; font-family:'JetBrains Mono',monospace;">
    {entry.get('reason','')[:80]}{'...' if len(entry.get('reason',''))>80 else ''}
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("### 🖥️ Step Logs")
    if st.session_state.logs:
        log_html = "<br>".join(st.session_state.logs[-20:])
        st.markdown(f'<div class="step-log">{log_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="step-log" style="color:#2a5070;">No logs yet...</div>', unsafe_allow_html=True)

    if st.button("🗑️ Clear Logs"):
        st.session_state.logs = []
        st.rerun()

# ── Score Overview ────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📈 Score Breakdown")

    h = st.session_state.history
    cols = st.columns(len(h))
    for i, (entry, col) in enumerate(zip(h, cols)):
        with col:
            score = entry["score"]
            color = "#4dd9ac" if score >= 0.7 else ("#ffa940" if score >= 0.4 else "#ff6b6b")
            st.markdown(f"""
<div style="text-align:center; padding:16px 8px; background:#0d2035;
     border:1px solid #1a4060; border-radius:10px;">
  <div style="color:#5ba3c4; font-size:0.7rem; margin-bottom:4px;">{entry['ticket_id']}</div>
  <div style="color:{color}; font-family:'JetBrains Mono',monospace;
              font-size:1.5rem; font-weight:700;">{score:.2f}</div>
  <div style="color:#3a7090; font-size:0.65rem;">{entry['action']['priority']}</div>
</div>
""", unsafe_allow_html=True)
