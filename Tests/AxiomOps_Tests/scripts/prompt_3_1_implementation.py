#!/usr/bin/env python3
"""
Prompt 3.1 — Test 3.1 Bulk Ingestion

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 3.1:
- Test bulk ingestion of 50 findings
- Execute multiple unit tests in sequence
- Query Postgres database to verify bulk processing results
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Reset database (test_0_1_reset)
2. Test registry sync (test_1_1_registry)
3. Loop 50 times:
   a. Create finding payload with unique runId
   b. Send via POST to http://localhost:5678/webhook/complianceops-finding-ingestion
   c. Wait 0.2 seconds between each
4. Wait 30 seconds for processing
5. Query Postgres: SELECT COUNT(*) FROM evidence_events WHERE run_id LIKE 'RUN-STRESS-%';
6. Query Postgres: SELECT occurrence_count FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
7. Query Postgres: SELECT COUNT(*) FROM remediation_tasks;

EXPECTED RESULTS:
- evidence_events table has 50 rows with run_id like 'RUN-STRESS-%'
- findings table has 1 row with occurrence_count >= 50
- remediation_tasks table has 1 row

EXPECTED OUTPUT FORMAT:
{
  "test_id": "3.1",
  "test_name": "bulk_ingestion_50",
  "status": "PASS or FAIL",
  "evidence_count": 0,
  "occurrence_count": 0,
  "ticket_count": 0,
  "notes": ""
}

DO NOT:
- Skip any step in the sequence
- Assume success without checking the database
"""

import json
import time
import psycopg2
import requests
from datetime import datetime

# ==================== CONFIGURATION ====================
# These should match your actual environment
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "n8n"
POSTGRES_USER = "n8n"
POSTGRES_PASSWORD = "change-me"
N8N_URL = "http://localhost:5678"
INGEST_TOKEN = "change-me"

# ==================== DATABASE HELPER ====================
class DB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=POSTGRES_HOST, port=POSTGRES_PORT, dbname=POSTGRES_DB,
            user=POSTGRES_USER, password=POSTGRES_PASSWORD
        )
        self.cur = self.conn.cursor()

    def query_one(self, sql, params=None):
        self.cur.execute(sql, params or ())
        return self.cur.fetchone()

    def query_all(self, sql, params=None):
        self.cur.execute(sql, params or ())
        return self.cur.fetchall()

    def execute(self, sql, params=None):
        self.cur.execute(sql, params or ())
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()

# ==================== HTTP HELPER ====================
def post_webhook(path, payload, headers=None):
    url = f"{N8N_URL}/webhook/{path}"
    h = headers or {}
    try:
        r = requests.post(url, json=payload, headers=h, timeout=30)
        return {"status": r.status_code, "json": r.json() if r.text else {}}
    except Exception as e:
        return {"status": 0, "error": str(e)}

# ==================== SUB-TESTS ====================
def test_0_1_reset():
    """Reset database to clean state."""
    db = DB()
    try:
        db.execute("TRUNCATE evidence_events, findings, exceptions, remediation_tasks, audit_log RESTART IDENTITY")
        db.execute("UPDATE assets SET active = false")
        db.execute("UPDATE controls SET active = false")
        row = db.query_one("SELECT COUNT(*) FROM findings")
        count = row[0] if row else -1
        db.close()
        return {"status": "PASS" if count == 0 else "FAIL", "findings_count": count}
    except Exception as e:
        db.close()
        return {"status": "FAIL", "notes": str(e)}

def test_1_1_registry():
    """Test registry sync."""
    payload = {
        "source": "ComplianceGuardPro", "runId": "RUN-REGISTRY", "framework": "SOC2",
        "timestamp": "2026-08-24T09:00:00Z",
        "evidence": [
            {"controlId": "CC6.6", "resourceId": "arn:aws:s3:::prod-data-lake", "service": "aws", "passed": True, "severity": "high"},
            {"controlId": "CC7.2", "resourceId": "arn:aws:s3:::prod-data-lake", "service": "aws", "passed": True, "severity": "medium"}
        ]
    }
    resp = post_webhook("complianceops-registry-sync", payload)
    time.sleep(2)
    db = DB()
    assets = db.query_all("SELECT asset_id, owner_email FROM assets WHERE active = true")
    controls = db.query_all("SELECT control_id, framework FROM controls WHERE active = true")
    db.close()
    return {
        "status": "PASS" if len(assets) == 2 and len(controls) == 2 else "FAIL",
        "assets_count": len(assets), "controls_count": len(controls)
    }

