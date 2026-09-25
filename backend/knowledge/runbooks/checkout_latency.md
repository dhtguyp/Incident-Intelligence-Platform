---
document_id: runbook-checkout-latency
document_type: runbook
service: checkout-api
timestamp: 2026-08-02T09:00:00Z
---
# Checkout latency triage

Inspect P99 latency, error rate, dependency health, and deployments in the hour before the alert. If database acquisition timeouts appear with rising PostgreSQL connections, investigate database connection pool exhaustion before treating the checkout API as the primary cause.
