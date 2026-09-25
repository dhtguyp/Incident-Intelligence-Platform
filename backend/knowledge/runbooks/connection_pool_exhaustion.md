---
document_id: runbook-connection-pool
document_type: runbook
service: postgres-primary
timestamp: 2026-08-01T09:00:00Z
---
# Connection pool exhaustion

When PostgreSQL active connections approach the configured maximum, new requests queue while applications wait for a connection. Confirm active connections, identify recent application deployments, reduce traffic if needed, and roll back a suspected connection-management change. Checkout API latency and HTTP 5xx responses are expected downstream symptoms.
