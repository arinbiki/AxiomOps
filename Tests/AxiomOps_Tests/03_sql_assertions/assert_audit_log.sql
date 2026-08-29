-- ASSERT: Audit trail
-- 1. Assert exception decisions logged
SELECT entity_type, entity_id, action, actor
FROM audit_log
WHERE entity_type = 'exception'
ORDER BY created_at DESC;

-- 2. Assert finding closure logged
SELECT entity_type, entity_id, action, actor
FROM audit_log
WHERE entity_type = 'finding' AND action = 'closed'
ORDER BY created_at DESC;
