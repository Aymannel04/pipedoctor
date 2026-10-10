# Decision log

One short record per major choice. Status: **Accepted**, **Open** (decide by the date shown) or
**Superseded**. Each gate review is recorded at the bottom.

| # | Decision | Status | Why | Alternatives rejected |
|---|---|---|---|---|
| D1 | Cloud: **Azure** | Accepted | Goal is to learn Azure; student and free tiers keep cost near zero; local Docker covers development | GCP (more PFE offers mention it: 4 vs 3, but not the learning goal), AWS |
| D2 | Platform: **Azure Databricks** (Jobs/Workflows, Unity Catalog) | Accepted, check free-tier limits in week 1-2 | Run logs, job API and lineage are exactly the agent's inputs | Self-managed Spark |
| D3 | Storage: **ADLS Gen2 + Delta Lake**, Auto Loader ingestion | Accepted | Table history and schema evolution drive several failure types | Plain Parquet |
| D4 | Orchestration: **Airflow** (schedules, emits failure events) with **Databricks Workflows** for Spark jobs; **dbt** for SQL models | Accepted | Covers the three failure sources named in the fiche | - |
| D5 | Agent: **LangGraph** state machine, tools exposed through an **MCP** server | Accepted | Every capability explicit, logged and limited | Free-form agent loop |
| D6 | LLM provider and second comparison model | **Open** (decide week 3) | Must be near-zero cost; the choice is itself benchmarked | - |
| D7 | Tracing: **Langfuse** or LangSmith | **Open** (decide week 3) | Replayable traces; pick whichever has a usable free tier | - |
| D8 | Development: local Docker replica (PySpark + Delta); Azure for the demo | Accepted | Free development, Azure cost only for the demo | Develop only on Azure |
| D9 | IaC: **Terraform (azurerm)** | Accepted | Rebuild the whole platform from one command | Portal clicks |
| D10 | CI/CD: **GitHub Actions** | Accepted | Hosts tests and the evaluation gate | - |
| D11 | Dataset: **NYC TLC yellow-taxi trips** (monthly parquet) | Accepted | Large, real, monthly files fit Auto Loader and late-file scenarios; already built and tested. Moroccan datasets found were small, paywalled or unverified; **Overture Maps Morocco** kept as an optional second pipeline in Phase 3 | UCI Moroccan smart meters (21 MB, one Excel file), IEEE Morocco weather (paywalled), data.gov.ma (no large time series confirmed) |
| D12 | Repository: GitHub **`Aymannel04/pipedoctor`**, **private** until the release (Gate 4), project kept outside OneDrive (`C:\dev\pipedoctor`) | Accepted | Private while interview replies and drafts live in `docs/`; Actions minutes are ample for unit tests; OneDrive sync would fight Delta files and 1.3 GB of data. Flip to public at the release after a review of `docs/` | Public from day one; developing inside OneDrive |

## Gate reviews
| Gate | Date | Go / no-go | Notes |
|---|---|---|---|
| 1 Foundations | | | |
| 2 First demo | | | |
| 3 Benchmark in CI | | | |
| 4 Five-minute demo | | | |
