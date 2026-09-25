---
document_id: runbook-redis-failover
document_type: runbook
service: redis-cache
timestamp: 2026-08-04T09:00:00Z
---
# Redis failover response

Check memory pressure, replication state, and client reconnect volume. A cache failover may increase database traffic, so monitor PostgreSQL connections during recovery.
