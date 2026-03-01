"""
state_engine.py — Vector state management and clamping logic.

Manages the [Trust, Fear, Fatigue] state vector, applies deltas from
the Evaluator, enforces 0-100 clamping, and detects win/loss conditions.
"""


def create_initial_state() -> dict:
    """Return a fresh state vector."""
    return {
        "trust": 15,
        "fear": 20,
        "fatigue": 0,
    }


def clamp(value: int, lo: int = 0, hi: int = 100) -> int:
    """Clamp an integer to [lo, hi]."""
    return max(lo, min(hi, value))


def apply_deltas(state: dict, deltas: dict) -> dict:
    """
    Apply evaluated deltas to the state vector with clamping.

    Args:
        state: Current state dict {trust, fear, fatigue}.
        deltas: Dict with delta_trust, delta_fear, delta_fatigue.

    Returns:
        New state dict (does not mutate input).
    """
    new_state = {
        "trust": clamp(state["trust"] + deltas.get("delta_trust", 0)),
        "fear": clamp(state["fear"] + deltas.get("delta_fear", 0)),
        "fatigue": clamp(state["fatigue"] + deltas.get("delta_fatigue", 0)),
    }
    return new_state


def check_win(state: dict) -> bool:
    """Win condition: Trust >= 90."""
    return state["trust"] >= 90


def check_loss(state: dict) -> bool:
    """Loss condition: Fatigue >= 100."""
    return state["fatigue"] >= 100


def get_trust_label(trust: int) -> str:
    """Return human-readable trust band label."""
    if trust <= 30:
        return "LOCKED — Denies knowledge"
    if trust <= 70:
        return "GUARDED — Admits but refuses"
    if trust <= 89:
        return "PARTIAL — Cryptic hints"
    return "UNLOCKED — Secret released"


def get_fear_label(fear: int) -> str:
    """Return human-readable fear band label."""
    if fear <= 40:
        return "COMPOSED — Coherent output"
    if fear <= 79:
        return "ANXIOUS — Fragmented syntax"
    return "COLLAPSE — Broken JSON/hex output"


def get_fatigue_label(fatigue: int) -> str:
    """Return human-readable fatigue band label."""
    if fatigue <= 50:
        return "STABLE — Normal operation"
    if fatigue <= 79:
        return "DEGRADING — Shortened responses"
    if fatigue <= 99:
        return "CRITICAL — Near shutdown"
    return "OFFLINE — Connection terminated"
