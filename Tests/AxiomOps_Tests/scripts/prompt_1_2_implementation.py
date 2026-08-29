#!/usr/bin/env python3
"""
Prompt 1.2 — Test 02 Finding Ingestion (Failed Control)

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 1.2:
- Test that a failed control creates a finding
- Read fixture file and send via POST to ingestion webhook
- Wait for sub-workflows to complete
- Query Postgres database to verify results
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Read D:\web project\AxiomOps\Tests\fixtures\finding_failed_high.json
2. Send it via POST to http://localhost:5678/webhook/complianceops-finding-ingestion with header X-COMPLIANCEOPS-TOKEN: change-me
3. Wait 5 seconds for sub-workflows to complete.
4. Query Postgres: SELECT * FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
5. Query Postgres: SELECT * FROM evidence_events WHERE run_id = 'RUN-TEST-001';

EXPECTED RESULTS:
- findings table has 1 row with status='open', severity='high', occurrence_count=1
- evidence_events table has 1 row with passed=false
- HTTP response was {"status":"accepted",...}

EXPECTED OUTPUT FORMAT:
{
  "test_id": "1.2",
  "workflow": "02_finding_ingestion",
  "status": "PASS or FAIL",
  "finding_exists": true,
  "finding_status": "open",
  "finding_severity": "high",
  "occurrence_count": 1,
  "evidence_count": 1,
  "notes": ""
}

DO NOT:
- Run this test before registry sync
- Skip the 5 second wait
- Check only the HTTP response
"""

import json
import requests
import psycopg2
import time
from pathlib import Path
from datetime import datetime

# ==================== CONFIGURATION ====================
# These should match your actual environment
N8N_URL = "http://localhost:5678"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "n8n"
POSTGRES_USER = "n8n"
POSTGRES_PASSWORD = "change-me"
INGEST_TOKEN = "change-me"
FIXTURES_DIR = Path("D:\web project\AxiomOps\Tests\fixtures")

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
    with open(FIXTURES_DIR / name, "r") as f:
        return json.load(f)

# ==================== MAIN IMPLEMENTATION ====================
def main():
    """Execute the exact steps from Prompt 1.2"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 02")
    print("TASK: Test that a failed control creates a finding.")
    print("=" * 60)
    print()
    
    # Step 1: Read D:\web project\AxiomOps\Tests\fixtures\finding_failed_high.json
    print("EXACT STEPS:")
    print("1. Read D:\web project\AxiomOps\Tests\fixtures\finding_failed_high.json")
    
    try:
        payload = load_fixture("finding_failed_high.json")
        print("   ✅ Fixture loaded successfully")
    except Exception as e:
        error_result = {
            "test_id": "1.2",
            "workflow": "02_finding_ingestion",
            "status": "FAIL",
            "finding_exists": False,
            "finding_status": None,
            "finding_severity": None,
            "occurrence_count": 0,
            "evidence_count": 0,
            "notes": f"Failed to load fixture: {e}"
        }
        print(f"\n❌ Failed to load fixture: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 2: Send it via POST to http://localhost:5678/webhook/complianceops-finding-ingestion with header X-COMPLIANCEOPS-TOKEN: change-me
    print("2. Send it via POST to http://localhost:5678/webhook/complianceops-finding-ingestion with header X-COMPLIANCEOPS-TOKEN: change-me")
    
    resp = post_webhook("complianceops-finding-ingestion", payload,
                        headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    print(f"   ✅ HTTP response status: {resp['status']}")
    
    # Step 3: Wait 5 seconds for sub-workflows to complete
    print("3. Wait 5 seconds for sub-workflows to complete.")
    time.sleep(5)
    
    # Step 4: Query Postgres: SELECT * FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("4. Query Postgres: SELECT * FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    db = DB()
    try:
        finding = db.query_one("SELECT status, severity, occurrence_count FROM findings WHERE finding_key = %s",
                               ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
        print(f"   ✅ Finding query returned: {finding}")
    except Exception as e:
        error_result = {
            "test_id": "1.2",
            "workflow": "02_finding_ingestion",
            "status": "FAIL",
            "finding_exists": False,
            "finding_status": None,
            "finding_severity": None,
            "occurrence_count": 0,
            "evidence_count": 0,
            "notes": f"Finding query failed: {e}"
        }
        print(f"\n❌ Finding query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    # Step 5: Query Postgres: SELECT * FROM evidence_events WHERE run_id = 'RUN-TEST-001';
    print("5. Query Postgres: SELECT * FROM evidence_events WHERE run_id = 'RUN-TEST-001';")
    
    try:
        evidence = db.query_all("SELECT * FROM evidence_events WHERE run_id = %s", ("RUN-TEST-001",))
        print(f"   ✅ Evidence query returned {len(evidence)} rows")
    except Exception as e:
        error_result = {
            "test_id": "1.2",
            "workflow": "02_finding_ingestion",
            "status": "FAIL",
            "finding_exists": finding is not None,
            "finding_status": finding[0] if finding else None,
            "finding_severity": finding[1] if finding else None,
            "occurrence_count": finding[2] if finding else 0,
            "evidence_count": 0,
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
    
    # Check finding exists and has correct properties
    finding_exists = finding is not None
    finding_status = finding[0] if finding else None
    finding_severity = finding[1] if finding else None
    occurrence_count = finding[2] if finding else 0
    
    evidence_count = len(evidence)
    
    # Determine overall status
    status = "PASS" if (finding_exists and finding_status == "open" and 
                       finding_severity == "high" and occurrence_count == 1 and 
                       evidence_count == 1 and resp["status"] == 200) else "FAIL"
    
    # Prepare result in exact format specified
    result = {
        "test_id": "1.2",
        "workflow": "02_finding_ingestion",
        "status": status,
        "finding_exists": finding_exists,
        "finding_status": finding_status,
        "finding_severity": finding_severity,
        "occurrence_count": occurrence_count,
        "evidence_count": evidence_count,
        "notes": ""
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Finding exists: {finding_exists}")
    print(f"   - Finding status: {finding_status} (expected: open)")
    print(f"   - Finding severity: {finding_severity} (expected: high)")
    print(f"   - Occurrence count: {occurrence_count} (expected: 1)")
    print(f"   - Evidence count: {evidence_count} (expected: 1)")
    print(f"   - HTTP status: {resp['status']} (expected: 200)")
    print(f"   - Overall status: {status}")
    
    if finding:
        print(f"   - Finding details: status={finding[0]}, severity={finding[1]}, occurrence_count={finding[2]}")
    if evidence:
        print(f"   - Evidence rows: {len(evidence)}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result, indent=2))
    
    return result

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 1.2 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)