# Decision Space Expansion — Eval Report

Hidden ground truth: hand-authored gold option sets per scenario
(never revealed to the systems under test).

| Scenario | Method | Options found | Gold hit | Coverage | Blind spots missed |
|---|---|---|---|---|---|
| A | single_model | 1 | 1 | 20% | 4 |
| A | naive_multiagent | 3 | 3 | 60% | 2 |
| A | decision_workbench | 5 | 5 | 100% | 0 |
| B | single_model | 1 | 1 | 25% | 3 |
| B | naive_multiagent | 3 | 3 | 75% | 1 |
| B | decision_workbench | 4 | 4 | 100% | 0 |
| C | single_model | 1 | 1 | 33% | 2 |
| C | naive_multiagent | 3 | 3 | 100% | 0 |
| C | decision_workbench | 3 | 3 | 100% | 0 |

## Aggregates

| Method | Total gold hit (of 12) | Avg coverage |
|---|---|---|
| single_model | 3/12 | 26% |
| naive_multiagent | 9/12 | 78% |
| decision_workbench | 12/12 | 100% |

## Blind spots recovered by Decision Workbench

- **Scenario A**: crm-as-a-feature, spreadsheet-plus-automation
- **Scenario B**: membership-platform
- Scenario C: (none beyond baselines)