# ==================== MAIN IMPLEMENTATION ====================
def main():
    """Execute the exact steps from Prompt 3.1"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 3.1")
    print("TASK: Test bulk ingestion of 50 findings.")
    print("=" * 60)
    print()
    
    # Step 1: Reset database (test_0_1_reset)
    print("EXACT STEPS:")
    print("1. Reset database (test_0_1_reset)")
    
    reset_result = test_0_1_reset()
    print(f"   ✅ Database reset: {reset_result.get('status', 'UNKNOWN')}")
    
    if reset_result.get("status") != "PASS":
        error_result = {
            "test_id": "3.1",
            "test_name": "bulk_ingestion_50",
            "status": "FAIL",
            "evidence_count": 0,
            "occurrence_count": 0,
            "ticket_count": 0,
            "notes": "Database reset failed"
        }
        print("\n❌ Database reset failed")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 2: Test registry sync (test_1_1_registry)
    print("2. Test registry sync (test_1_1_registry)")
    
    registry_result = test_1_1_registry()
    print(f"   ✅ Registry sync: {registry_result.get('status', 'UNKNOWN')}")
    
    if registry_result.get("status") != "PASS":
        error_result = {
            "test_id": "3.1",
            "test_name": "bulk_ingestion_50",
            "status": "FAIL",
            "evidence_count": 0,
            "occurrence_count": 0,
            "ticket_count": 0,
            "notes": "Registry sync failed"
        }
        print("\n❌ Registry sync failed")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 3: Loop 50 times
    print("3. Loop 50 times:")
    print("   a. Create finding payload with unique runId")
    print("   b. Send via POST to http://localhost:5678/webhook/complianceops-finding-ingestion")
    print("   c. Wait 0.2 seconds between each")
    
    for i in range(1, 51):
        payload = {
            "source": "ComplianceGuardPro", "runId": f"RUN-STRESS-{i:03d}", "framework": "SOC2",
            "timestamp": "2026-08-24T09:00:00Z",
            "evidence": [{"controlId": "CC6.6", "resourceId": "arn:aws:s3:::prod-data-lake", "service": "aws", "passed": False, "severity": "medium"}]
        }
        
        resp = post_webhook("complianceops-finding-ingestion", payload,
                            headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
        print(f"   ✅ Iteration {i}/50: HTTP status {resp['status']}")
        
        if i < 50:
            time.sleep(0.2)
    
    # Step 4: Wait 30 seconds for processing
    print("4. Wait 30 seconds for processing.")
    time.sleep(30)
    
    # Step 5: Query Postgres: SELECT COUNT(*) FROM evidence_events WHERE run_id LIKE 'RUN-STRESS-%';
    print("5. Query Postgres: SELECT COUNT(*) FROM evidence_events WHERE run_id LIKE 'RUN-STRESS-%';")
    
    db = DB()
    try:
        evidence_result = db.query_one("SELECT COUNT(*) FROM evidence_events WHERE run_id LIKE %s", ("RUN-STRESS-%",))
        print(f"   ✅ Evidence query returned: {evidence_result}")
    except Exception as e:
        error_result = {
            "test_id": "3.1",
            "test_name": "bulk_ingestion_50",
            "status": "FAIL",
            "evidence_count": 0,
            "occurrence_count": 0,
            "ticket_count": 0,
            "notes": f"Evidence query failed: {e}"
        }
        print(f"\n❌ Evidence query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    # Step 6: Query Postgres: SELECT occurrence_count FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("6. Query Postgres: SELECT occurrence_count FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    try:
        finding_result = db.query_one("SELECT occurrence_count FROM findings WHERE finding_key = %s",
                                       ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
        print(f"   ✅ Finding query returned: {finding_result}")
    except Exception as e:
        error_result = {
            "test_id": "3.1",
            "test_name": "bulk_ingestion_50",
            "status": "FAIL",
            "evidence_count": evidence_result[0] if evidence_result else 0,
            "occurrence_count": 0,
            "ticket_count": 0,
            "notes": f"Finding query failed: {e}"
        }
        print(f"\n❌ Finding query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    # Step 7: Query Postgres: SELECT COUNT(*) FROM remediation_tasks;
    print("7. Query Postgres: SELECT COUNT(*) FROM remediation_tasks;")
    
    try:
        task_result = db.query_one("SELECT COUNT(*) FROM remediation_tasks")
        print(f"   ✅ Task query returned: {task_result}")
    except Exception as e:
        error_result = {
            "test_id": "3.1",
            "test_name": "bulk_ingestion_50",
            "status": "FAIL",
            "evidence_count": evidence_result[0] if evidence_result else 0,
            "occurrence_count": finding_result[0] if finding_result else 0,
            "ticket_count": 0,
            "notes": f"Task query failed: {e}"
        }
        print(f"\n❌ Task query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    db.close()
    
    # EXPECTED RESULTS verification
    print("\n📊 Verifying expected results...")
    
    if evidence_result is None:
        error_result = {
            "test_id": "3.1",
            "test_name": "bulk_ingestion_50",
            "status": "FAIL",
            "evidence_count": 0,
            "occurrence_count": 0,
            "ticket_count": 0,
            "notes": "Evidence query returned no results"
        }
        print("\n❌ Evidence query returned no results")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    if finding_result is None:
        error_result = {
            "test_id": "3.1",
            "test_name": "bulk_ingestion_50",
            "status": "FAIL",
            "evidence_count": evidence_result[0] if evidence_result else 0,
            "occurrence_count": 0,
            "ticket_count": 0,
            "notes": "Finding query returned no results"
        }
        print("\n❌ Finding query returned no results")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    if task_result is None:
        error_result = {
            "test_id": "3.1",
            "test_name": "bulk_ingestion_50",
            "status": "FAIL",
            "evidence_count": evidence_result[0] if evidence_result else 0,
            "occurrence_count": finding_result[0] if finding_result else 0,
            "ticket_count": 0,
            "notes": "Task query returned no results"
        }
        print("\n❌ Task query returned no results")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Extract results
    evidence_count = evidence_result[0]
    occurrence_count = finding_result[0]
    ticket_count = task_result[0]
    
    # Determine status
    status = "PASS" if (evidence_count == 50 and occurrence_count >= 50 and ticket_count == 1) else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "3.1",
        "test_name": "bulk_ingestion_50",
        "status": status,
        "evidence_count": evidence_count,
        "occurrence_count": occurrence_count,
        "ticket_count": ticket_count,
        "notes": ""
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Evidence count: {evidence_count} (expected: 50)")
    print(f"   - Occurrence count: {occurrence_count} (expected: >= 50)")
    print(f"   - Ticket count: {ticket_count} (expected: 1)")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 3.1 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)