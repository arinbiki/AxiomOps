#!/usr/bin/env python3
"""
Prompt 4.1 — Test 4.1 Invalid Auth

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 4.1:
- Test invalid authentication handling
- Send finding with wrong token
- Verify evidence not created
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Load fixture D:\web project\AxiomOps\Tests\fixtures\finding_failed_high.json
2. Send it via POST to http://localhost:5678/webhook/complianceops-finding-ingestion with header X-COMPLIANCEOPS-TOKEN: wrong
3. Query Postgres: SELECT COUNT(*) FROM evidence_events WHERE run_id = 'RUN-TEST-001';

EXPECTED RESULTS:
- evidence_events table has 0 rows (evidence blocked)
- HTTP response status is not 200 (authentication failed)

EXPECTED OUTPUT FORMAT:
{
  "test_id": "4.1",
  "test_name": "invalid_auth",
  "status": "PASS or FAIL",
  "http_status": 0,
  "evidence_blocked": true,
  "notes": ""
}

DO NOT:
- Use the correct token
- Assume success without checking the database
"""

import json
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
INGEST_TOKEN = "wrong"  # Wrong token for this test
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

# ==================== MAIN IMPLEMENTATION ====================
def main():
    """Execute the exact steps from Prompt 4.1"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 4.1")
    print("TASK: Test invalid authentication handling.")
    print("=" * 60)
    print()
    
    # Step 1: Load fixture D:\web project\AxiomOps\Tests\fixtures\finding_failed_high.json
    print("EXACT STEPS:")
    print("1. Load fixture D:\web project\AxiomOps\Tests\fixtures\finding_failed_high.json")
    
    try:
        payload = load_fixture("finding_failed_high.json")
        print("   ✅ Fixture loaded successfully")
    except Exception as e:
        error_result = {
            "test_id": "4.1",
            "test_name": "invalid_auth",
            "status": "FAIL",
            "http_status": 0,
            "evidence_blocked": False,
            "notes": f"Failed to load fixture: {e}"
        }
        print(f"\n❌ Failed to load fixture: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 2: Send it via POST to http://localhost:5678/webhook/complianceops-finding-ingestion with header X-COMPLIANCEOPS-TOKEN: wrong
    print("2. Send it via POST to http://localhost:5678/webhook/complianceops-finding-ingestion with header X-COMPLIANCEOPS-TOKEN: wrong")
    
    resp = post_webhook("complianceops-finding-ingestion", payload,
                        headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    print(f"   ✅ HTTP response status: {resp['status']}")
    
    # Step 3: Query Postgres: SELECT COUNT(*) FROM evidence_events WHERE run_id = 'RUN-TEST-001';
    print("3. Query Postgres: SELECT COUNT(*) FROM evidence_events WHERE run_id = 'RUN-TEST-001';")
    
    db = DB()
    try:
        evidence_result = db.query_one("SELECT COUNT(*) FROM evidence_events WHERE run_id = %s", ("RUN-TEST-001",))
        print(f"   ✅ Evidence query returned: {evidence_result}")
    except Exception as e:
        error_result = {
            "test_id": "4.1",
            "test_name": "invalid_auth",
            "status": "FAIL",
            "http_status": resp["status"],
            "evidence_blocked": False,
            "notes": f"Evidence query failed: {e}"
        }
        print(f"\n❌ Evidence query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    db.close()
    
    # EXPECTED RESULTS verification
    print("\n📊 Verifying expected results...")
    
    if evidence_result is None:
        error_result = {
            "test_id": "4.1",
            "test_name": "invalid_auth",
            "status": "FAIL",
            "http_status": resp["status"],
            "evidence_blocked": False,
            "notes": "Evidence query returned no results"
        }
        print("\n❌ Evidence query returned no results")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    evidence_count = evidence_result[0]
    
    # Determine status
    evidence_blocked = evidence_count == 0
    http_status_ok = resp["status"] != 200
    
    status = "PASS" if (evidence_blocked and http_status_ok) else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "4.1",
        "test_name": "invalid_auth",
        "status": status,
        "http_status": resp["status"],
        "evidence_blocked": evidence_blocked,
        "notes": ""
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - HTTP status: {resp['status']} (expected: not 200)")
    print(f"   - Evidence count: {evidence_count} (expected: 0)")
    print(f"   - Evidence blocked: {evidence_blocked}")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 4.1 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)