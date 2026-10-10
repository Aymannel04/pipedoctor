# Sprint 1: local platform

**Dates:** Thu 8 Oct - Wed 14 Oct 2026 (proposed)
**Phase:** 1 Foundations
**Goal:** a healthy local lakehouse that runs on a schedule and emits failure events.

## Backlog
- [x] **Step 1** Project skeleton, one-page brief, decision log, risk register, interview guide
- [x] **Step 2** Local lakehouse in Docker (bronze/silver/gold on NYC taxi)
  - [x] Docker image and compose file written
  - [x] Pure transforms with unit tests (8 passing)
  - [x] Bronze, silver, gold modules and `run_all` written
  - [x] **Docker build and full run on the user's machine** (8 Oct: 8 tests pass; 9,554,778 bronze rows, 9,417,635 silver, 137,142 quarantined, 20,623 gold; second run idempotent)
  - [x] Run explained in `docs/guide/03-step2-run-decoded.pdf` (LaTeX)
- [ ] **Step 3** Git repo on GitHub (outside OneDrive) and CI running the tests
  - [x] `ci.yml`, `.gitattributes`, decision D12, README badge and architecture picture, guide `docs/guide/04-git-and-ci.pdf`
  - [ ] **User: copy to `C:\dev\pipedoctor`, `git init`, create the private repo, push, CI green** (pending)
- [ ] **Step 4** Airflow DAG for the pipeline, failure callback writing an event, run logs kept
- [ ] **Step 5** Interview requests sent (5+), doc checkpoint 1, sprint review

## Definition of done
- Each step has code or docs, was run or tested, and has a journal entry.
- `python -m pipelines.run_all` ends green on the user's machine.
- Airflow can run the DAG, and a deliberately broken run produces an event file.

## Risks to watch
- R4 cost: nothing in this sprint should cost money.
- R8 interviews: requests must go out this sprint.
- Windows + OneDrive + Docker bind mounts: develop outside OneDrive.

## Review (fill in at the end)
- Shipped:
- Slipped:

## Retro (fill in at the end)
- Keep:
- Change:
- Try:
