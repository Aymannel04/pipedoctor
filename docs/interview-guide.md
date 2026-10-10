# Interview guide: data engineers (3 to 5, 25 minutes each)

**Goal:** learn which failures really hurt on call, so the failure catalogue reflects reality.
**Who:** data engineers who have been on call for Spark, Airflow or dbt pipelines.
**Ground rules:** no company names or confidential details; say that notes will be anonymised.

## Warm-up (3 min)
1. What stack do you run, and how big is the on-call rotation?

## Incidents (15 min)
2. Tell me about the worst pipeline incident you handled in the last year. What happened, step by step?
3. How did you find the cause? What did you open first (orchestrator, logs, table history, lineage)?
4. How long did diagnosis take versus the fix itself?
5. What are the 3 failures you see most often? (Prompt only if needed: schema change, bad values,
   late file, skew, out of memory, duplicate rows after retry, credentials.)
6. Which failures should *never* be fixed automatically, and why?

## The agent idea (5 min)
7. If a tool opened a pull request with a diagnosis and a fix, what would you need to see to trust it?
8. What would make you reject it immediately?

## Wrap-up (2 min)
9. Anyone else I should talk to?

## Capture sheet (one per interview)
| Field | Notes |
|---|---|
| Role / stack (anonymised) | |
| Top failures (ranked) | |
| Time to diagnose / fix | |
| Never-auto-fix list | |
| Trust requirements | |
| Maps to catalogue # | |
| New failure type to add? | |

---

# Written version (chosen format)

**Decision (2026-10-08):** no calls; collect answers by written message. Same goal, shorter form.
Send to 8-10 people, aim for 3-5 replies. Questions (answer in one line each is fine):

1. The 3 most frequent pipeline failures on your team?
2. The worst incident, in 3-4 lines: what broke, how the cause was found, how long it took.
3. Which failures should never be fixed automatically?
4. What would you need to see in a pull request (diagnosis + tested fix) to trust it?

Paste each reply into the capture sheet above (anonymised). Map every answer to a catalogue number.

## Replies log
| # | Date | Source (anonymised) | Replied? | Notes |
|---|---|---|---|---|
