# Decision Workbench

**Expand the decision-maker's cognition BEFORE they decide.**

Decision power = size of your option space, not the ability to pick.
This tool diverges options, reveals blind spots, structures the map — and
hands the decision back to a human. It **never picks a winner**.

> *"AI shouldn't make important decisions for you.*
> *It should make the decision space harder for you to misunderstand."*

> *"I only know Java Spring."* — said every engineer who never saw the
> open-source CRM bases, the SaaS options, or the no-code builders.

## What it does

Paste a decision you're about to make — including what you already know.
Decision Workbench runs a 6-stage pipeline:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  1. BIAS FLAG          "I only know Java Spring" -> anchored_stack      │
│  2. DIVERGENCE         5 stances argue independently (parallel):        │
│                        architect · cost · security                      │
│                        product · red team                               │
│  3. CROSS-EXAM         3 probing questions force the space open:        │
│                        "Why did you NOT consider X?"                    │
│                        "Give one non-mainstream option w/ reason"       │
│                        "Weakest point of your preferred option?"        │
│  4. OPTION MAP         consensus / true divergence / false divergence,  │
│                        each tagged "you probably didn't know this" vs   │
│                        "you already knew this"                          │
│  5. CONSTRAINTS        you check budget/team/deadline/compliance ->     │
│                        weighted re-score (still no winner)              │
│  6. HUMAN DECISION     the decision is yours. The system never picks.   │
└─────────────────────────────────────────────────────────────────────────┘
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

The value is not "5 agents talking" — multi-agent debate is not new. The
value is the *mechanism layer* around the models, each constraining a natural
model failure mode:

1. **Bias flag BEFORE discussion.** The input is not assumed neutral. We
   first detect whether the question itself has already framed the answer
   ("I only know Java Spring" → anchored_stack). You cannot expand a space
   you don't know is locked.
2. **Independent divergence.** Architect / Cost / Security / Product /
   Red Team reason independently (parallel, isolated) before anything is
   shared — reducing mutual anchoring. This beats "everyone joins one chat"
   because the first-mover's frame doesn't pollute the others.
3. **Forced cross-examination.** Probing questions like *"Why did you NOT
   consider X?"* and *"Weakest point of your preferred option?"* are
   institutionalized disconfirmation — the system *forces* counter-evidence
   search instead of relying on a prompt saying "be comprehensive."
4. **Option map, not winner.** The objective is decision-space coverage, not
   answer selection. We optimize for the human seeing a complete-enough
   space *before* deciding.
5. **Constraints LAST.** Divergence happens first, reality filters after.
   If you tell the models "our team is all Java" up front, every agent
   orbits Java. Divergence must be constraint-free to be honest.
6. **Human decides.** AI provides evidence, trade-offs, and surfaces
   unknown-unknowns; the responsibility boundary stays with the human. This
   is especially right for enterprise architecture decisions.
7. **The model does not decide. Ever.** The output is a map, not a verdict.

## The honest limitation: 5 stances ≠ 5 independent minds

Five role prompts on ONE model tend to collapse into one opinion wearing
five hats (representational collapse — arXiv 2604.03809). The mock provider
shows real divergence because its five stances are hand-authored. With a
single real model, divergence narrows. The fix (roadmap): each stance runs
on a *different* model family (heterogeneous providers), so the divergence is
cognitively real, not just prompt-deep. The eval harness below measures
whether this actually works.

## Eval: does it expand the decision space?

The product makes a falsifiable claim:

> *Decision Workbench surfaces more decision-relevant options — especially
> options the baseline would miss — than a single model or a naive
> multi-agent chat.*

Metrics:

| Metric | Question |
|---|---|
| Option discovery | How many distinct decision-relevant options surface? |
| Blind-spot coverage | How many options did the baseline MISS that ours found? |
| Counterargument coverage | How many stances have a real counterargument to the anchor? |
| Novel-option rate | Fraction of surfaced options tagged "you probably didn't know this" |

### Current results (mock mode, hidden ground truth)

Hidden ground truth = hand-authored gold option sets per scenario, never
revealed to the systems under test. Run it yourself: `uv run python -m backend.eval_harness`

| Method | Gold hit (of 12) | Avg coverage |
|---|---|---|
| Single model direct answer | 3/12 | 26% |
| Naive multi-agent (stances only) | 9/12 | 78% |
| **Decision Workbench** | **12/12** | **100%** |

**Blind spots recovered by Decision Workbench that both baselines missed:**
- Scenario A: `spreadsheet-plus-automation`, `crm-as-a-feature`
- Scenario B: `membership-platform`

The spread between single-model (26%) and the full pipeline (100%) is the
measurable value of the mechanism layer: bias-flag → independent divergence →
forced cross-examination → option map. Full per-scenario breakdown:
[`docs/EVAL_REPORT.md`](docs/EVAL_REPORT.md)

The next milestone is the same experiment on **heterogeneous real models**
(one provider per stance) to confirm the divergence survives
representational collapse (arXiv 2604.03809) with real models, not just
hand-authored mocks.

If that holds, the project is no longer "an impressive multi-agent workflow"
— it is a testable position:

> *AI shouldn't make important decisions for you. It should make the decision
> space harder for you to misunderstand.*

## License

MIT
