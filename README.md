# Decision Workbench

**Expand the decision-maker's cognition BEFORE they decide.**

Decision power = size of your option space, not the ability to pick.
This tool diverges options, reveals blind spots, structures the map — and
hands the decision back to a human. It **never picks a winner**.

> *"I only know Java Spring."* — said every engineer who never saw the
> open-source CRM bases, the SaaS options, or the no-code builders.

## What it does

Paste a decision you're about to make — including what you already know.
Decision Workbench runs a 6-stage pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│  1. BIAS FLAG      "I only know Java Spring" → anchored_stack    │
│  2. DIVERGENCE     5 stances argue independently (parallel):    │
│                    🏛️ architect · 💰 cost · 🛡️ security          │
│                    📦 product · 🔴 red team                       │
│  3. CROSS-EXAM     3 probing questions force the space open:    │
│                    "Why did you NOT consider X?"                │
│                    "Give one non-mainstream option w/ reason"   │
│                    "Weakest point of your preferred option?"    │
│  4. OPTION MAP     consensus / true divergence / false          │
│                    divergence, each tagged "you probably didn't │
│                    know this" vs "you already knew this"         │
│  5. CONSTRAINTS    you check budget/team/deadline/compliance →  │
│                    weighted re-score (still no winner)          │
│  6. HUMAN DECISION the decision is yours. The system never      │
│                    picks.                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Why this exists (and why it is NOT llm-council)

| | llm-council (Karpathy) | **Decision Workbench** |
|---|---|---|
| Goal | Converge multiple models to a **better single answer** | **Expand the option space** before a human decides |
| End state | One synthesized answer | A map + trade-offs + a human decision |
| Divergence | Means to an end (better consensus) | **The product itself** |
| Who decides | The chairman model | **The human** (explicitly, always) |
| Failure mode | Artificial consensus (all models converge) | Anchoring bias (decision-maker locked in) |

The academic grounding: multi-agent LLM committees suffer from
**representational collapse** when they share a model (arXiv 2604.03809) and
**artificial consensus** when they share an architecture (arXiv 2604.26561).
This tool is deliberately built around the opposite: heterogeneous stances +
a hard human gate. It is a *diverger*, not a *converger*.

## Quick start (mock mode — zero API keys)

```bash
# Backend (port 8002)
uv sync
uv run python -m backend.main

# Frontend (port 5173, proxies /api → 8002)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, type a decision, click **"Expand my option
space"**. The mock provider ships pre-baked answers for 3 demo scenarios
(tech stack / business / hiring) so the demo never depends on a live API.

### Real models (OpenRouter)

```bash
export OPENROUTER_API_KEY=sk-or-v1-...
export PROVIDER=openrouter
uv run python -m backend.main
```

## Demo scenarios (pre-baked in mock mode)

| Scenario | Input | Blind spot revealed |
|---|---|---|
| A. Tech stack | "I need to build a CRM. I only know Java Spring." | open-source CRM bases, buy-vs-build, no-code, spreadsheet+automation |
| B. Business | "Sell report subscriptions. Only thought of Stripe." | merchant-of-record (Lemon Squeezy/Paddle), membership platforms, crypto |
| C. Hiring | "I need to hire a full-stack engineer." | remote-first, AI-augmented small team, agency outsourcing |

## API

| Endpoint | Purpose |
|---|---|
| `POST /api/decide` | Run the full pipeline → bias flags, stance divergence, probing, option-space map |
| `POST /api/decide/constraints` | Re-score against selected constraints (weighted, still no winner) |
| `POST /api/decide/human-decision` | Record the human's final choice |

## Tests

```bash
uv run pytest
# 25 tests: bias detection, stance prompts, probing, zone classification,
# novelty tagging, constraint weighting, mock provider, engine golden path
```

## Design principles

1. **The model does not decide. Ever.** The output is a map, not a verdict.
2. **Divergence is the product.** If all stances agree, the pipeline is not
   doing its job.
3. **Surfacing the anchor is the first move.** You cannot expand a space you
   don't know is locked.
4. **Real constraints close the loop.** Options are re-scored against the
   decision-maker's actual world, but the choice stays human.

## License

MIT
