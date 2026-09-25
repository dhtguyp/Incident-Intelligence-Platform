---
document_id: service-postgres-primary
document_type: service_doc
service: postgres-primary
timestamp: 2026-09-01T00:00:00Z
---
# PostgreSQL primary service documentation

The primary database permits 200 client connections. An active connection warning begins at 190. Connection saturation queues new client requests until sessions close or capacity is restored.
