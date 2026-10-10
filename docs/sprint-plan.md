# PipeDoctor: sprint plan

Eight one-week sprints grouped into the four phases (and four gates) of the technical sheet.
Dates are proposed and can slide; the order and the gates cannot. Sprint 1 starts Thu 8 Oct 2026.

## The end goal
By the end of week 8 we can show, with numbers, that an AI agent can act as an on-call data engineer:

1. A **platform** on Azure (Terraform-built) running real pipelines on a large dataset.
2. A **failure injector** with 12 failure types, each with a known root cause and a ground-truth fix, expanded into 50-60 benchmark scenarios.
3. An **agent** (LangGraph + MCP) that detects a failure, gathers context through read-only tools, diagnoses with evidence, proposes a fix, validates it in a sandbox, and opens a pull request, or escalates when no safe fix exists. A human approves.
4. A **benchmark** that measures it: diagnosis accuracy, fix validity and correctness, safe escalation, unsafe actions (target 0), cost and time, against two baselines and three ablations, with bootstrap 95% confidence intervals, enforced by a CI gate.
5. The **management layer**: brief, decision log, risk register, cost dashboard, postmortems, reliability scorecard, demo script.
6. A rehearsed, recorded **five-minute demo** and a README that states the limits honestly.

## How we work
- **A step is the unit of work.** Each step: explain (what, why, how) -> do -> verify -> journal entry.
- **A sprint** has a goal, a backlog of steps, and a definition of done. Sprint file: `docs/sprints/sprint-NN.md`.
- **Definition of done** for a step: code or doc exists, it was run or tested, `docs/journal.md` has an entry, and the sprint checklist is ticked.
- **Journal** (`docs/journal.md`): one dated entry per work session. What we did, why, what happened, what we learned, what is next.
- **Doc checkpoints** every 2-3 steps: a page in `docs/guide/` describing what now exists (architecture, how to run, design choices, troubleshooting), written while it is fresh.
- **Sprint review and retro** at the end of every sprint: tick the sprint file, update the decision log and the README roadmap, review the risk register at every gate.
- **Gates** are go/no-go reviews recorded in `docs/decision-log.md`.
- **Cut order if we slip** (so we cut on purpose, not by accident): ablations, then the second model, then the Azure deployment of the agent. Never cut the benchmark, the sandbox or the guardrails.

## Sprint map

| Sprint | Dates (proposed) | Phase | Goal | Gate |
|---|---|---|---|---|
| 1 | 8-14 Oct | 1 Foundations | A healthy local lakehouse that runs on a schedule and emits failure events | |
| 2 | 15-21 Oct | 1 Foundations | dbt on top, the same pipelines running on Azure Databricks, interviews done | **Gate 1**: pipelines green locally and on Azure |
| 3 | 22-28 Oct | 2 Break it | A failure injector with ground truth, and the run context captured per incident | |
| 4 | 29 Oct-4 Nov | 2 Break it | MCP tool server and agent v1 opening a PR | **Gate 2**: first demo, PR for 3 failure types |
| 5 | 5-11 Nov | 3 Safe and measured | Sandbox validation, guardrails, all 12 failure types | |
| 6 | 12-18 Nov | 3 Safe and measured | The benchmark, baselines, ablations, CI evaluation gate | **Gate 3**: benchmark runs in CI with intervals |
| 7 | 19-25 Nov | 4 Ship it | Cost dashboard, postmortems, scorecard, Azure deployment | |
| 8 | 26 Nov-2 Dec | 4 Ship it | Demo, README, final report, release | **Gate 4**: five-minute demo runs end to end |

## Steps by sprint

### Sprint 1: local platform (goal: a healthy local lakehouse that emits failure events)
| Step | What | Why | Status |
|---|---|---|---|
| 1 | Project skeleton, brief, decision log, risk register, interview guide | Gate 1 starts here; decisions recorded from day one | Done |
| 2 | Local lakehouse in Docker: bronze/silver/gold on NYC taxi data, unit tests | The system the agent will watch and we will break | Written, tests pass, **Docker run pending** |
| 3 | Git repo on GitHub (outside OneDrive) and CI that runs the tests | CI is later the evaluation gate; start with the habit | To do |
| 4 | Airflow (Docker): a DAG running the pipeline, a failure callback that writes an event and keeps run logs | Failure events and logs are the agent's raw material | To do |
| 5 | Send interview requests (5+); doc checkpoint 1; sprint review | Interviews take days to schedule | To do |

