-- ASSERT: Findings table state after test
-- Run these after each test scenario to verify outcomes

-- 1. Assert finding exists with correct key
SELECT 
  finding_key,
  status,
  severity,
  owner_email,
  owner_status,
  missing_owner,
  risk_score,
  priority,
  occurrence_count,
  repeated_failure,
  exception_active,
  jira_issue_key
FROM findings
WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';

-- 2. Assert occurrence count after duplicate runs
SELECT finding_key, occurrence_count, status
FROM findings
WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';

-- 3. Assert missing owner fallback
SELECT finding_key, missing_owner, owner_email, owner_status
FROM findings
WHERE finding_key LIKE '%orphan-instance%';

-- 4. Assert critical production finding has P1 + short SLA
SELECT finding_key, priority, risk_score, sla_due
FROM findings
WHERE severity = 'critical' AND status IN ('open','reopened');

-- 5. Assert closed finding after pass evidence
SELECT finding_key, status, closed_at, closure_reason
FROM findings
WHERE status = 'closed';

-- 6. Assert risk_accepted finding with active exception
SELECT finding_key, status, exception_active
FROM findings
WHERE status = 'risk_accepted';
