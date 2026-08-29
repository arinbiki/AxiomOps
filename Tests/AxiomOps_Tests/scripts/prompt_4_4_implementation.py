#!/usr/bin/env python3
"""
Prompt 4.4 — Test 4.4 SLA Differentiation

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 4.4:
- Test SLA differentiation between critical and high severity findings
- Execute multiple unit tests in sequence
- Query Postgres database to verify SLA calculation differences
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Reset database (test_0_1_reset)
2. Test registry sync (test_1_1_registry)
3. Create critical prod finding via webhook
4. Wait 5 seconds
5. Create high prod finding via webhook
6. Wait 5 seconds
7. Query Postgres: SELECT priority, sla_due FROM findings WHERE finding_key = 'CC7.2::arn:aws:s3:::prod-data-lake::SOC2';
8. Query Postgres: SELECT priority, sla_due FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';

EXPECTED RESULTS:
- findings table has 2 rows: CC7.2 (priority P1, sla_due < 24h) and CC6.6 (priority P2, sla_due > 24h)
- Critical finding has shorter SLA than high finding

EXPECTED OUTPUT FORMAT:
{
  "test_id": "4.4",
  "test_name": "sla_differentiation",
  "status": "PASS or FAIL",
  "critical_priority": "",
  "high_priority": "",
  "critical_sla_hours": 0,
  "high_sla_hours": 0,
  "critical_sla_shorter": true,
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
    """Execute the exact steps from Prompt 4.4"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 4.4")
    print("TASK: Test SLA differentiation between critical and high severity findings.")
    print("=" * 60)
    print()
    
    # Step 1: Reset database (test_0_1_reset)
    print("EXACT STEPS:")
    print("1. Reset database (test_0_1_reset)")
    
    reset_result = test_0_1_reset()
    print(f"   ✅ Database reset: {reset_result.get('status', 'UNKNOWN')}")
    
    if reset_result.get("status") != "PASS":
        error_result = {
            "test_id": "4.4",
            "test_name": "sla_differentiation",
            "status": "FAIL",
            "critical_priority": "",
            "high_priority": "",
            "critical_sla_hours": 0,
            "high_sla_hours": 0,
            "critical_sla_shorter": False,
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
            "test_id": "4.4",
            "test_name": "sla_differentiation",
            "status": "FAIL",
            "critical_priority": "",
            "high_priority": "",
            "critical_sla_hours": 0,
            "high_sla_hours": 0,
            "critical_sla_shorter": False,
            "notes": "Registry sync failed"
        }
        print("\n❌ Registry sync failed")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 3: Create critical prod finding via webhook
    print("3. Create critical prod finding via webhook")
    
    critical_payload = load_fixture("finding_failed_critical_prod.json")
    critical_resp = post_webhook("complianceops-finding-ingestion", critical_payload,
                                 headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    print(f"   ✅ Critical finding creation response status: {critical_resp['status']}")
    
    # Step 4: Wait 5 seconds
    print("4. Wait 5 seconds.")
    time.sleep(5)
    
    # Step 5: Create high prod finding via webhook
    print("5. Create high prod finding via webhook")
    
    high_payload = load_fixture("finding_failed_high.json")
    high_resp = post_webhook("complianceops-finding-ingestion", high_payload,
                             headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    print(f"   ✅ High finding creation response status: {high_resp['status']}")
    
    # Step 6: Wait 5 seconds
    print("6. Wait 5 seconds.")
    time.sleep(5)
    
    # Step 7: Query Postgres: SELECT priority, sla_due FROM findings WHERE finding_key = 'CC7.2::arn:aws:s3:::prod-data-lake::SOC2';
    print("7. Query Postgres: SELECT priority, sla_due FROM findings WHERE finding_key = 'CC7.2::arn:aws:s3:::prod-data-lake::SOC2';")
    
    db = DB()
    try:
        critical_result = db.query_one(
            "SELECT priority, sla_due FROM findings WHERE finding_key = %s",
            ("CC7.2::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Critical finding query returned: {critical_result}")
    except Exception as e:
        error_result = {
            "test_id": "4.4",
            "test_name": "sla_differentiation",
            "status": "FAIL",
            "critical_priority": "",
            "high_priority": "",
            "critical_sla_hours": 0,
            "high_sla_hours": 0,
            "critical_sla_shorter": False,
            "notes": f"Critical finding query failed: {e}"
        }
        print(f"\n❌ Critical finding query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    # Step 8: Query Postgres: SELECT priority, sla_due FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("8. Query Postgres: SELECT priority, sla_due FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    try:
        high_result = db.query_one(
            "SELECT priority, sla_due FROM findings WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ High finding query returned: {high_result}")
    except Exception as e:
        error_result = {
            "test_id": "4.4",
            "test_name": "sla_differentiation",
            "status": "FAIL",
            "critical_priority": critical_result[0] if critical_result else "",
            "high_priority": "",
            "critical_sla_hours": 0,
            "high_sla_hours": 0,
            "critical_sla_shorter": False,
            "notes": f"High finding query failed: {e}"
        }
        print(f"\n❌ High finding query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    db.close()
    
    # EXPECTED RESULTS verification
    print("\n📊 Verifying expected results...")
    
    if critical_result is None:
        error_result = {
            "test_id": "4.4",
            "test_name": "sla_differentiation",
            "status": "FAIL",
            "critical_priority": "",
            "high_priority": "",
            "critical_sla_hours": 0,
            "high_sla_hours": 0,
            "critical_sla_shorter": False,
            "notes": "No critical finding found for the specified key"
        }
        print("\n❌ No critical finding found for the specified key")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    if high_result is None:
        error_result = {
            "test_id": "4.4",
            "test_name": "sla_differentiation",
            "status": "FAIL",
            "critical_priority": critical_result[0] if critical_result else "",
            "high_priority": "",
            "critical_sla_hours": 0,
            "high_sla_hours": 0,
            "critical_sla_shorter": False,
            "notes": "No high finding found for the specified key"
        }
        print("\n❌ No high finding found for the specified key")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Extract results
    critical_priority = critical_result[0]
    critical_sla_due = critical_result[1]
    
    high_priority = high_result[0]
    high_sla_due = high_result[1]
    
    # Calculate SLA hours
    critical_sla_hours = (critical_sla_due - datetime.now()).total_seconds() / 3600 if critical_sla_due else 0
    high_sla_hours = (high_sla_due - datetime.now()).total_seconds() / 3600 if high_sla_due else 0
    
    # Determine status
    critical_sla_shorter = critical_sla_hours < high_sla_hours
    
    status = "PASS" if (critical_priority == "P1" and high_priority == "P2" and 
                       critical_sla_shorter and critical_sla_hours > 0 and high_sla_hours > 0) else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "4.4",
        "test_name": "sla_differentiation",
        "status": status,
        "critical_priority": critical_priority,
        "high_priority": high_priority,
        "critical_sla_hours": round(critical_sla_hours, 1),
        "high_sla_hours": round(high_sla_hours, 1),
        "critical_sla_shorter": critical_sla_shorter,
        "notes": ""
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Critical priority: {critical_priority} (expected: P1)")
    print(f"   - High priority: {high_priority} (expected: P2)")
    print(f"   - Critical SLA hours: {round(critical_sla_hours, 1)} (expected: > 0)")
    print(f"   - High SLA hours: {round(high_sla_hours, 1)} (expected: > 0)")
    print(f"   - Critical SLA shorter: {critical_sla_shorter} (expected: true)")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 4.4 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)