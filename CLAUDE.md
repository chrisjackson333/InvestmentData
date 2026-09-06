# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state: scaffold only

This repo is currently a **skeleton** — the directory layout and domain design are locked, but almost no
code exists yet. All Python source files (`data-jobs/ingestion/adapters/csv.py`, `data-jobs/ingestion/adapters/yfinance.py`,
`data-jobs/transforms/spark/buildTimeframes.py`), every `pyproject.toml`, and `services/signal-engine/Dokerfile`
are empty placeholders. `shared/`, `infra/`, and `tests/` contain only empty directories marking where things
belong. There is no CI config (`.github/` is empty), no lockfiles, and no installed dependencies.

**Implication for Claude:** there are no working build/lint/test commands to run yet. Don't assume Poetry
environments, dependency installs, or pytest exist and runnable — check before invoking them, and expect to be
the one creating `pyproject.toml` contents, not just editing existing ones. When implementing a component, set
it up per the standards below (Python 3.10, Poetry, Ruff, Black, Pyright, pytest) since none of that
tooling is wired up yet.

## What this project is

A portfolio project (see `README.txt`) demonstrating a Python microservices platform: ingest market/portfolio
data, process with PySpark, store in DynamoDB/PostgreSQL, expose trade-signal APIs via API Gateway + Lambda,
deployed on EKS, with Kafka event streaming and Terraform/GitHub Actions CI/CD.

## MVP scope lock (see `docs/architecture/ScopeBoundaries.txt`)

Keep all work inside this until told otherwise — the scope doc explicitly defers anything not required to pass
MVP acceptance:

- **Instrument:** NQ1! futures only, no other instruments.
- **Timeframes:** 1-minute source candles aggregated to 5-minute strategy candles only.
- **Data source:** CSV ingestion only (a yfinance adapter path exists as an empty stub for phase 1.5+, not MVP).
- **Strategy:** long-only SMA20 signal only — no other strategy families yet.
- **Persistence:** PostgreSQL is the source of truth for signal history in MVP; DynamoDB latest-state cache is
  optional/deferred unless latency requires it early.
- **Deployment:** only the Signal Engine service deploys to EKS (dev, non-prod); other cloud components may be
  mocked during MVP.
- **Out of scope:** no live broker integration/order execution, no multi-instrument or multi-timeframe support,
  no production release hardening.

MVP acceptance path: `CSV -> transform -> signal -> PostgreSQL -> API -> Kafka event`.

## Domain architecture (see `docs/architecture/DomainContract.txt`)

The repo is split into five strictly-bounded domains. Each owns specific responsibilities and must not reach
into another domain's concerns — this is the key thing to understand before touching multiple directories:

| Domain | Directory | Owns | Does NOT own |
|---|---|---|---|
| **Ingestion** | `data-jobs/ingestion/` | CSV adapter, raw schema validation, S3 raw-zone landing conventions | Candle aggregation, signal calc, Kafka publish |
| **Signal Engine** | `services/signal-engine/` | SMA20 long-only strategy logic, reason codes, PostgreSQL signal history, latest-signal computation | API auth/routing, Kafka provisioning |
| **API Layer** | `services/api-orchestrator/` | Endpoint contracts, request/response validation, API Gateway + Lambda orchestration | Strategy math, transform logic, raw ingestion |
| **Streaming** | (Kafka producer/consumer code, domain not yet scaffolded as its own directory) | Topic conventions, event schema/versioning, producer reliability (acks/retry/idempotency) | Authoritative storage (Postgres owns that), API contracts |
| **Platform/Infra** | `infra/` | EKS/Docker/Terraform, IAM, observability baseline, CI/CD gates | Business/strategy/API logic |

Allowed dependency direction (strict, enforced by convention not tooling):
`Ingestion -> Signal Engine -> PostgreSQL`, `Signal Engine -> Streaming`, `API Layer -> Signal Engine read path`,
`Streaming Consumers -> read models/audit stores`, `Platform/Infra -> supports all domains`.

Explicitly disallowed shortcuts: API Layer reading raw ingestion data directly; Ingestion publishing final
trading signals; Platform/Infra containing business strategy code.

### Cross-domain data contracts to respect

These are the locked interfaces between domains (field-level contracts, see `DomainContract.txt` for full detail):

1. **Ingestion -> Signal Engine** (5-minute candle): `symbol, candle_ts_utc, open, high, low, close, volume, source_batch_id, quality_flags[]`
2. **Signal Engine -> API Layer** (latest signal): `symbol, timeframe, signal ("LONG"|"HOLD"), strategy ("sma20_long_only"), signal_ts_utc, reason_code, input_ref`
3. **Signal Engine -> Streaming** (`signal.created` event): `event_id, event_type, event_version, produced_ts_utc, correlation_id, payload`

`shared/contracts/{market_tick,transformed_candle,signal,event}/` are the (currently empty) homes for these
contract definitions — implement schema validation/types there rather than duplicating field definitions inside
each service.

## Local development standards (see `docs/architecture/Standards.txt`)

Apply these when building out any component (`services/signal-engine`, `services/api-orchestrator`,
`data-jobs/ingestion`, `data-jobs/transforms`):

- **Python 3.10.x** everywhere — no component uses a different minor version.
- **Poetry** per-component (`pyproject.toml` in each service/job dir), with lockfiles committed. Avoid ad-hoc
  pip installs outside Poetry.
- **Ruff** for linting, **Black** for formatting; pre-commit hooks should run both before commit.
- **Pyright** for type checking (baseline strictness for MVP); public functions in new core modules need type hints.
- **Config/env vars:** loaded via `pydantic-settings`; one tracked `.env.example` at repo root, real secrets in
  untracked `.env`. Prefix env vars by domain: `INGESTION_`, `SIGNAL_`, `API_`, `DB_`, `KAFKA_`, `AWS_`.
- **Testing:** pytest. Unit tests live alongside each component; cross-component tests go in top-level
  `tests/contract`, `tests/integration`, `tests/fixtures`. Test files named `test_<feature>.py`. Required pytest
  markers: `unit`, `integration`, `contract`, `slow`.
- **Quality gate before merge:** Black clean, Ruff clean, unit + contract tests passing. Integration tests may
  be reserved for the merge/main pipeline if costly.
- Any change to these standards must be reflected in `docs/architecture/Standards.txt` in the same PR.
