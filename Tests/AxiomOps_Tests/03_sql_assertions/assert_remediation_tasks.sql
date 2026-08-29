-- ASSERT: Remediation tasks
-- 1. Assert ticket created for open finding
SELECT finding_key, ticket_key, status
FROM remediation_tasks
WHERE status = 'open';

-- 2. Assert no duplicate open tickets per finding
SELECT finding_key, COUNT(*) as open_count
FROM remediation_tasks
WHERE status = 'open'
GROUP BY finding_key
HAVING COUNT(*) > 1;

-- 3. Assert closed task after finding closure
SELECT finding_key, ticket_key, status
FROM remediation_tasks
WHERE status = 'closed';
