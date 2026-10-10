# Risk register

Owner for all risks: Ayman. Probability and impact: L / M / H. Reviewed at every phase gate.

| # | Risk | Prob. | Impact | Mitigation | Trigger to act | Status |
|---|---|---|---|---|---|---|
| R1 | Injected failures differ from real incidents | H | M | Build scenarios from the interviews; state the limit in the report | Interviews contradict the catalogue | Open |
| R2 | Scope creep (12 types + platform + management layer) | H | H | Fixed order: 6 types first, then the rest; each phase ends at a gate | A phase runs past its week | Open |
| R3 | Model output varies run to run | H | M | Repeat runs; report mean with bootstrap 95% CI | - | Open |
| R4 | Cloud cost (Databricks clusters bill while idle) | M | H | Develop locally in Docker; auto-terminate clusters; budget alert and cost cap | Any unexpected charge | Open |
| R5 | Free-tier limits (lineage or job features missing) | M | M | Check before building on them; fall back to table history and parsed logs | A feature is missing on the plan | Open |
| R6 | The agent takes an unsafe action | L | H | Read-only layers, allow-listed paths, mandatory approval, unsafe-action metric | Any non-zero unsafe action | Open |
| R7 | Time competes with PFE applications | H | H | Eight weeks with a demoable result at the end of week 4 | Gate 2 slips | Open |
| R8 | Not enough engineers to interview | M | M | Fall back to public postmortems and Databricks/Airflow issue trackers | Fewer than 3 interviews by end of week 1 | Open |
| R9 | Prompt injection through logs or sampled rows | M | M | Treat tool output as data; allow-list paths so the agent cannot edit tests or CI | Seen in any benchmark run | Open |
