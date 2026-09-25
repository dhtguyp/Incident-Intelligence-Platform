---
document_id: postmortem-redis-oom
document_type: postmortem
service: redis-cache
timestamp: 2026-09-15T10:00:00Z
---
# Redis memory pressure

An eviction-policy configuration caused out-of-memory restarts. Checkout traffic saw cache misses, but database connections did not reach capacity.
