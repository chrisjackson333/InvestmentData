# Raw market data CSV schema (NQ1!, 1-minute bars)

This is the input format the ingestion CSV adapter (`adapters/csv.py`) accepts. The executable
source of truth is `shared/contracts/market_tick/models.py::RawMarketBar` — this document
describes the on-disk CSV shape that gets parsed into that model.

## Filename convention

```
NQ1!_1min_YYYYMMDD.csv
```

One file per symbol per trading day. MVP only ever produces `NQ1!` files.

## Columns (header row required, comma-delimited, UTF-8)

| column      | type                        | notes                                    |
|-------------|-----------------------------|-------------------------------------------|
| `timestamp` | ISO8601 UTC, `Z` suffix     | 1-minute bar open time, e.g. `2026-09-04T13:31:00Z` |
| `open`      | decimal                     | must be > 0                              |
| `high`      | decimal                     | must be >= max(open, close, low)         |
| `low`       | decimal                     | must be <= min(open, close, high)        |
| `close`     | decimal                     | must be > 0                              |
| `volume`    | non-negative integer        |                                           |
| `symbol`    | string, constant `NQ1!`     | included per-row so files are self-describing |

## Raw-zone landing convention (local dev stand-in for S3)

Validated bars and a per-batch quality report are written under:

```
{raw_zone_root}/{symbol}/{yyyy}/{mm}/{dd}/{source_batch_id}.jsonl
{raw_zone_root}/{symbol}/{yyyy}/{mm}/{dd}/{source_batch_id}.quality.json
```

This mirrors the intended S3 raw-zone prefix `s3://<bucket>/raw/{symbol}/{yyyy}/{mm}/{dd}/{batch_id}.csv`
without requiring AWS access in local development.
