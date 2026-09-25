---
document_id: service-checkout-api
document_type: service_doc
service: checkout-api
timestamp: 2026-09-01T00:00:00Z
---
# Checkout API service documentation

Checkout API processes orders through payments-api and writes order state to postgres-primary. Each request obtains a PostgreSQL connection from the application pool. Waiting for a connection raises P99 latency and can exhaust request timeouts.
