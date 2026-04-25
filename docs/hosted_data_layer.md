# CommerceLens Hosted Data Layer and Connectors

CommerceLens v0.6 introduces the foundation for hosted deployments and downstream data workflows.

The project still works as a local-first CLI and SDK, but the internals now support pluggable storage, optional PostgreSQL, product dataset import/export, webhook event envelopes, and cross-store product matching.

## Storage backends

The default backend is still SQLite:

```python
from commercelens import StorageConfig, make_snapshot_backend

backend = make_snapshot_backend(StorageConfig(backend="sqlite", sqlite_path="prices.db"))
```

For hosted deployments, install the Postgres extra:

```bash
pip install -e ".[postgres]"
```

Then use:

```python
from commercelens import StorageConfig, make_snapshot_backend

backend = make_snapshot_backend(
    StorageConfig(
        backend="postgres",
        postgres_dsn="postgresql://user:password@localhost:5432/commercelens",
    )
)
```

You can also set:

```bash
export COMMERCELENS_POSTGRES_DSN=postgresql://user:password@localhost:5432/commercelens
```

## Monitoring with a backend

```python
from commercelens import StorageConfig, monitor_product

result = monitor_product(
    "https://example.com/products/sample",
    storage_config=StorageConfig(backend="sqlite", sqlite_path="prices.db"),
)
```

This preserves the old API too:

```python
from commercelens import monitor_product

result = monitor_product("https://example.com/products/sample", db_path="prices.db")
```

## Dataset connectors

Load product records from text, CSV, JSON, or JSONL:

```python
from commercelens import load_product_records

records = load_product_records("products.csv")
print(records.records)
```

Export tracked product snapshots:

```bash
commercelens export-history --db prices.db --out latest_products.jsonl
commercelens export-history --db prices.db --out latest_products.csv
```

Normalize external records:

```bash
commercelens load-records products.csv --out normalized.json
```

Supported input fields include:

- `url`
- `source_url`
- `canonical_url`
- `product_key`
- `name`
- `title`
- `brand`
- `amount`
- `price`
- `currency`
- `availability`
- `image_url`
- `image`

## Product matching

CommerceLens can compare products across two datasets:

```bash
commercelens match-records shop_a.csv shop_b.csv --threshold 0.72 --out matches.json
```

Python SDK:

```python
from commercelens import ProductRecord, match_products

left = [ProductRecord(name="Nike Air Max 90", brand="Nike", amount=120, currency="USD")]
right = [ProductRecord(name="Nike Air Max 90 Shoes", brand="Nike", amount=125, currency="USD")]

matches = match_products(left, right, threshold=0.72)
print(matches.matches[0].score)
```

The current matcher is intentionally transparent. It combines name similarity, token overlap, brand match, currency match, price similarity, and domain hints. This gives developers a reliable baseline before introducing embedding-based matching later.

## API endpoints

Normalize product records:

```bash
curl -X POST http://localhost:8000/v1/records/normalize \
  -H 'Content-Type: application/json' \
  -d '{"records": [{"url": "https://example.com/p/1", "name": "Sample Product"}]}'
```

Match products:

```bash
curl -X POST http://localhost:8000/v1/match/products \
  -H 'Content-Type: application/json' \
  -d '{
    "left": [{"name": "Nike Air Max 90", "brand": "Nike", "amount": 120, "currency": "USD"}],
    "right": [{"name": "Nike Air Max 90 Shoes", "brand": "Nike", "amount": 125, "currency": "USD"}],
    "threshold": 0.72
  }'
```

## Webhook envelopes

Alert events can now be converted into a stable webhook envelope:

```python
from commercelens import alert_event_to_webhook

envelope = alert_event_to_webhook(alert_event)
```

This is useful for future hosted queues, team notification routing, Zapier/Make/Pipedream connectors, and customer-owned event ingestion.

## Why this phase matters

Before v0.6, CommerceLens was a local scraper and monitor. With v0.6, it becomes a developer platform foundation:

- local SQLite for individual developers
- optional Postgres for hosted deployments
- normalized import/export records
- API and CLI matching workflows
- stable event envelopes for integrations

The next natural phase is a job queue and worker system so product monitoring can run continuously at scale.
