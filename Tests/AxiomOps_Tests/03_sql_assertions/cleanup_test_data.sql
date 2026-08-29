-- CLEANUP: Remove all test data before/after test runs
DELETE FROM audit_log WHERE payload::text LIKE '%test%' OR created_at > now() - interval '1 hour';
DELETE FROM remediation_tasks WHERE finding_key LIKE '%TEST%' OR finding_key LIKE '%stress%' OR created_at > now() - interval '1 hour';
DELETE FROM exceptions WHERE finding_key LIKE '%TEST%' OR finding_key LIKE '%stress%' OR created_at > now() - interval '1 hour';
DELETE FROM evidence_events WHERE run_id LIKE '%TEST%' OR run_id LIKE '%STRESS%' OR collected_at > now() - interval '1 hour';
DELETE FROM findings WHERE finding_key LIKE '%TEST%' OR finding_key LIKE '%stress%' OR first_seen > now() - interval '1 hour';
DELETE FROM assets WHERE asset_id LIKE '%TEST%' OR updated_at > now() - interval '1 hour';
DELETE FROM controls WHERE control_id LIKE '%TEST%' OR updated_at > now() - interval '1 hour';
