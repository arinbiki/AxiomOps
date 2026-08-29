# AxiomOps Test Runbook

## Prerequisites
- n8n self-hosted running on localhost:5678
- PostgreSQL running with AxiomOps schema applied
- All 11 core workflows imported and named exactly as generated
- Test workflows imported from `02_n8n_test_workflows/`

## Test Execution Order

### Phase 0: One-Time Setup
1. Import `test_master_unit_smoke.json` into n8n
2. Import `test_stress_batch_ingestion.json` into n8n
3. Import `test_race_condition.json` into n8n
4. Create Postgres credential in n8n if not already done
5. Assign Postgres credential to ALL Postgres nodes in test workflows

### Phase 1: Unit + Smoke Tests
1. Open Copilot Chat
2. Run Prompt Chain 1 (Environment Setup)
3. Run Prompt Chain 2 (Database Preparation)
4. Manually trigger `TEST_master_unit_smoke` workflow in n8n
5. Check the `Report_Output` node for final JSON result
6. If any FAIL, run Prompt Chain 7 (Debug Failure Analysis)

### Phase 2: Stress Tests
1. Trigger `TEST_stress_batch_ingestion` workflow
2. Default batch size is 100. To test 500 or 1000, edit the `Config` node batchSize value
3. Check `Stress_End` node for report JSON
4. Expected: `status: "PASS"`, `duplicatesFound: 0`, `evidenceInserted` equals batchSize

### Phase 3: Race Condition Tests
1. Trigger `TEST_race_condition` workflow
2. This sends 5 identical requests simultaneously
3. Check `Race_End` node for result
4. Expected: `test_race_condition: "PASS"` (occurrence_count must be 1)

### Phase 4: Manual API Tests (Optional)
Use the fixtures in `01_fixtures/` with curl:

```bash
# Registry sync
curl -X POST http://localhost:5678/webhook/complianceops-registry-sync   -H "Content-Type: application/json"   -d @01_fixtures/registry_valid.json

# Failed finding
curl -X POST http://localhost:5678/webhook/complianceops-finding-ingestion   -H "Content-Type: application/json"   -H "X-COMPLIANCEOPS-TOKEN: test-token-123"   -d @01_fixtures/findings_single_fail.json
```

### Phase 5: SQL Verification
After any test, run queries from `03_sql_assertions/` to verify state.

## Interpreting Results

| Result | Meaning | Action |
|--------|---------|--------|
| ALL_PASS | All 8 smoke tests passed | Ready for production |
| HAS_FAILURES | One or more tests failed | Run debug prompt chain |
| stress PASS | No duplicates, all evidence processed | Scale-ready |
| stress FAIL | Duplicates or missing evidence | Check Split In Batches settings |
| race PASS | Concurrent requests handled safely | Thread-safe |
| race FAIL | Duplicate rows or wrong occurrence_count | Check ON CONFLICT clauses |

## Known Limitations
- Jira tickets are sent to a mock URL during testing
- Slack/Discord alerts go to a mock webhook
- Ollama calls may timeout; the suite should still pass (test 09 fallback)
- Aging Digest (Workflow 07) is schedule-triggered; test it by manually triggering or waiting for schedule
