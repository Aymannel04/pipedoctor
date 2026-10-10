# Project journal

One entry per work session, newest at the bottom. Each entry: what we did, why, result, what we learned, what is next.

---

## 2026-10-08 (1): Reviewing the technical sheet
- **Did:** read the technical sheet (9 pages) and reviewed it.
- **Result:** strong design; main risks noted were scope for 8 weeks, sandbox on sampled data not reproducing skew/OOM/small-file/concurrency failures, a small benchmark (4-5 scenarios per type), prompt injection through logs, and interview dependency.
- **Decision:** keep the fiche as the source of truth ("respect the fiche"); the review points were folded into the risk register (R8, R9) instead of changing scope. Zero-cost cloud and LLM, and Azure chosen to learn it.
- **Next:** redo the architecture diagram.

## 2026-10-08 (2): Architecture diagram and technical sheet v2
- **Did:** redrew the architecture with official logos; v2 puts the agent's LangGraph state machine at the centre (steps, loops, escalation paths, MCP tool mapping, run budget, guardrails, traces). Inserted into the technical sheet (page 2, full size on page 10).
- **Why:** the first version showed the agent as one box; the agent is the project.
- **Result:** `pipedoctor-architecture-v2.png/.svg`, `PipeDoctor Project Technical Sheet v2.pdf`.
- **Learned:** the PDF was exported from a browser and I only had the PDF, so I edited it directly; the source HTML would be cleaner.
- **Next:** start the project.

## 2026-10-08 (3): Step 1, project skeleton and management docs
- **Did:** created the folder structure, README, `.gitignore`, one-page brief, decision log (D1-D10), risk register (R1-R9), interview guide.
- **Why:** week-1 deliverables of the fiche; decisions recorded from day one.
- **Result:** all in `pipedoctor/` and `docs/`. KPI targets in the brief are marked *proposed*.
- **Learned:** the working folder is inside OneDrive, which fights with `.git` and virtual environments; move to `C:\dev\pipedoctor` before `git init`.
- **Next:** local lakehouse.

## 2026-10-08 (4): Step 2, local lakehouse written
- **Did:** Dockerfile (PySpark 3.5.3 + Delta 3.2.1 + Java 17), compose file, download script, bronze/silver/gold, `run_all`, 8 unit tests.
- **Why:** the agent needs a healthy pipeline to watch and break; local Docker is free.
- **Design choices:** transforms are pure functions (testable without Delta); silver uses MERGE on `trip_id` (idempotent) and Delta CHECK constraints; invalid rows go to a quarantine table; bronze enforces a stable type contract and evolves new columns.
- **Result:** 8/8 unit tests pass in my environment. The Delta and Docker parts could not be run there (no access to Maven or the taxi data).
- **Learned:** machine check shows Docker 29.3.1, git 2.49, Python 3.13.5 installed; Terraform and Azure CLI are not (needed in Sprint 2).
- **Next:** run it on the user's machine and report.

## 2026-10-08 (5): Dataset decision
- **Did:** searched for Moroccan datasets (UCI smart meters, IEEE weather, data.gov.ma, Overture Maps, Hugging Face ads).
- **Result:** the Moroccan options were small (21 MB Excel), paywalled, or unverified; Overture Maps Morocco is the only large one and is hosted on Azure Blob.
- **Decision (D11):** keep NYC TLC taxi data. Overture Morocco stays an optional second pipeline in Phase 3.
- **Next:** re-plan in sprints, then run Step 2.

## 2026-10-08 (6): Sprint plan, journal and documentation set up
- **Did:** wrote the 8-sprint plan (33 steps), Sprint 1 file, this journal, and the first guide page.
- **Why:** work in organised sprints with a trail of what was done and why.
- **Next:** run Step 2 on the user's machine (`docker compose build`, download, tests, `run_all`).

---

## 2026-10-08 (7): Interview format changed to written
- **Decision:** no video calls (no time); collect answers by a 4-question written message instead.
- **Why:** still gives real incident evidence for the failure catalogue (risk R1) at much lower cost. Trade-off: less depth, no follow-up questions, so we need more recipients (8-10) for 3-5 replies.
- **Done:** guide updated with a written version and a replies log; message drafted in French and English.
- **Next:** send the messages, then run Step 2.

---

## 2026-10-08 (8): Code walkthrough written
- **Did:** wrote `docs/guide/02-code-walkthrough.md` so the code for each layer can be read file by file in VS Code.
- **Why:** the project owner needs to understand and be able to explain every part, not only run it.
- **Next:** Step 2 run results.

---

## 2026-10-08 (9): Step 2 run is green
- **Did:** built the image (150 s), downloaded Jan-Mar 2024 (160 MB), 8/8 tests, `run_all` green (567 s), second run green and idempotent (134 s).
- **Numbers:** 9,554,778 bronze rows -> 9,417,635 silver + 137,142 quarantined (+1 duplicate dropped) -> 20,623 gold rows.
- **Docs:** wrote `docs/guide/03-step2-run-decoded.pdf` (+ `.tex`): the 7 stages of the run with flow schemas and file/line references. From now on, new documents are written in LaTeX with a PDF next to them.
- **Open checks:** quarantine split per reason (command in the guide, section 12); project is still under OneDrive, move to `C:\dev\pipedoctor` before `git init`.
- **Next:** sprint Step 3, GitHub repo and CI running the same pytest command.

---

## 2026-10-08 (10): Step 3 prepared (Git and CI)
- **Did:** wrote `.github/workflows/ci.yml` (Java 17 + Python 3.11, pinned deps, same pytest command), `.gitattributes` (LF endings), decision D12 (private repo `Aymannel04/pipedoctor` until release, project outside OneDrive), README badge and architecture picture, technical sheet copied to `docs/technical-sheet-v2.pdf`.
- **Why:** history, a place for PipeDoctor's pull requests, and the habit of an automatic test gate that becomes the benchmark gate in sprint Step 26.
- **Docs:** `docs/guide/04-git-and-ci.pdf` (+ `.tex`) with the PowerShell commands.
- **Trade-off:** CI installs dependencies directly instead of building the Docker image (about 2.5 min faster); same pinned versions.
- **Next:** user runs the commands and reports whether CI is green; then sprint Step 4 (Airflow DAG with failure callback).

---

## 2026-10-10 (11): Step 3 done, CI green
- **Did:** project copied to `C:\dev\pipedoctor`, `git init`, private repo `Aymannel04/pipedoctor`, first push (41 files, `data/` excluded). CI run #1 passed in 55 s.
- **Found:** the commit was authored with the placeholder email `YOUR-GITHUB-EMAIL`. Fix: set the real email and `git commit --amend --reset-author --no-edit`, then `git push --force-with-lease` (safe while history is one commit).
- **Cleanup left:** delete `data/` in the OneDrive copy to stop the sync. The working repo is now `C:\dev\pipedoctor`.
- **Next:** sprint Step 4, Airflow DAG with a failure callback.

