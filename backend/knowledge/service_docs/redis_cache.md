---
document_id: service-redis-cache
document_type: service_doc
service: redis-cache
timestamp: 2026-09-01T00:00:00Z
---
# Redis Cache service documentation

Redis Cache stores sessions and product lookups. Its failures create cache misses and increased backing-store reads, though it has no direct PostgreSQL connection pool.
