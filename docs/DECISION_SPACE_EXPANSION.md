# Decision Space Expansion — Expand Cognition BEFORE You Decide

> **Decision power = size of your option space, not the ability to pick.**
>
> This is the methodology behind two projects: **llm-council** (first-generation
> implementation) and **decision-workbench** (second-generation, purpose-built).
> This document is the English companion to the Japanese docs hub
> (`doc-ja/decision-space-expansion/`).

## The core idea

Most people decide within the options they already know. A developer who
"only knows Java Spring" isn't choosing — they're picking from a 10-year-old
menu. A senior architect isn't better at choosing; they've simply **seen more
options**. Cognition surface = decision space = your decision power ceiling.

> *"AI shouldn't make important decisions for you.*
> *It should make the decision space harder for you to misunderstand."*

The best posture: ask AI **when you don't know what you don't know**, not when
you already know what you want and just want it done faster.

## The 3-stage process

### Stage 1 — Diverge (expand options)

Feed the same brief to models from **different families** (Claude/GPT/DeepSeek/
local open-source), answered **in isolation** (no cross-anchoring). Assign each
model a stance: Architect / Cost / Security / Product / Red Team.

**Three mandatory probing questions:**

1. **"Why did you NOT consider X?"** — forces out excluded options + reasons
   (highest information density)
2. **"Give one non-mainstream option with a real reason"** — kicks the model
   out of its training distribution
3. **"Weakest point of your preferred option?"** — cross-examination; a single
   model never attacks its own answer

### Stage 2 — Structure (classify options)

- **Consensus zone** → adopt directly (standard-answer parts)
- **True divergence zone** → worth human adjudication
- **False divergence zone** → noise, filter out (e.g. PHP vs Go for a CRUD app)

### Stage 3 — Converge (decide)

Backfill real constraints (budget, team skills, deadline, domestic/overseas,
compliance) and let AI do a **weighted evaluation within the expanded space**.
Optional pyDecision (AHP/TOPSIS/PROMETHEE) for comparable score tables.
**Final adjudication is always human** — models fail with confidence.

## Core insights

- Model divergence = **training-data geography/ecosystem bias + post-hoc
  rationalization**, not deep reasoning
- The most valuable divergence is geographic/ecosystem blind spots
  (domestic models surface ICP filing/WeChat mini-programs/Alibaba Cloud;
  overseas models default to AWS)
- Same-model multi-role (pi chains) has role diversity but **no cognitive
  diversity** — only heterogeneous models produce true divergence
- Committees expand "known unknowns"; they cannot reach "unknown unknowns"
- Forced understanding of divergence during human adjudication = cognitive growth
- **Decision power = option-space size.** Each decision made this way upgrades
  your decision system — option space is the only asset that grows with use

## The two projects

| | llm-council | decision-workbench |
|---|---|---|
| Origin | Fork of Karpathy's llm-council | Purpose-built from the methodology |
| Goal | Multi-model committee → **better single answer** (converger) | **Expand the option space** (diverger) |
| End state | One synthesized answer | Option map + trade-offs + **human decision** |
| Who decides | Chairman model (ours: human) | **Human (always)** |
| Stack | FastAPI 8001 + React/Vite 5173 | FastAPI 8002 + React/Vite 5173 |
| Generation | 1st (transitioned converger→diverger) | 2nd (purpose-built diverger) |

### llm-council — first generation

Karpathy's original repo was a Saturday vibe-code: multiple models answer →
anonymized peer review → a **Chairman LLM synthesizes the final answer**. We
forked and flipped the design philosophy:

- **Provider abstraction layer** (`backend/providers/`) — mock (zero-key) or
  real models, pluggable
- **Stage 3 → structured comparison report** (consensus / true divergence /
  false divergence) — the model no longer picks a winner
- **DecisionGate** — human final decision UI, persisted (`POST /decision`),
  revisable (old decision kept in `decision_history`)
- **History + export** — `GET /api/decisions`, full decision records as
  Markdown

### decision-workbench — second generation

Purpose-built 6-stage pipeline with an eval harness:

```
 1. BIAS FLAG      "I only know Java Spring" → anchored_stack
 2. DIVERGENCE     5 stances argue independently (parallel, isolated)
 3. CROSS-EXAM     3 probing questions force the space open
 4. OPTION MAP     consensus / true divergence / false divergence,
                   tagged "you probably didn't know this" vs "you already knew this"
 5. CONSTRAINTS    budget/team/deadline/compliance → weighted re-score (no winner)
 6. HUMAN DECISION the decision is yours. The system never picks.
```

**7 design principles** (mechanism layer, not "5 agents talking"):

1. Bias flag BEFORE discussion — the input is not assumed neutral
2. Independent divergence — isolated parallel reasoning, no first-mover pollution
3. Forced cross-examination — institutionalized disconfirmation
4. Option map, not winner — optimize decision-space coverage
5. Constraints LAST — divergence must be constraint-free to be honest
6. Human decides — AI provides evidence/trade-offs/unknown-unknowns
7. The model does not decide. Ever.

**Honest limitation**: 5 stances on ONE model collapse into one opinion wearing
five hats (representational collapse, arXiv 2604.03809). The mock provider
shows real divergence because its stances are hand-authored. The roadmap: each
stance on a different model family (heterogeneous providers).

## Eval: does it expand the decision space?

Falsifiable claim — *Decision Workbench surfaces more decision-relevant options,
especially ones baselines miss, than a single model or a naive multi-agent chat.*

Hidden ground truth = hand-authored gold option sets per scenario, never
revealed to the systems under test.

| Method | Gold hit (of 12) | Avg coverage |
|---|---|---|
| Single model direct answer | 3/12 | **26%** |
| Naive multi-agent (stances only) | 9/12 | **78%** |
| **Decision Workbench** | **12/12** | **100%** |

**Blind spots recovered by DW that both baselines missed:**
- Scenario A: `spreadsheet-plus-automation`, `crm-as-a-feature`
- Scenario B: `membership-platform`

The spread (26% → 100%) is the measurable value of the mechanism layer:
bias-flag → independent divergence → forced cross-examination → option map.

## Academic grounding

| arXiv | Title | Contribution |
|---|---|---|
| [2604.03809](https://arxiv.org/abs/2604.03809) | Representational Collapse in Multi-Agent LLM Committees | Same-model committees pseudo-diverge → heterogeneous models needed (cos-sim 0.888, eff. rank 2.17/3.0) |
| [2604.26561](https://arxiv.org/abs/2604.26561) | Preserving Disagreement: Architectural Heterogeneity and Coherence Validation | Artificial consensus → architecture heterogeneity + human gate (120 deliberations) |
| [2603.11781](https://arxiv.org/abs/2603.11781) | From Debate to Deliberation | Disagreement-preserving convergence → option-map design |

Full details: `doc-ja/decision-space-expansion/literature.md` (Japanese).

## Repos

- `llm-council` — http://192.168.1.21:3000/dev/llm-council (Forgejo private)
- `decision-workbench` — http://192.168.1.21:3000/dev/decision-workbench (Forgejo private)
- Methodology skill: `decision-space-expansion` (Hermes Agent)
- Japanese docs: `doc-ja/decision-space-expansion/`
