#!/usr/bin/env python3
"""
Prompt 1.6 — Test 08 Closure Validator

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 1.6:
- Verify finding closure on passed evidence.
- Read fixture file and send via POST to ingestion webhook
- Wait for processing
- Query Postgres database to verify closure results
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Read D:\web project\AxiomOps\Tests\fixtures\finding_passed.json
2. Send it via POST to http://localhost:5678/webhook/complianceops-finding-ingestion with header X-COMPLIANCEOPS-TOKEN: change-me
3. Wait 5 seconds.
4. Query Postgres: SELECT status, closed_at, closure_reason FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
5. Query Postgres: SELECT status FROM remediation_tasks WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';

EXPECTED RESULTS:
- findings.status = 'closed'
- findings.closed_at is not null
- findings.closure_reason = 'consecutive_evidence_passed'
- remediation_tasks.status = 'closed'

EXPECTED OUTPUT FORMAT:
{
  "test_id": "1.6",
  "workflow": "08_closure_validator",
  "status": "PASS or FAIL",
  "finding_closed": true,
  "closure_reason": "",
  "task_closed": true,
  "notes": ""
}

DO NOT:
- Skip the wait time
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
    """Execute the exact steps from Prompt 1.6"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 08")
    print("TASK: Verify finding closure on passed evidence.")
    print("=" * 60)
    print()
    
    # Step 1: Read D:\web project\AxiomOps\Tests\fixtures\finding_passed.json
    print("EXACT STEPS:")
    print("1. Read D:\web project\AxiomOps\Tests\fixtures\finding_passed.json")
    
    try:
        payload = load_fixture("finding_passed.json")
        print("   ✅ Fixture loaded successfully")
    except Exception as e:
        error_result = {
            "test_id": "1.6",
            "workflow": "08_closure_validator",
            "status": "FAIL",
            "finding_closed": False,
            "closure_reason": "",
            "task_closed": False,
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
    
    # Step 3: Wait 5 seconds.
    print("3. Wait 5 seconds.")
    time.sleep(5)
    
    # Step 4: Query Postgres: SELECT status, closed_at, closure_reason FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("4. Query Postgres: SELECT status, closed_at, closure_reason FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    db = DB()
    try:
        finding_result = db.query_one(
            "SELECT status, closed_at, closure_reason FROM findings WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Finding query returned: {finding_result}")
    except Exception as e:
        error_result = {
            "test_id": "1.6",
            "workflow": "08_closure_validator",
            "status": "FAIL",
            "finding_closed": False,
            "closure_reason": "",
            "task_closed": False,
            "notes": f"Finding query failed: {e}"
        }
        print(f"\n❌ Finding query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    # Step 5: Query Postgres: SELECT status FROM remediation_tasks WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("5. Query Postgres: SELECT status FROM remediation_tasks WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    try:
        task_result = db.query_one(
            "SELECT status FROM remediation_tasks WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Task query returned: {task_result}")
    except Exception as e:
        error_result = {
            "test_id": "1.6",
            "workflow": "08_closure_validator",
            "status": "FAIL",
            "finding_closed": finding_result[0] == "closed" if finding_result else False,
            "closure_reason": finding_result[2] if finding_result else "",
            "task_closed": False,
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
    
    if finding_result is None:
        error_result = {
            "test_id": "1.6",
            "workflow": "08_closure_validator",
            "status": "FAIL",
            "finding_closed": False,
            "closure_reason": "",
            "task_closed": False,
            "notes": "No finding found for the specified key"
        }
        print("\n❌ No finding found for the specified key")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    if task_result is None:
        error_result = {
            "test_id": "1.6",
            "workflow": "08_closure_validator",
            "status": "FAIL",
            "finding_closed": finding_result[0] == "closed" if finding_result else False,
            "closure_reason": finding_result[2] if finding_result else "",
            "task_closed": False,
            "notes": "No remediation task found for the specified key"
        }
        print("\n❌ No remediation task found for the specified key")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    finding_status = finding_result[0]
    finding_closed_at = finding_result[1]
    finding_closure_reason = finding_result[2]
    task_status = task_result[0]
    
    # Determine status
    finding_closed = finding_status == "closed" and finding_closed_at is not None
    task_closed = task_status == "closed"
    
    status = "PASS" if (finding_closed and task_closed and 
                       finding_closure_reason == "consecutive_evidence_passed") else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "1.6",
        "workflow": "08_closure_validator",
        "status": status,
        "finding_closed": finding_closed,
        "closure_reason": finding_closure_reason,
        "task_closed": task_closed,
        "notes": ""
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Finding status: {finding_status} (expected: closed)")
    print(f"   - Finding closed at: {finding_closed_at}")
    print(f"   - Finding closure reason: {finding_closure_reason} (expected: consecutive_evidence_passed)")
    print(f"   - Task status: {task_status} (expected: closed)")
    print(f"   - Finding closed: {finding_closed}")
    print(f"   - Task closed: {task_closed}")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 1.6 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)