#!/usr/bin/env python3
"""
Prompt 2.2 — Test 2.2 Exception Flow

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 2.2:
- Test the complete exception lifecycle from request to approval
- Execute multiple unit tests in sequence
- Query Postgres database to verify exception handling results
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Reset database (test_0_1_reset)
2. Test registry sync (test_1_1_registry)
3. Test finding ingestion (test_1_2_ingestion)
4. Wait 5 seconds
5. Create exception request via webhook
6. Extract exceptionId from response or query database
7. Approve exception via webhook
8. Wait 3 seconds
9. Query Postgres: SELECT status, exception_active FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
10. Query Postgres: SELECT status, approved_by FROM exceptions WHERE exception_id = [extracted_id];

EXPECTED RESULTS:
- Exception request creates an exception record with status='requested'
- Exception approval sets status='active' and approved_by='compliance-admin@example.com'
- Finding status changes from 'open' to 'risk_accepted'
- Finding exception_active flag becomes true

EXPECTED OUTPUT FORMAT:
{
  "test_id": "2.2",
  "test_name": "exception_lifecycle",
  "status": "PASS or FAIL",
  "exception_approved": true,
  "finding_risk_accepted": true,
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
FIXTURES_DIR = "D:\web project\AxiomOps\Tests\fixtures"

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

def get_webhook(params=None):
    url = f"{N8N_URL}/webhook/complianceops-exception-decision"
    try:
        r = requests.get(url, params=params, timeout=30)
        return {"status": r.status_code, "json": r.json() if r.text else {}}
    except Exception as e:
        return {"status": 0, "error": str(e)}

# ==================== FIXTURE LOADER ====================
def load_fixture(name):
    with open(f"{FIXTURES_DIR}/{name}", "r") as f:
        return json.load(f)

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
    payload = load_fixture("registry_valid.json")
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

def test_1_2_ingestion():
    """Test finding ingestion."""
    payload = load_fixture("finding_failed_high.json")
    resp = post_webhook("complianceops-finding-ingestion", payload,
                        headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    time.sleep(5)
    db = DB()
    finding = db.query_one("SELECT status, severity, occurrence_count FROM findings WHERE finding_key = %s",
                           ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    evidence = db.query_all("SELECT * FROM evidence_events WHERE run_id = %s", ("RUN-TEST-001",))
    db.close()
    return {
        "status": "PASS" if finding and finding[0] == "open" and len(evidence) == 1 else "FAIL",
        "finding_status": finding[0] if finding else None,
        "finding_severity": finding[1] if finding else None,
        "occurrence_count": finding[2] if finding else None,
        "evidence_count": len(evidence)
    }

# ==================== MAIN IMPLEMENTATION ====================
def main():
    """Execute the exact steps from Prompt 2.2"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 2.2")
    print("TASK: Test the complete exception lifecycle from request to approval.")
    print("=" * 60)
    print()
    
    # Step 1: Reset database (test_0_1_reset)
    print("EXACT STEPS:")
    print("1. Reset database (test_0_1_reset)")
    
    reset_result = test_0_1_reset()
    print(f"   ✅ Database reset: {reset_result.get('status', 'UNKNOWN')}")
    
    if reset_result.get("status") != "PASS":
        error_result = {
            "test_id": "2.2",
            "test_name": "exception_lifecycle",
            "status": "FAIL",
            "exception_approved": False,
            "finding_risk_accepted": False,
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
            "test_id": "2.2",
            "test_name": "exception_lifecycle",
            "status": "FAIL",
            "exception_approved": False,
            "finding_risk_accepted": False,
            "notes": "Registry sync failed"
        }
        print("\n❌ Registry sync failed")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 3: Test finding ingestion (test_1_2_ingestion)
    print("3. Test finding ingestion (test_1_2_ingestion)")
    
    ingestion_result = test_1_2_ingestion()
    print(f"   ✅ Finding ingestion: {ingestion_result.get('status', 'UNKNOWN')}")
    
    if ingestion_result.get("status") != "PASS":
        error_result = {
            "test_id": "2.2",
            "test_name": "exception_lifecycle",
            "status": "FAIL",
            "exception_approved": False,
            "finding_risk_accepted": False,
            "notes": "Finding ingestion failed"
        }
        print("\n❌ Finding ingestion failed")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 4: Wait 5 seconds
    print("4. Wait 5 seconds.")
    time.sleep(5)
    
    # Step 5: Create exception request via webhook
    print("5. Create exception request via webhook")
    
    req_payload = load_fixture("exception_request.json")
    req_resp = post_webhook("complianceops-exception-request", req_payload)
    print(f"   ✅ Exception request response status: {req_resp['status']}")
    
    # Extract exceptionId from response or query database
    exception_id = None
    if req_resp.get("json") and "exceptionId" in req_resp["json"]:
        exception_id = req_resp["json"]["exceptionId"]
        print(f"   ✅ Exception ID from response: {exception_id}")
    else:
        print("   ⚠️  Exception ID not in response, querying database...")
        db = DB()
        row = db.query_one("SELECT exception_id FROM exceptions WHERE finding_key = %s ORDER BY created_at DESC",
                           ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
        db.close()
        exception_id = row[0] if row else None
        print(f"   ✅ Exception ID from database: {exception_id}")
    
    if not exception_id:
        error_result = {
            "test_id": "2.2",
            "test_name": "exception_lifecycle",
            "status": "FAIL",
            "exception_approved": False,
            "finding_risk_accepted": False,
            "notes": "Could not get exceptionId"
        }
        print("\n❌ Could not get exceptionId")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 6: Approve exception via webhook
    print("6. Approve exception via webhook")
    
    approve_resp = get_webhook(params={"exceptionId": exception_id, "decision": "approve"})
    print(f"   ✅ Exception approval response status: {approve_resp['status']}")
    
    # Step 7: Wait 3 seconds
    print("7. Wait 3 seconds.")
    time.sleep(3)
    
    # Step 8: Query Postgres: SELECT status, exception_active FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("8. Query Postgres: SELECT status, exception_active FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    db = DB()
    try:
        finding_result = db.query_one(
            "SELECT status, exception_active FROM findings WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Finding query returned: {finding_result}")
    except Exception as e:
        error_result = {
            "test_id": "2.2",
            "test_name": "exception_lifecycle",
            "status": "FAIL",
            "exception_approved": False,
            "finding_risk_accepted": False,
            "notes": f"Finding query failed: {e}"
        }
        print(f"\n❌ Finding query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    # Step 9: Query Postgres: SELECT status, approved_by FROM exceptions WHERE exception_id = [extracted_id];
    print("9. Query Postgres: SELECT status, approved_by FROM exceptions WHERE exception_id =", exception_id)
    
    try:
        exception_result = db.query_one(
            "SELECT status, approved_by FROM exceptions WHERE exception_id = %s",
            (exception_id,)
        )
        print(f"   ✅ Exception query returned: {exception_result}")
    except Exception as e:
        error_result = {
            "test_id": "2.2",
            "test_name": "exception_lifecycle",
            "status": "FAIL",
            "exception_approved": False,
            "finding_risk_accepted": False,
            "notes": f"Exception query failed: {e}"
        }
        print(f"\n❌ Exception query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    db.close()
    
    # EXPECTED RESULTS verification
    print("\n📊 Verifying expected results...")
    
    if finding_result is None:
        error_result = {
            "test_id": "2.2",
            "test_name": "exception_lifecycle",
            "status": "FAIL",
            "exception_approved": False,
            "finding_risk_accepted": False,
            "notes": "No finding found for the specified key"
        }
        print("\n❌ No finding found for the specified key")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    if exception_result is None:
        error_result = {
            "test_id": "2.2",
            "test_name": "exception_lifecycle",
            "status": "FAIL",
            "exception_approved": False,
            "finding_risk_accepted": False,
            "notes": "No exception found for the specified ID"
        }
        print("\n❌ No exception found for the specified ID")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Extract results
    finding_status = finding_result[0]
    finding_exception_active = finding_result[1]
    
    exception_status = exception_result[0]
    approved_by = exception_result[1]
    
    # Determine status
    exception_approved = exception_status == "active" and approved_by == "compliance-admin@example.com"
    finding_risk_accepted = finding_status == "risk_accepted" and finding_exception_active == True
    
    status = "PASS" if (exception_approved and finding_risk_accepted) else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "2.2",
        "test_name": "exception_lifecycle",
        "status": status,
        "exception_approved": exception_approved,
        "finding_risk_accepted": finding_risk_accepted,
        "notes": ""
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Finding status: {finding_status} (expected: risk_accepted)")
    print(f"   - Finding exception_active: {finding_exception_active} (expected: True)")
    print(f"   - Exception status: {exception_status} (expected: active)")
    print(f"   - Approved by: {approved_by} (expected: compliance-admin@example.com)")
    print(f"   - Exception approved: {exception_approved}")
    print(f"   - Finding risk accepted: {finding_risk_accepted}")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 2.2 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)