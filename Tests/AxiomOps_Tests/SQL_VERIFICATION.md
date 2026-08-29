# AxiomOps SQL Verification Cheat Sheet

Run these after each test to verify state. Copy the exact query into your Postgres client.

---

## 1. Check Asset Registry
```sql
SELECT asset_id, resource_id, service, owner_email, criticality, environment
FROM assets
ORDER BY updated_at DESC;
```
**Expected after Test 01:** 2 rows (prod-data-lake, dev-data-lake)

---

## 2. Check Control Registry
```sql
SELECT control_id, framework, default_owner_email, default_sla_hours
FROM controls
ORDER BY updated_at DESC;
```
**Expected after Test 01:** 2 rows (CC6.6, CC7.2)

---

## 3. Check Evidence Events
```sql
SELECT run_id, finding_key, passed, collected_at
FROM evidence_events
ORDER BY collected_at DESC
LIMIT 10;
```
**Expected after Test 02:** Rows with run IDs RUN-TEST-001, RUN-TEST-002, etc.

---

## 4. Check Findings (the most important table)
```sql
SELECT
  finding_key,
  status,
  severity,
  owner_email,
  owner_status,
  missing_owner,
  risk_score,
  priority,
  sla_due,
  occurrence_count,
  repeated_failure,
  jira_issue_key,
  exception_active,
  closed_at,
  closure_reason
FROM findings
ORDER BY updated_at DESC;
```

**Expected states:**
- After failed ingestion: `status = 'open'`, `occurrence_count >= 1`
- After owner resolution: `owner_status` = 'resolved_asset_owner' or 'missing_owner_fallback'
- After risk prioritization: `risk_score` > 0, `priority` = P1/P2/P3/P4, `sla_due` is a future timestamp
- After exception approval: `status = 'risk_accepted'`, `exception_active = true`
- After closure: `status = 'closed'`, `closed_at` is set, `closure_reason` = 'consecutive_evidence_passed'

---

## 5. Check Exceptions
```sql
SELECT exception_id, finding_key, status, requested_by, approved_by, starts_at, expires_at
FROM exceptions
ORDER BY created_at DESC;
```

**Expected:**
- After request: `status = 'pending'`
- After approve: `status = 'active'`, `approved_by` is set, `expires_at` is future
- After reject: `status = 'rejected'`

---

## 6. Check Remediation Tasks
```sql
SELECT finding_key, ticket_system, ticket_key, status
FROM remediation_tasks
ORDER BY created_at DESC;
```

**Expected:**
- After remediation orchestrator: `status = 'open'`, `ticket_key` is not null
- After closure: `status = 'closed'`

---

## 7. Check Audit Log
```sql
SELECT entity_type, entity_id, action, actor, created_at
FROM audit_log
ORDER BY created_at DESC
LIMIT 20;
```

**Expected:** Records for exception approve/reject and finding closure.

---

## 8. Reset Database (USE WITH CAUTION)
```sql
-- Only for test environments
TRUNCATE evidence_events, findings, exceptions, remediation_tasks, audit_log RESTART IDENTITY;
UPDATE assets SET active = false;
UPDATE controls SET active = false;
```
