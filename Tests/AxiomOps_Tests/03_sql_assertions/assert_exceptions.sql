-- ASSERT: Exception lifecycle
-- 1. Assert pending exception
SELECT exception_id, finding_key, status, requested_by
FROM exceptions
WHERE status = 'pending';

-- 2. Assert active exception with expiry
SELECT exception_id, finding_key, status, approved_by, starts_at, expires_at
FROM exceptions
WHERE status = 'active';

-- 3. Assert rejected exception
SELECT exception_id, finding_key, status, approved_by
FROM exceptions
WHERE status = 'rejected';

-- 4. Assert expired exceptions
SELECT exception_id, finding_key, status, expires_at
FROM exceptions
WHERE status = 'active' AND expires_at <= now();
