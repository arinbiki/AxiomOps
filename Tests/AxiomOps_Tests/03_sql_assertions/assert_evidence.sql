-- ASSERT: Evidence events
-- 1. Assert no duplicate (run_id, finding_key)
SELECT run_id, finding_key, COUNT(*) as cnt
FROM evidence_events
GROUP BY run_id, finding_key
HAVING COUNT(*) > 1;

-- 2. Assert evidence sequence
SELECT finding_key, run_id, passed, collected_at
FROM evidence_events
WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2'
ORDER BY collected_at DESC;

-- 3. Assert redaction (no raw tokens)
SELECT id, raw_data::text
FROM evidence_events
WHERE raw_data::text LIKE '%token%' OR raw_data::text LIKE '%password%' OR raw_data::text LIKE '%secret%';
