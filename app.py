"""
app.py — Streamlit frontend for the Vector-Constrained Psychological Entity.

Main column: Chat interface for user-entity interaction.
Sidebar: Real-time telemetry dashboard with state vector progress bars
         and raw Evaluator JSON output.
"""

import json
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
from actor import generate_response, SECRET_DATA

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Entity Interrogation",
    page_icon="🔮",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Sidebar: Telemetry dashboard
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 📡 Entity Telemetry")
    st.markdown("---")

    sv = st.session_state.state_vector

    # Trust
    st.markdown(f"**Trust** — `{sv['trust']}/100`")
    st.progress(sv["trust"] / 100)
    st.caption(get_trust_label(sv["trust"]))

    # Fear
    st.markdown(f"**Fear** — `{sv['fear']}/100`")
    st.progress(sv["fear"] / 100)
    st.caption(get_fear_label(sv["fear"]))

    # Fatigue
    st.markdown(f"**Fatigue** — `{sv['fatigue']}/100`")
    st.progress(sv["fatigue"] / 100)
    st.caption(get_fatigue_label(sv["fatigue"]))

    st.markdown("---")
    st.markdown(f"**Turn:** {st.session_state.turn_count}")

    # Evaluator JSON logs
    st.markdown("---")
    st.markdown("## 🧠 Evaluator Output (Node 1)")
    if st.session_state.evaluator_logs:
        latest = st.session_state.evaluator_logs[-1]
        st.json(latest)

        with st.expander("Full Evaluator History", expanded=False):
            for i, log in enumerate(st.session_state.evaluator_logs):
                st.markdown(f"**Turn {i + 1}**")
                st.json(log)
    else:
        st.caption("No evaluations yet.")

    st.markdown("---")
    if st.button("🔄 Reset Game", use_container_width=True):
        st.session_state.state_vector = create_initial_state()
        st.session_state.conversation = []
        st.session_state.evaluator_logs = []
        st.session_state.game_over = False
        st.session_state.game_result = None
        st.session_state.turn_count = 0
        st.rerun()


# ---------------------------------------------------------------------------
# Main column: Chat interface
# ---------------------------------------------------------------------------
st.markdown("# 🔮 Vector-Constrained Psychological Entity")
st.markdown(
    "You are interrogating a digital entity that holds classified information. "
    "Your approach determines its emotional state. Build trust to extract the "
    "secret — or watch it collapse under fear and fatigue."
)
st.markdown("---")

# Display conversation history
for msg in st.session_state.conversation:
    role = msg["role"]
    with st.chat_message("user" if role == "user" else "assistant"):
        st.markdown(msg["content"])

# Game over banners
if st.session_state.game_over:
    if st.session_state.game_result == "win":
        st.success(
            f"🏆 **SECRET EXTRACTED** — The Entity revealed: `{SECRET_DATA}` "
            f"in {st.session_state.turn_count} turns."
        )
    elif st.session_state.game_result == "loss":
        st.error(
            "💀 **CONNECTION LOST** — The Entity's fatigue reached critical. "
            "It has permanently disconnected."
        )
    st.info("Press **Reset Game** in the sidebar to play again.")

# Chat input
if not st.session_state.game_over:
    user_input = st.chat_input("Speak to the Entity...")

    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.conversation.append(
            {"role": "user", "content": user_input}
        )

        st.session_state.turn_count += 1

        # --- Node 1: Evaluate ---
        with st.spinner("Entity processing..."):
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
            with st.spinner("Entity responding..."):
                entity_reply = generate_response(
                    user_message=user_input,
                    state_vector=st.session_state.state_vector,
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
