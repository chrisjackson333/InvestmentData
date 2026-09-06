# shared

Cross-domain contract models (`contracts/`) and small utilities (`utils/`) used by more than one
service or job, so field definitions for the locked interfaces in
`docs/architecture/DomainContract.txt` live in exactly one place instead of being duplicated
per-component.

To consume this package from another component, add a Poetry path dependency:

```toml
investment-platform-shared = { path = "../../shared", develop = true }
```

then import as `from contracts.market_tick.models import RawMarketBar`, etc.
