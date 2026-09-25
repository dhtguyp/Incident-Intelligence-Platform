---
document_id: postmortem-payment-gateway
document_type: postmortem
service: payments-api
timestamp: 2026-07-14T12:00:00Z
---
# Payment gateway degradation

A third-party gateway timeout raised payments-api errors. Database connection usage remained normal, distinguishing this event from connection-pool exhaustion.
