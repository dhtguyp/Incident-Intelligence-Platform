---
document_id: runbook-payment-timeouts
document_type: runbook
service: payments-api
timestamp: 2026-08-03T09:00:00Z
---
# Payment timeout triage

Compare gateway response time with local request failures. Roll back only after correlating a deployment with the changed failure mode. Dependency failures can propagate to checkout requests.