### Sprint 2: dbt and Azure (goal: Gate 1)
| Step | What | Why |
|---|---|---|
| 6 | dbt project: models over silver/gold plus dbt tests, running locally | dbt is one of the three failing layers |
| 7 | Azure account, budget alert first, install Azure CLI and Terraform | Cost control before anything is created |
| 8 | Terraform: resource group, ADLS Gen2, Key Vault, Databricks workspace (check free-tier limits, risk R5) | Platform rebuilt from code |
| 9 | Run the pipelines on Databricks with Auto Loader on the same data | Proves local and Azure behave alike |
| 10 | Interviews synthesised, failure catalogue adjusted, one-page brief final; **Gate 1 review**; doc checkpoint 2 | Catalogue must reflect real incidents (risk R1) |

### Sprint 3: break it (goal: failures with ground truth)
| Step | What | Why |
|---|---|---|
| 11 | Scenario format and injector framework: repo patch + data change + `ground_truth.yaml`, apply and revert | Reproducible failures and a way to score fixes |
| 12 | Scenarios 1-3: schema drift, type change, invalid values | Most common failures first |
| 13 | Scenarios 8, 10, 11: duplicates after retry, broken dbt ref, column removed upstream | Cover Spark and dbt layers |
| 14 | Capture run context per incident: logs, Spark error, Delta history, schema diff, lineage; doc checkpoint 3 | Exactly what the MCP tools will serve |

### Sprint 4: agent v1 (goal: Gate 2)
| Step | What | Why |
|---|---|---|
| 15 | MCP tool server: read-only tools, SQL validator plus read-only role | Every capability explicit, logged and limited |
| 16 | LangGraph agent v1: triage, gather, diagnose, propose, report; decide LLM (D6) and tracing (D7) | The decision loop |
| 17 | `open_pr` on GitHub (cannot merge); first PRs for 3 failure types | The end of the loop a human can review |
| 18 | **Gate 2 demo**, doc checkpoint 4, sprint review | First demoable result |

### Sprint 5: safe (goal: sandbox, guardrails, all 12 types)
| Step | What | Why |
|---|---|---|
| 19 | Sandbox on a sampled copy, validate node, retry loop | A fix is only proposed after it passes |
| 20 | Guardrails: path allow-list (not tests or CI), step and cost caps, confidence gate, no-auto-fix list, unsafe-action detector | Safety is the point; unsafe actions target 0 |
| 21 | Remaining scenarios: 4, 5, 6, 7, 9, 12 | Complete catalogue, includes the two escalation cases |
| 22 | Doc checkpoint 5 | |

### Sprint 6: measured (goal: Gate 3)
| Step | What | Why |
|---|---|---|
| 23 | Scenario generator to 50-60 scenarios; development split and held-out split | Tune on one, score once on the other |
| 24 | Benchmark runner, metrics, repeated runs, bootstrap 95% CI | Model output varies (risk R3) |
| 25 | Baselines (model with logs only; rule-based runbook) and ablations (no lineage, no Delta history, no sandbox) | Shows which part earns its place |
| 26 | CI evaluation gate in GitHub Actions; **Gate 3 review**; doc checkpoint 6 | Blocks regressions |

### Sprint 7: ship prep (goal: management artifacts and Azure deployment)
| Step | What | Why |
|---|---|---|
| 27 | Cost tracking and dashboard (cloud and model spend per incident and per week) | Fixed budget, visible |
| 28 | Postmortem per benchmark failure the agent got wrong; reliability scorecard | Learning loop and one-page results |
| 29 | Terraform deploy of the agent and tool server on Container Apps, Registry, Key Vault | The whole platform from one command |
| 30 | Doc checkpoint 7 | |

### Sprint 8: ship (goal: Gate 4)
| Step | What | Why |
|---|---|---|
| 31 | Demo script, rehearsal, recording | Five minutes from failure to merged fix |
| 32 | README, final report (limits stated), cleanup, release tag | What a recruiter reads first |
| 33 | **Gate 4 review**, retro, final documentation | Closing the project properly |

## Sprint template
Every sprint file in `docs/sprints/` has: goal, dates, backlog with checkboxes, definition of done, risks to watch, review (what shipped, what slipped) and retro (keep, change, try).
