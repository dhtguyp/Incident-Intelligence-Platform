---
document_id: postmortem-auth-sessions
document_type: postmortem
service: user-api
timestamp: 2026-07-23T10:00:00Z
---
# Authentication session failures

A signing-key rollout caused invalid session tokens. Error rates rose immediately after deployment with no database connection pressure.
