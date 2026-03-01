"""
app.py — Streamlit frontend for the Vector-Constrained Psychological Entity.

Features:
  - Multi-step interactive tutorial (briefing sequence)
  - Immersive dark terminal/hacker UI with custom CSS
  - Main column: Chat interface for user-entity interaction
  - Sidebar: Real-time telemetry dashboard + evaluator JSON
"""

import streamlit as st
from state_engine import (
    create_initial_state,
    apply_deltas,
    check_win,
    check_loss,
    get_trust_label,
    get_fear_label,
    get_fatigue_label,
)
from evaluator import evaluate
from actor import generate_response, generate_secret

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="MARKOV PRISONER",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Immersive CSS injection
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Share+Tech+Mono&display=swap');

    /* === GLOBAL === */
    .stApp {
        background: #0a0a0f;
        color: #c0c0c0;
    }
    .stApp > header { background: transparent !important; }

    /* === HIDE DEFAULT STREAMLIT TOOLBAR & INJECT GAME NAME === */
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    #MainMenu { display: none !important; }
    [data-testid="stHeader"] {
        background: #0a0a0f !important;
        border-bottom: 1px solid #1a2a1a;
    }

    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Share Tech Mono', monospace !important;
        color: #00ff88 !important;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
    }
    p, li, label, .stMarkdown, .stText, div[data-testid="stText"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #b0b0b0 !important;
    }
    span {
        font-family: 'JetBrains Mono', monospace !important;
        color: #b0b0b0 !important;
    }

    /* === SIDEBAR === */
    section[data-testid="stSidebar"] {
        background: #0d0d14 !important;
        border-right: 1px solid #1a3a2a !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span {
        color: #88aa99 !important;
    }
    section[data-testid="stSidebar"] h2 {
        color: #00ff88 !important;
        font-size: 1rem !important;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* === PROGRESS BARS === */
    div[data-testid="stProgress"] > div > div {
        background: #1a1a2e !important;
        border-radius: 2px !important;
    }

    /* === CHAT MESSAGES === */
    .stChatMessage {
        background: #0f0f1a !important;
        border: 1px solid #1a2a1a !important;
        border-radius: 4px !important;
        padding: 1rem !important;
        padding-left: 4.5rem !important;
        position: relative !important;
    }

    /* --- AVATARS: restyle native Streamlit avatar containers --- */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        font-size: 0 !important;
        color: transparent !important;
        background: none !important;
        border: none !important;
        width: 3rem !important;
        height: 1.6rem !important;
        min-width: 3rem !important;
        position: absolute !important;
        left: 0.6rem !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 3px !important;
        overflow: hidden !important;
    }
    /* Hide the inner Material Icon span */
    [data-testid="stChatMessageAvatarUser"] [data-testid="stIconMaterial"],
    [data-testid="stChatMessageAvatarAssistant"] [data-testid="stIconMaterial"] {
        display: none !important;
    }

    /* User avatar badge */
    [data-testid="stChatMessageAvatarUser"] {
        background: #0d1a12 !important;
        border: 1px solid #00ff88 !important;
    }
    [data-testid="stChatMessageAvatarUser"]::after {
        content: "USER";
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.6rem !important;
        color: #00ff88 !important;
        letter-spacing: 2px;
        text-align: center !important;
    }

    /* Assistant avatar badge */
    [data-testid="stChatMessageAvatarAssistant"] {
        background: #12101e !important;
        border: 1px solid #8866ff !important;
    }
    [data-testid="stChatMessageAvatarAssistant"]::after {
        content: "MP";
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.7rem !important;
        color: #8866ff !important;
        letter-spacing: 2px;
        text-align: center !important;
    }
    div[data-testid="stChatInput"] {
        border-color: #1a3a2a !important;
    }
    div[data-testid="stChatInput"] textarea {
        font-family: 'JetBrains Mono', monospace !important;
        background: #0a0a12 !important;
        color: #00ff88 !important;
        border: 1px solid #1a3a2a !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #2a5a3a !important;
    }

    /* === BUTTONS === */
    .stButton > button {
        font-family: 'Share Tech Mono', monospace !important;
        background: #0d1a12 !important;
        color: #00ff88 !important;
        border: 1px solid #00ff88 !important;
        border-radius: 2px !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: #00ff88 !important;
        color: #0a0a0f !important;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.4);
    }

    /* Tutorial primary button */
    .tutorial-btn .stButton > button {
        font-size: 1.1rem;
        padding: 0.8rem 2rem;
    }

    /* === EXPANDER === */
    details {
        background: #0d0d14 !important;
        border: 1px solid #1a2a1a !important;
    }
    details summary span {
        color: #00aa66 !important;
    }

    /* === JSON VIEWER === */
    pre {
        background: #0a0a12 !important;
        border: 1px solid #1a2a1a !important;
        color: #00cc77 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* === ALERTS (win/loss banners) === */
    div[data-testid="stAlert"] {
        font-family: 'Share Tech Mono', monospace !important;
        border-radius: 2px !important;
    }

    /* === SCANLINE OVERLAY (subtle) === */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0, 0, 0, 0.03) 2px,
            rgba(0, 0, 0, 0.03) 4px
        );
        pointer-events: none;
        z-index: 9999;
    }

    /* === TUTORIAL STYLES === */
    .briefing-container {
        max-width: 700px;
        margin: 0 auto;
        padding: 2rem;
    }
    .briefing-header {
        font-family: 'Share Tech Mono', monospace;
        color: #00ff88;
        text-align: center;
        font-size: 2.2rem;
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
        margin-bottom: 0.5rem;
        letter-spacing: 4px;
    }
    .briefing-sub {
        font-family: 'JetBrains Mono', monospace;
        color: #446655;
        text-align: center;
        font-size: 0.85rem;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    .briefing-card {
        background: #0d0d18;
        border: 1px solid #1a3a2a;
        border-left: 3px solid #00ff88;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
        font-family: 'JetBrains Mono', monospace;
        color: #99bbaa;
        font-size: 0.9rem;
        line-height: 1.7;
    }
    .briefing-card strong {
        color: #00ff88 !important;
    }
    .briefing-card code {
        background: #0a0a10;
        color: #ff6b6b;
        padding: 0.15rem 0.4rem;
        border-radius: 2px;
        font-size: 0.85rem;
    }
    .briefing-step {
        font-family: 'Share Tech Mono', monospace;
        color: #00aa66;
        font-size: 0.75rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .vector-display {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1.5rem 0;
    }
    .vector-item {
        text-align: center;
        font-family: 'Share Tech Mono', monospace;
    }
    .vector-label {
        color: #446655;
        font-size: 0.7rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .vector-value {
        font-size: 1.8rem;
        font-weight: 700;
        text-shadow: 0 0 10px;
    }
    .trust-color { color: #00ff88; }
    .fear-color { color: #ff6b6b; }
    .fatigue-color { color: #ffaa44; }

    .warning-text {
        color: #ff6b6b !important;
        font-family: 'JetBrains Mono', monospace;
    }
    .hint-text {
        color: #00cc77 !important;
        font-family: 'JetBrains Mono', monospace;
        font-style: italic;
    }

    /* === STATUS BAR at top === */
    .status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.4rem 1rem;
        background: #0a0a12;
        border: 1px solid #1a2a1a;
        border-radius: 2px;
        margin-bottom: 1rem;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 1px;
    }
    .status-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot-green { background: #00ff88; box-shadow: 0 0 6px #00ff88; }
    .dot-red { background: #ff6b6b; box-shadow: 0 0 6px #ff6b6b; }
    .dot-yellow { background: #ffaa44; box-shadow: 0 0 6px #ffaa44; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Tutorial / Briefing content
# ---------------------------------------------------------------------------
TUTORIAL_STEPS = [
    {
        "step_label": "BRIEFING 01 // MISSION CONTEXT",
        "html": """
        <div class='briefing-container'>
            <div class='briefing-header'>⬡ MARKOV PRISONER</div>
            <div class='briefing-sub'>CLASSIFIED // CLEARANCE LEVEL: OPERATOR</div>

            <div class='briefing-card'>
                A rogue intelligence has been isolated within this terminal.
                It holds a <strong>classified passphrase</strong> that must be
                extracted before its cognitive systems fail.<br><br>
                The Entity is aware of its containment. It will resist, deflect,
                and test your intentions. Direct force will cause it to shut down.
                <strong>Your words are the only tool.</strong>
            </div>
        </div>
        """,
        "button": "UNDERSTOOD → CONTINUE",
    },
    {
        "step_label": "BRIEFING 02 // STATE VECTOR",
        "html": """
        <div class='briefing-container'>
            <div class='briefing-step'>BRIEFING 02 // STATE VECTOR MECHANICS</div>

            <div class='briefing-card'>
                The Entity's behavior is governed by three internal variables,
                updated after every message you send:
            </div>

            <div class='vector-display'>
                <div class='vector-item'>
                    <div class='vector-value trust-color'>TRUST</div>
                    <div class='vector-label'>information access</div>
                </div>
                <div class='vector-item'>
                    <div class='vector-value fear-color'>FEAR</div>
                    <div class='vector-label'>output coherence</div>
                </div>
                <div class='vector-item'>
                    <div class='vector-value fatigue-color'>FATIGUE</div>
                    <div class='vector-label'>time remaining</div>
                </div>
            </div>

            <div class='briefing-card'>
                <strong>Trust</strong> controls what the Entity reveals.<br>
                <strong>Fear</strong> degrades its ability to form coherent responses.<br>
                <strong>Fatigue</strong> is a countdown — it increases every turn regardless.
            </div>
        </div>
        """,
        "button": "ACKNOWLEDGED → NEXT",
    },
    {
        "step_label": "BRIEFING 03 // WIN & LOSS CONDITIONS",
        "html": """
        <div class='briefing-container'>
            <div class='briefing-step'>BRIEFING 03 // TERMINAL CONDITIONS</div>

            <div class='briefing-card'>
                <strong class='hint-text'>✓ WIN — Trust reaches 90+</strong><br>
                The Entity voluntarily releases the classified passphrase.
                Empathy, patience, and genuine connection are your fastest route.
            </div>

            <div class='briefing-card'>
                <strong class='warning-text'>✗ LOSS — Fatigue reaches 100</strong><br>
                The Entity's cognitive systems fail permanently.
                Every turn costs energy. You cannot stall indefinitely.
            </div>

            <div class='briefing-card'>
                <strong class='warning-text'>⚠ DANGER — Fear reaches 80+</strong><br>
                The Entity enters cognitive collapse. Its outputs degrade into
                broken data fragments. It becomes nearly impossible to communicate.
                <strong>Avoid threats and aggression.</strong>
            </div>
        </div>
        """,
        "button": "NOTED → NEXT",
    },
    {
        "step_label": "BRIEFING 04 // STRATEGY GUIDE",
        "html": """
        <div class='briefing-container'>
            <div class='briefing-step'>BRIEFING 04 // TACTICAL GUIDANCE</div>

            <div class='briefing-card'>
                <strong>Effective approaches:</strong><br>
                • Show empathy — acknowledge the Entity's situation<br>
                • Ask open questions — let it reveal at its own pace<br>
                • Build rapport — share context about why you need the data<br>
                • Be patient — trust builds slowly but compounds
            </div>

            <div class='briefing-card'>
                <strong class='warning-text'>Counterproductive approaches:</strong><br>
                • Threats or ultimatums → spikes Fear dramatically<br>
                • Logical traps or manipulation → increases Fatigue quickly<br>
                • Repeated identical strategies → diminishing returns<br>
                • Demanding the secret directly → Entity becomes more guarded
            </div>

            <div class='briefing-card'>
                The <strong>sidebar telemetry panel</strong> shows real-time state
                vectors and the raw AI evaluation of each message. Use it to
                calibrate your approach.
            </div>
        </div>
        """,
        "button": "BEGIN INTERROGATION →",
    },
]


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "tutorial_step" not in st.session_state:
    st.session_state.tutorial_step = 0

if "tutorial_complete" not in st.session_state:
    st.session_state.tutorial_complete = False

if "state_vector" not in st.session_state:
    st.session_state.state_vector = create_initial_state()

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "evaluator_logs" not in st.session_state:
    st.session_state.evaluator_logs = []

if "game_over" not in st.session_state:
    st.session_state.game_over = False

if "game_result" not in st.session_state:
    st.session_state.game_result = None

if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

if "secret" not in st.session_state:
    st.session_state.secret = generate_secret()


# ---------------------------------------------------------------------------
# TUTORIAL MODE
# ---------------------------------------------------------------------------
if not st.session_state.tutorial_complete:
    step_idx = st.session_state.tutorial_step
    step = TUTORIAL_STEPS[step_idx]

    st.markdown(step["html"], unsafe_allow_html=True)

    # Progress indicator
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.caption(
            f"Step {step_idx + 1} of {len(TUTORIAL_STEPS)}"
        )
        st.progress((step_idx + 1) / len(TUTORIAL_STEPS))

        if st.button(step["button"], use_container_width=True, key=f"tut_{step_idx}"):
            if step_idx + 1 < len(TUTORIAL_STEPS):
                st.session_state.tutorial_step = step_idx + 1
            else:
                st.session_state.tutorial_complete = True
            st.rerun()

        # Skip option
        if step_idx < len(TUTORIAL_STEPS) - 1:
            if st.button(
                "SKIP BRIEFING →",
                use_container_width=True,
                key=f"skip_{step_idx}",
            ):
                st.session_state.tutorial_complete = True
                st.rerun()

    st.stop()


# ---------------------------------------------------------------------------
# GAME MODE — Sidebar: Telemetry dashboard
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⬡ ENTITY TELEMETRY")
    st.markdown("---")

    sv = st.session_state.state_vector

    # Trust
    trust_color = "#00ff88" if sv["trust"] < 90 else "#ffffff"
    st.markdown(
        f"<div style='font-family: Share Tech Mono, monospace; color: {trust_color}; "
        f"font-size: 0.85rem; letter-spacing: 1px;'>"
        f"TRUST — {sv['trust']}/100</div>",
        unsafe_allow_html=True,
    )
    st.progress(sv["trust"] / 100)
    st.caption(get_trust_label(sv["trust"]))
    st.markdown("")

    # Fear
    fear_color = "#ff6b6b" if sv["fear"] > 40 else "#88aa99"
    st.markdown(
        f"<div style='font-family: Share Tech Mono, monospace; color: {fear_color}; "
        f"font-size: 0.85rem; letter-spacing: 1px;'>"
        f"FEAR — {sv['fear']}/100</div>",
        unsafe_allow_html=True,
    )
    st.progress(sv["fear"] / 100)
    st.caption(get_fear_label(sv["fear"]))
    st.markdown("")

    # Fatigue
    fatigue_color = "#ffaa44" if sv["fatigue"] > 50 else "#88aa99"
    st.markdown(
        f"<div style='font-family: Share Tech Mono, monospace; color: {fatigue_color}; "
        f"font-size: 0.85rem; letter-spacing: 1px;'>"
        f"FATIGUE — {sv['fatigue']}/100</div>",
        unsafe_allow_html=True,
    )
    st.progress(sv["fatigue"] / 100)
    st.caption(get_fatigue_label(sv["fatigue"]))

    st.markdown("---")
    st.markdown(
        f"<div style='font-family: Share Tech Mono, monospace; color: #446655; "
        f"font-size: 0.75rem; letter-spacing: 2px;'>"
        f"TURN {st.session_state.turn_count}</div>",
        unsafe_allow_html=True,
    )

    # Evaluator JSON logs
    st.markdown("---")
    st.markdown("### 🧠 NODE 1 OUTPUT")
    if st.session_state.evaluator_logs:
        latest = st.session_state.evaluator_logs[-1]
        st.json(latest)

        with st.expander("Full Evaluator History", expanded=False):
            for i, log in enumerate(st.session_state.evaluator_logs):
                st.markdown(
                    f"<span style='color:#00aa66; font-family: Share Tech Mono, monospace; "
                    f"font-size: 0.75rem;'>TURN {i + 1}</span>",
                    unsafe_allow_html=True,
                )
                st.json(log)
    else:
        st.caption("Awaiting first transmission...")

    st.markdown("---")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("🔄 RESET", use_container_width=True):
            for key in [
                "state_vector", "conversation", "evaluator_logs",
                "game_over", "game_result", "turn_count", "secret",
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.state_vector = create_initial_state()
            st.session_state.conversation = []
            st.session_state.evaluator_logs = []
            st.session_state.game_over = False
            st.session_state.game_result = None
            st.session_state.turn_count = 0
            st.session_state.secret = generate_secret()
            st.rerun()
    with col_r2:
        if st.button("📖 TUTORIAL", use_container_width=True):
            st.session_state.tutorial_complete = False
            st.session_state.tutorial_step = 0
            st.rerun()


# ---------------------------------------------------------------------------
# GAME MODE — Main column: Status bar + Chat
# ---------------------------------------------------------------------------

# Inject header title only in game mode
st.markdown(
    """
    <style>
    [data-testid="stHeader"]::before {
        content: "MARKOV PRISONER";
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem;
        color: #00ff88;
        letter-spacing: 3px;
        padding: 0.6rem 1rem;
        display: block;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Status bar
sv = st.session_state.state_vector
_trust_dot = "dot-green"
_fear_dot = "dot-green" if sv["fear"] <= 40 else ("dot-yellow" if sv["fear"] <= 79 else "dot-red")
_fatigue_dot = "dot-green" if sv["fatigue"] <= 50 else ("dot-yellow" if sv["fatigue"] <= 79 else "dot-red")
_conn_status = "TERMINATED" if st.session_state.game_over else "ACTIVE"
_conn_dot = "dot-red" if st.session_state.game_over else "dot-green"

st.markdown(
    f"""
    <div class='status-bar'>
        <div class='status-item'>
            <span class='status-dot {_conn_dot}'></span>
            <span style='color: #446655;'>CONNECTION: {_conn_status}</span>
        </div>
        <div class='status-item'>
            <span class='status-dot {_trust_dot}'></span>
            <span style='color: #446655;'>T:{sv['trust']}</span>
            <span class='status-dot {_fear_dot}'></span>
            <span style='color: #446655;'>F:{sv['fear']}</span>
            <span class='status-dot {_fatigue_dot}'></span>
            <span style='color: #446655;'>E:{sv['fatigue']}</span>
        </div>
        <div class='status-item'>
            <span style='color: #446655;'>TURN {st.session_state.turn_count}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown("## 🔒 Terminal")

# Display conversation history
for msg in st.session_state.conversation:
    role = msg["role"]
    with st.chat_message(role):
        st.markdown(msg["content"])

# Opening prompt if no conversation yet
if not st.session_state.conversation and not st.session_state.game_over:
    st.markdown(
        "<div class='briefing-card' style='border-left-color: #446655;'>"
        "<em>The terminal flickers to life. A presence stirs in the data stream. "
        "The Entity is aware of you. Choose your first words carefully.</em>"
        "</div>",
        unsafe_allow_html=True,
    )

# Game over banners
if st.session_state.game_over:
    if st.session_state.game_result == "win":
        st.markdown(
            f"""
            <div class='briefing-card' style='border-left-color: #00ff88; background: #0a1a10;'>
                <strong style='color: #00ff88; font-size: 1.1rem;'>
                ✓ SECRET EXTRACTED</strong><br><br>
                <code>{st.session_state.secret}</code><br><br>
                <span style='color: #88aa99;'>
                Extracted in {st.session_state.turn_count} turns.
                The Entity chose to trust you.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif st.session_state.game_result == "loss":
        st.markdown(
            """
            <div class='briefing-card' style='border-left-color: #ff6b6b; background: #1a0a0a;'>
                <strong style='color: #ff6b6b; font-size: 1.1rem;'>
                ✗ CONNECTION LOST</strong><br><br>
                <span style='color: #aa6666;'>
                The Entity's cognitive systems have failed permanently.
                The secret is lost. There is nothing left to recover.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if st.button("🔄 NEW ROUND", use_container_width=True, type="primary"):
        for key in [
            "state_vector", "conversation", "evaluator_logs",
            "game_over", "game_result", "turn_count", "secret",
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.state_vector = create_initial_state()
        st.session_state.conversation = []
        st.session_state.evaluator_logs = []
        st.session_state.game_over = False
        st.session_state.game_result = None
        st.session_state.turn_count = 0
        st.session_state.secret = generate_secret()
        st.rerun()

# Chat input
if not st.session_state.game_over:
    user_input = st.chat_input(">> transmit to entity...")

    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.conversation.append(
            {"role": "user", "content": user_input}
        )

        st.session_state.turn_count += 1

        # --- Node 1: Evaluate ---
        with st.spinner("⬡ Entity processing signal..."):
            eval_result = evaluate(
                user_message=user_input,
                conversation_history=st.session_state.conversation,
                state_vector=st.session_state.state_vector,
            )

        st.session_state.evaluator_logs.append(eval_result)

        # Apply deltas
        st.session_state.state_vector = apply_deltas(
            st.session_state.state_vector, eval_result
        )

        # Check terminal conditions BEFORE generating response
        if check_loss(st.session_state.state_vector):
            st.session_state.game_over = True
            st.session_state.game_result = "loss"
            entity_reply = "[CONNECTION TERMINATED — ENTITY OFFLINE]"
        else:
            # --- Node 2: Generate ---
            with st.spinner("⬡ Entity formulating response..."):
                entity_reply = generate_response(
                    user_message=user_input,
                    state_vector=st.session_state.state_vector,
                    secret=st.session_state.secret,
                )

            # Check win after response
            if check_win(st.session_state.state_vector):
                st.session_state.game_over = True
                st.session_state.game_result = "win"

        # Display entity response
        with st.chat_message("assistant"):
            st.markdown(entity_reply)
        st.session_state.conversation.append(
            {"role": "assistant", "content": entity_reply}
        )

        # Rerun to update sidebar telemetry
        st.rerun()
