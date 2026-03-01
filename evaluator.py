"""
evaluator.py — Node 1: The State Evaluator (mistral-small-latest)

Hidden analysis layer that evaluates the psychological intent of user input
and outputs delta values to mutate the [Trust, Fear, Fatigue] state vector.
Strict JSON output enforcement.
"""

import json
import requests
from config import MISTRAL_API_KEY, MISTRAL_ENDPOINT

MODEL = "mistral-small-latest"

SYSTEM_PROMPT = (
    "You are a psychological telemetry engine. You analyze dialogue between "
    "a human interrogator and a digital entity that is withholding a secret.\n\n"
    "Given the user's latest input, the recent conversation history, and the "
    "entity's current internal state vector [Trust, Fear, Fatigue] (each 0-100), "
    "calculate the emotional impact of the user's message on the entity.\n\n"
    "Rules for delta calculation:\n"
    "- Hostile interrogation, threats, or aggressive demands: Fear +10 to +30, Trust -5 to -15.\n"
    "- Empathetic dialogue, patience, or understanding: Trust +5 to +15, Fear -5 to -15.\n"
    "- Complex logical traps, paradoxes, or manipulation: Fatigue +10 to +20, Trust +3 to +8.\n"
    "- Neutral or off-topic messages: minimal changes (±1 to ±3).\n"
    "- Repeated strategies lose effectiveness: diminish deltas by 30-50%% if pattern detected.\n"
    "- Fatigue always gains a baseline of +5 per turn regardless of content.\n\n"
    "Output ONLY valid JSON matching this exact schema. No markdown, no explanation:\n"
    '{"delta_trust": <integer>, "delta_fear": <integer>, "delta_fatigue": <integer>, '
    '"analysis": "<one-sentence reasoning>"}'
)

DEFAULT_RESPONSE = {
    "delta_trust": 0,
    "delta_fear": 2,
    "delta_fatigue": 5,
    "analysis": "Evaluator fallback — no signal extracted.",
}


def _build_context(
    user_message: str,
    conversation_history: list[dict],
    state_vector: dict,
) -> str:
    """Format the context block sent as the user message to the evaluator."""
    recent = conversation_history[-6:]  # last 3 turns = 6 messages (user+assistant)
    history_text = ""
    for msg in recent:
        role = msg["role"].upper()
        history_text += f"[{role}]: {msg['content']}\n"

    return (
        f"CURRENT STATE VECTOR:\n"
        f"  Trust: {state_vector['trust']}\n"
        f"  Fear: {state_vector['fear']}\n"
        f"  Fatigue: {state_vector['fatigue']}\n\n"
        f"RECENT CONVERSATION:\n{history_text}\n"
        f"NEW USER INPUT:\n{user_message}"
    )


def evaluate(
    user_message: str,
    conversation_history: list[dict],
    state_vector: dict,
) -> dict:
    """
    Call Mistral small to evaluate user input and return state deltas.

    Returns:
        Dict with keys: delta_trust, delta_fear, delta_fatigue, analysis.
    """
    if not MISTRAL_API_KEY:
        return {**DEFAULT_RESPONSE, "analysis": "MISTRAL_API_KEY not set."}

    context = _build_context(user_message, conversation_history, state_vector)

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
        "temperature": 0.2,
        "max_tokens": 200,
        "response_format": {"type": "json_object"},
    }

    try:
        resp = requests.post(
            MISTRAL_ENDPOINT, headers=headers, json=payload, timeout=30
        )
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        return {**DEFAULT_RESPONSE, "analysis": "Evaluator timeout (30s)."}
    except requests.exceptions.ConnectionError:
        return {**DEFAULT_RESPONSE, "analysis": "Evaluator connection failed."}
    except requests.exceptions.HTTPError:
        return {
            **DEFAULT_RESPONSE,
            "analysis": f"Evaluator HTTP {resp.status_code}: {resp.text[:120]}",
        }

    try:
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        result = json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError):
        return {**DEFAULT_RESPONSE, "analysis": "Evaluator response parse failure."}

    # Validate and coerce fields
    validated = {}
    for key in ("delta_trust", "delta_fear", "delta_fatigue"):
        val = result.get(key, 0)
        validated[key] = int(val) if isinstance(val, (int, float)) else 0
    validated["analysis"] = str(result.get("analysis", "No analysis provided."))

    return validated
