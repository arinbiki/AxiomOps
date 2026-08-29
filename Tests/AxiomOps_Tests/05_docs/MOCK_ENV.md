# Mock Environment for Testing

## Required Environment Variables

```bash
# Core security
COMPLIANCEOPS_INGEST_TOKEN=test-token-123

# Fallback contacts
COMPLIANCE_ADMIN_EMAIL=test-admin@axiomops.local
COMPLIANCE_ESCALATION_EMAIL=test-escalation@axiomops.local

# URLs
PUBLIC_WEBHOOK_URL=http://localhost:5678
ALERT_WEBHOOK_URL=http://localhost:5678/webhook/test-alert

# Jira (mocked during tests)
JIRA_URL=http://localhost:5678/mock-jira
JIRA_PROJECT_KEY=TEST

# Closure logic
REQUIRED_CONSECUTIVE_PASSES=1
```

## How to Set in Self-Hosted n8n

### Docker Compose
Add to `environment:` section of n8n service.

### systemd / direct
Export before starting n8n:
```bash
export COMPLIANCEOPS_INGEST_TOKEN=test-token-123
export COMPLIANCE_ADMIN_EMAIL=test-admin@axiomops.local
# ... etc
```

### n8n UI (not recommended for secrets)
Use Settings -> Variables for non-sensitive values only.

## Mock Endpoints

During testing, these endpoints should be available or mocked:

| Endpoint | Purpose | Mock Response |
|----------|---------|---------------|
| `POST /webhook/test-alert` | Error/slack notifications | `{"ok": true}` |
| `POST /mock-jira/rest/api/2/issue` | Jira ticket creation | `{"id": "TEST-123", "key": "TEST-123"}` |
| `POST /api/chat` | Ollama AI | `{"model": "qwen2.5:3b", "message": {"role": "assistant", "content": "Mock summary."}}` |

## Creating Mock Endpoints in n8n

If you don't have external mock services, create simple n8n workflows:

### Mock Alert Webhook
- Trigger: Webhook `POST /webhook/test-alert`
- Node: Respond to Webhook (200, `{"ok": true}`)

### Mock Jira
- Trigger: Webhook `POST /mock-jira/rest/api/2/issue`
- Node: Respond to Webhook (200, `{"id": "TEST-123", "key": "TEST-123"}`)

### Mock Ollama
- Trigger: Webhook `POST /api/chat`
- Node: Respond to Webhook (200, `{"model": "qwen2.5:3b", "message": {"role": "assistant", "content": "Mock AI summary."}}`)
