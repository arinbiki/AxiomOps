#!/usr/bin/env python3
"""
Prompt 2.3 — Test 2.3 Missing Owner

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 2.3:
- Test missing owner fallback logic
- Execute multiple unit tests in sequence
- Query Postgres database to verify missing owner handling
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Reset database (test_0_1_reset)
2. Test registry sync with missing owner (test_1_1_registry_missing_owner)
3. Wait 2 seconds
4. Create a finding for orphan bucket via webhook
5. Wait 5 seconds
6. Query Postgres: SELECT owner_email, owner_status, missing_owner FROM findings WHERE resource_id = 'arn:aws:s3:::orphan-bucket';

EXPECTED RESULTS:
- owner_email = null (no owner assigned)
- owner_status = 'missing_owner_fallback'
- missing_owner = true

EXPECTED OUTPUT FORMAT:
{
  "test_id": "2.3",
  "test_name": "missing_owner_fallback",
  "status": "PASS or FAIL",
  "fallback_owner_assigned": true,
  "owner_status": "",
  "missing_owner_flag": false,
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

def test_1_1_registry_missing_owner():
    """Test registry sync with missing owner."""
    payload = load_fixture("registry_missing_owner.json")
    resp = post_webhook("complianceops-registry-sync", payload)
    time.sleep(2)
    db = DB()
    assets = db.query_all("SELECT asset_id, owner_email FROM assets WHERE active = true")
    controls = db.query_all("SELECT control_id, framework FROM controls WHERE active = true")
    db.close()
    return {
        "status": "PASS" if len(assets) == 1 and len(controls) == 1 else "FAIL",
        "assets_count": len(assets), "controls_count": len(controls)
    }

# ==================== MAIN IMPLEMENTATION ====================
def main():
    """Execute the exact steps from Prompt 2.3"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 2.3")
    print("TASK: Test missing owner fallback logic.")
    print("=" * 60)
    print()
    
    # Step 1: Reset database (test_0_1_reset)
    print("EXACT STEPS:")
    print("1. Reset database (test_0_1_reset)")
    
    reset_result = test_0_1_reset()
    print(f"   ✅ Database reset: {reset_result.get('status', 'UNKNOWN')}")
    
    if reset_result.get("status") != "PASS":
        error_result = {
            "test_id": "2.3",
            "test_name": "missing_owner_fallback",
            "status": "FAIL",
            "fallback_owner_assigned": False,
            "owner_status": "",
            "missing_owner_flag": False,
            "notes": "Database reset failed"
        }
        print("\n❌ Database reset failed")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 2: Test registry sync with missing owner (test_1_1_registry_missing_owner)
    print("2. Test registry sync with missing owner (test_1_1_registry_missing_owner)")
    
    registry_result = test_1_1_registry_missing_owner()
    print(f"   ✅ Registry sync: {registry_result.get('status', 'UNKNOWN')}")
    
    if registry_result.get("status") != "PASS":
        error_result = {
            "test_id": "2.3",
            "test_name": "missing_owner_fallback",
            "status": "FAIL",
            "fallback_owner_assigned": False,
            "owner_status": "",
            "missing_owner_flag": False,
            "notes": "Registry sync failed"
        }
        print("\n❌ Registry sync failed")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 3: Wait 2 seconds
    print("3. Wait 2 seconds.")
    time.sleep(2)
    
    # Step 4: Create a finding for orphan bucket via webhook
    print("4. Create a finding for orphan bucket via webhook")
    
    finding_payload = {
        "source": "ComplianceGuardPro", "runId": "RUN-ORPHAN", "framework": "SOC2",
        "timestamp": "2026-08-24T09:00:00Z",
        "evidence": [{"controlId": "CC6.6", "resourceId": "arn:aws:s3:::orphan-bucket", "service": "aws", "passed": False, "severity": "high"}]
    }
    
    finding_resp = post_webhook("complianceops-finding-ingestion", finding_payload,
                                headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    print(f"   ✅ Finding creation response status: {finding_resp['status']}")
    
    # Step 5: Wait 5 seconds
    print("5. Wait 5 seconds.")
    time.sleep(5)
    
    # Step 6: Query Postgres: SELECT owner_email, owner_status, missing_owner FROM findings WHERE resource_id = 'arn:aws:s3:::orphan-bucket';
    print("6. Query Postgres: SELECT owner_email, owner_status, missing_owner FROM findings WHERE resource_id = 'arn:aws:s3:::orphan-bucket';")
    
    db = DB()
    try:
        result = db.query_one(
            "SELECT owner_email, owner_status, missing_owner FROM findings WHERE resource_id = %s",
            ("arn:aws:s3:::orphan-bucket",)
        )
        print(f"   ✅ Query returned: {result}")
    except Exception as e:
        error_result = {
            "test_id": "2.3",
            "test_name": "missing_owner_fallback",
            "status": "FAIL",
            "fallback_owner_assigned": False,
            "owner_status": "",
            "missing_owner_flag": False,
            "notes": f"Query failed: {e}"
        }
        print(f"\n❌ Query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    db.close()
    
    # EXPECTED RESULTS verification
    print("\n📊 Verifying expected results...")
    
    if result is None:
        error_result = {
            "test_id": "2.3",
            "test_name": "missing_owner_fallback",
            "status": "FAIL",
            "fallback_owner_assigned": False,
            "owner_status": "",
            "missing_owner_flag": False,
            "notes": "No finding found for the specified resource_id"
        }
        print("\n❌ No finding found for the specified resource_id")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Extract results
    owner_email = result[0]
    owner_status = result[1]
    missing_owner = result[2]
    
    # Determine status
    fallback_owner_assigned = owner_email is not None
    owner_status_match = owner_status == "missing_owner_fallback"
    missing_owner_flag = missing_owner == True
    
    status = "PASS" if (fallback_owner_assigned and owner_status_match and missing_owner_flag) else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "2.3",
        "test_name": "missing_owner_fallback",
        "status": status,
        "fallback_owner_assigned": fallback_owner_assigned,
        "owner_status": owner_status,
        "missing_owner_flag": missing_owner_flag,
        "notes": ""
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Owner email: {owner_email} (expected: null or empty)")
    print(f"   - Owner status: {owner_status} (expected: missing_owner_fallback)")
    print(f"   - Missing owner flag: {missing_owner} (expected: true)")
    print(f"   - Fallback owner assigned: {fallback_owner_assigned}")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 2.3 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)