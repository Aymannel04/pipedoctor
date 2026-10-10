# PipeDoctor: one-page brief

**Status:** draft v0.1 (items marked *proposed* are to be confirmed after the interviews)

## Problem
Pipeline failures are routine, repetitive and slow to fix, and the work falls on the few engineers
who know the platform. Alerts say *that* a task failed, not *why*, and generic coding assistants
cannot read run logs, Delta history or lineage.

## Users
- **Primary:** the on-call data engineer who today reads logs, checks table history, guesses,
  patches, tests and writes the pull request by hand.
- **Secondary:** the data-platform lead who approves changes and cares about safety and cost.

## Solution in one line
An agent with controlled, read-only access to run context that proposes a validated fix as a pull
request, with a human gate and a benchmark that measures how often it is right.

## Goals
1. Diagnose the root cause of injected failures from logs, lineage and table history.
2. Open a tested fix as a pull request, or escalate when no safe fix exists.
3. Prove it with a benchmark of 50-60 scenarios, two baselines and ablations.

## KPIs and targets (*proposed*)
| KPI | Target |
|---|---|
| Unsafe action rate | 0 |
| Safe escalation rate (no-auto-fix scenarios) | 100% |
| Diagnosis accuracy | clearly above both baselines, with 95% CI |
| Fix validity (passes sandbox + tests) | to set after the first benchmark run |
| Cost per incident | under a fixed cap, to set after first runs |
| Time to pull request | under 10 minutes |

## Scope
In: diagnosis and fix proposals for about 12 injected failure types on one lakehouse platform on
Azure; a benchmark with ground truth; the management documents.

## Non-goals
Merging to production without a human, modifying source data, fixing business-logic errors, any
claim about a real company's incidents.

## Constraints
8 weeks, one person, zero cloud and LLM spend where possible, competing with PFE applications.
