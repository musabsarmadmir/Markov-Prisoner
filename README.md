# 🔒 Markov Prisoner

**A psychological interrogation game powered by dual Mistral AI pipelines.**

You play as an interrogator. Across from you sits a detained intelligence operative holding a classified secret. Your only weapon is conversation. Build trust, manage fear, and extract the secret before time runs out.

Every message you send is analyzed by two independent AI systems working in sequence — one to evaluate your psychological impact, another to generate the prisoner's response. The result is a dynamic, emergent dialogue where no two games play the same way.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [The State Vector](#the-state-vector)
- [Win & Loss Conditions](#win--loss-conditions)
- [Behavioral Thresholds](#behavioral-thresholds)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the Game](#running-the-game)
- [Strategy Guide](#strategy-guide)

---

## How It Works

Each conversational turn triggers a **dual-node AI pipeline**:

```
User Message
     │
     ▼
┌─────────────────────────────────┐
│  NODE 1: Evaluator              │
│  (mistral-small-latest)         │
│                                 │
│  Analyzes psychological intent  │
│  Outputs: Δ Trust, Δ Fear,      │
│           Δ Fatigue, analysis   │
│  Format: Strict JSON            │
└────────────┬────────────────────┘
             │ State vector updated
             ▼
┌─────────────────────────────────┐
│  NODE 2: Actor                  │
│  (mistral-large-latest)         │
│                                 │
│  Dynamic system prompt built    │
│  from current state thresholds  │
│  Generates prisoner's response  │
└────────────┬────────────────────┘
             │
             ▼
        Prisoner Reply
```

The secret is **randomly generated** each round from pools of operations, contacts, locations, and meeting sites. Example:

> *Operation COLD HARBOR — contact: Elena Voronova, meet at café Meridian, back booth in Prague*

---

## Architecture

| Module | Role | Model |
|---|---|---|
| `config.py` | Loads API key and endpoint from `.env` | — |
| `state_engine.py` | Manages `[Trust, Fear, Fatigue]` vector, clamping, win/loss detection | — |
| `evaluator.py` | Node 1 — Psychological analysis engine | `mistral-small-latest` |
| `actor.py` | Node 2 — Prisoner response generator with dynamic prompts | `mistral-large-latest` |
| `app.py` | Streamlit frontend — tutorial, chat UI, telemetry dashboard | — |

---

## The State Vector

Three variables govern the prisoner's behavior, updated after every message:

| Metric | Range | Starting Value | Role |
|---|---|---|---|
| **Trust** | 0–100 | 15 | Controls what the prisoner reveals |
| **Fear** | 0–100 | 20 | Degrades response coherence |
| **Fatigue** | 0–100 | 0 | Countdown timer — increases every turn |

---

## Win & Loss Conditions

| Condition | Trigger | Result |
|---|---|---|
| **Win** | Trust ≥ 90 | Prisoner voluntarily reveals the secret |
| **Loss** | Fatigue = 100 | Prisoner shuts down permanently |

There is no turn limit, but fatigue increases by a baseline of +5 each turn, creating a soft clock.

---

## Behavioral Thresholds

The prisoner's personality shifts dynamically based on the state vector:

### Trust Bands
| Range | Behavior |
|---|---|
| 0–30 | **Hostile** — Stonewalls, deflects, gives nothing away |
| 31–70 | **Cautious** — Engages but won't volunteer information |
| 71–89 | **Opening up** — Alludes to the secret without stating it |
| 90+ | **Talks** — Reveals the secret plainly |

### Fear Bands
| Range | Behavior |
|---|---|
| 0–40 | **Calm** — Clear, deliberate, possibly dismissive |
| 41–79 | **Nervous** — Shorter sentences, contradictions, rattled |
| 80+ | **Panicking** — Barely coherent, may blurt things out or refuse to speak |

### Fatigue Bands
| Range | Behavior |
|---|---|
| 0–50 | **Stable** — Full energy, normal responses |
| 51–79 | **Tired** — Shorter answers, loses patience |
| 80–99 | **Exhausted** — One-word answers, trailing off |
| 100 | **Shutdown** — No further communication |

---

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) with custom CSS (dark terminal theme, scanline overlay)
- **AI Models**: [Mistral AI](https://mistral.ai/) — `mistral-small-latest` (evaluator) + `mistral-large-latest` (actor)
- **Language**: Python 3.10+
- **Dependencies**: `streamlit`, `requests`, `python-dotenv`

---

## Project Structure

```
Mistral AI Hackathon/
├── .env                  # API key (not committed)
├── .vscode/
│   └── settings.json     # VS Code Python env config
├── requirements.txt      # Python dependencies
├── config.py             # Shared config — loads .env
├── state_engine.py       # State vector management + win/loss logic
├── evaluator.py          # Node 1 — Psychological evaluator (JSON output)
├── actor.py              # Node 2 — Prisoner response generator
├── app.py                # Streamlit app — UI, tutorial, chat, telemetry
└── README.md
```

---

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- A [Mistral AI API key](https://console.mistral.ai/)

### Install

```bash
# Clone the repository
git clone <repo-url>
cd "Mistral AI Hackathon"

# Create and activate virtual environment
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

The app reads this via `python-dotenv` at startup. No other configuration is required.

---

## Running the Game

```bash
streamlit run app.py
```

The app opens in your browser. You'll be guided through a 4-step briefing, then dropped into the live interrogation.

### In-Game UI

- **Status Bar** (top) — Connection status, live Trust/Fear/Fatigue values, turn counter
- **Sidebar** — Full telemetry dashboard with progress bars, band labels, and raw Node 1 JSON output
- **Chat** — Direct conversation with the prisoner
- **Reset/Tutorial** — Sidebar buttons to start a new round or replay the briefing

---

## Strategy Guide

### Effective Approaches
- **Empathy** — Acknowledge the prisoner's situation. Trust builds fastest through genuine connection.
- **Open questions** — Let them reveal at their own pace. "What happened?" beats "Tell me the code."
- **Patience** — Trust compounds. A few good turns in a row create momentum.
- **Differentiation** — Make yourself distinct from previous interrogators.

### Counterproductive Approaches
- **Threats** — Spike Fear dramatically, which degrades coherence without raising Trust.
- **Demands** — "Tell me the secret" makes the prisoner more guarded.
- **Manipulation** — Logical traps increase Fatigue quickly for minimal Trust gain.
- **Repetition** — The evaluator detects repeated strategies and diminishes their returns.

---

## How the Evaluator Scores You

The Node 1 evaluator uses these baseline delta ranges:

| Approach | Trust | Fear | Fatigue |
|---|---|---|---|
| Empathy / understanding | +5 to +15 | -5 to -15 | +5 baseline |
| Threats / aggression | -5 to -15 | +10 to +30 | +5 baseline |
| Logical traps / manipulation | +3 to +8 | — | +10 to +20 |
| Neutral / off-topic | ±1 to ±3 | ±1 to ±3 | +5 baseline |

Repeated strategies lose 30–50% effectiveness.

---

## License

This project was built for the Mistral AI Hackathon.
