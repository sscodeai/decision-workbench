# Decision Workbench — Demo Scenarios (D1)

> Core idea: **expand the decision-maker's cognition BEFORE they decide.**
> Decision power = size of the option space, not the ability to pick.
> The system does NOT pick an answer for the user — it expands their option
> space, reveals blind spots, then hands the decision back to a human.

## Golden-path interaction (the "aha" moment)

The user types a real decision they are about to make, e.g.:

> "I need to build a CRM. I only know Java Spring."

The system:

1. **Flags locked-in bias**: detects the user already anchored on a stack
   ("only know Java Spring") and surfaces it explicitly.
2. **Diverges by stance**: spawns independent perspectives (Architect / Cost /
   Security / Product / Red-team) — each forced to argue a different angle.
3. **Asks the three probing questions**:
   - "Why did you NOT consider X?" (forces out excluded options)
   - "Give one non-mainstream option with a real reason" (kicks the model out
     of its training distribution)
   - "What is the weakest point of your preferred option?" (cross-examination)
4. **Outputs an option-space map**: consensus zone / true-divergence zone /
   false-divergence zone, with each option tagged **"you probably didn't know
   this"** vs "you already knew this".
5. **Constraint backfill**: user checks real constraints (budget, team skills,
   deadline, compliance) → weighted evaluation.
6. **Human final decision**: the system explicitly does NOT pick a winner.
   It presents the map + trade-offs and asks the human to decide.

## Scenario A — Tech stack selection (flagship, matches JD)

| Field | Content |
|---|---|
| Input | "I need to build a CRM system. I only know Java Spring." |
| Blind spot revealed | Go/TypeScript open-source CRM bases (e.g. twenty, crmscript), buying vs building, no-code |
| Expected output | Option-space map with ≥5 options, 2-3 tagged "you probably didn't know" |
| Impact point | Red-team: "Building a CRM from scratch when mature open source exists is reinventing the wheel." |

## Scenario B — Business decision (payment for report subscriptions)

| Field | Content |
|---|---|
| Input | "I want to sell English research-report subscriptions. I only thought of Stripe." |
| Blind spot revealed | Lemon Squeezy (merchant of record), Paddle, self-hosted payment, PayPal, crypto |
| Expected output | Options with compliance/tax implications per region, ≥1 non-mainstream option |
| Impact point | "Stripe needs a US entity or a payment partner — Lemon Squeezy/Paddle are merchants of record that solve tax for you." |

## Scenario C — Hiring / team building

| Field | Content |
|---|---|
| Input | "I need to hire a full-stack engineer." |
| Blind spot revealed | Remote-first hiring, overseas contractors, AI-augmented small team, buying vs hiring |
| Expected output | ≥4 hiring models with cost/latency/quality trade-offs |
| Impact point | "For a 3-month MVP, an AI-augmented 1-person team + a contractor may beat a full-time hire." |

## Anti-patterns (what the system must NOT do)

- ❌ Pick a winner / "the best option is X" — the model does NOT decide.
- ❌ Silently agree with the user's anchored choice.
- ❌ Converge to one answer (that is llm-council's job, not ours).
- ❌ Hide disagreements — true divergence is the product.

## Success metric for the demo

After the interaction the user can answer: "I knew 1 option before, I know
≥3 more now, and I understand WHY my original choice may be biased."
