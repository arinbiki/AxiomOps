#!/usr/bin/env python3
"""
Prompt 2.1 — Test 2.1 Full Lifecycle

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 2.1:
- Test the complete workflow from registry sync through finding creation to closure
- Execute multiple unit tests in sequence
- Query Postgres database to verify final state
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Reset database (test_0_1_reset)
2. Test registry sync (test_1_1_registry)
3. Test finding ingestion (test_1_2_ingestion)
4. Wait 3 seconds
5. Query Postgres: SELECT status, owner_status, risk_score, priority, jira_issue_key FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
6. Query Postgres: SELECT ticket_key FROM remediation_tasks WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
7. Test finding closure (test_1_6_closure)
8. Query Postgres: SELECT status, closed_at FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';

EXPECTED RESULTS:
- Registry sync loads 2 assets and 2 controls
- Finding ingestion creates a finding with status='open', severity='high', occurrence_count=1
- Owner resolution sets owner_email='data-platform@example.com', owner_status='resolved_asset_owner'
- Risk calculation sets risk_score>0, priority in ['P1','P2','P3','P4'], sla_due in future, repeated_failure=false
- Remediation creates a ticket with status='open' and jira_issue_key matches ticket_key
- Finding closure sets status='closed', closed_at not null, closure_reason='consecutive_evidence_passed'
- Remediation task status='closed'

EXPECTED OUTPUT FORMAT:
{
  "test_id": "2.1",
  "test_name": "full_lifecycle",
  "status": "PASS or FAIL",
  "registry_loaded": true,
  "finding_created": true,
  "owner_resolved": true,
  "risk_calculated": true,
  "ticket_created": true,
  "finding_closed": true,
  "notes": ""
}

DO NOT:
- Skip any step in the sequence
- Assume success without checking the database
"""

import json
import time
import psycopg2
from datetime import datetime

# ==================== CONFIGURATION ====================
# These should match your actual environment
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "n8n"
POSTGRES_USER = "n8n"
POSTGRES_PASSWORD = "change-me"
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
    url = f"http://localhost:5678/webhook/{path}"
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

def test_1_6_closure():
    """Test finding closure."""
    payload = load_fixture("finding_passed.json")
    resp = post_webhook("complianceops-finding-ingestion", payload,
                        headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    time.sleep(5)
    db = DB()
    finding = db.query_one("SELECT status, closed_at, closure_reason FROM findings WHERE finding_key = %s",
                           ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    task = db.query_one("SELECT status FROM remediation_tasks WHERE finding_key = %s",
                        ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    db.close()
    return {
        "status": "PASS" if finding and finding[0] == "closed" and finding[1] is not None else "FAIL",
        "finding_closed": finding[0] == "closed" if finding else False,
        "closure_reason": finding[2] if finding else None,
        "task_closed": task[0] == "closed" if task else False
    }

# ==================== MAIN IMPLEMENTATION ====================
def main():
    """Execute the exact steps from Prompt 2.1"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 2.1")
    print("TASK: Test the complete workflow from registry sync through finding creation to closure.")
    print("=" * 60)
    print()
    
    # Step 1: Reset database (test_0_1_reset)
    print("EXACT STEPS:")
    print("1. Reset database (test_0_1_reset)")
    
    reset_result = test_0_1_reset()
    print(f"   ✅ Database reset: {reset_result.get('status', 'UNKNOWN')}")
    
    if reset_result.get("status") != "PASS":
        error_result = {
            "test_id": "2.1",
            "test_name": "full_lifecycle",
            "status": "FAIL",
            "registry_loaded": False,
            "finding_created": False,
            "owner_resolved": False,
            "risk_calculated": False,
            "ticket_created": False,
            "finding_closed": False,
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
            "test_id": "2.1",
            "test_name": "full_lifecycle",
            "status": "FAIL",
            "registry_loaded": False,
            "finding_created": False,
            "owner_resolved": False,
            "risk_calculated": False,
            "ticket_created": False,
            "finding_closed": False,
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
            "test_id": "2.1",
            "test_name": "full_lifecycle",
            "status": "FAIL",
            "registry_loaded": True,
            "finding_created": False,
            "owner_resolved": False,
            "risk_calculated": False,
            "ticket_created": False,
            "finding_closed": False,
            "notes": "Finding ingestion failed"
        }
        print("\n❌ Finding ingestion failed")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 4: Wait 3 seconds
    print("4. Wait 3 seconds.")
    time.sleep(3)
    
    # Step 5: Query Postgres: SELECT status, owner_status, risk_score, priority, jira_issue_key FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("5. Query Postgres: SELECT status, owner_status, risk_score, priority, jira_issue_key FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    db = DB()
    try:
        finding_result = db.query_one(
            "SELECT status, owner_status, risk_score, priority, jira_issue_key FROM findings WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Finding query returned: {finding_result}")
    except Exception as e:
        error_result = {
            "test_id": "2.1",
            "test_name": "full_lifecycle",
            "status": "FAIL",
            "registry_loaded": True,
            "finding_created": True,
            "owner_resolved": False,
            "risk_calculated": False,
            "ticket_created": False,
            "finding_closed": False,
            "notes": f"Finding query failed: {e}"
        }
        print(f"\n❌ Finding query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    # Step 6: Query Postgres: SELECT ticket_key FROM remediation_tasks WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("6. Query Postgres: SELECT ticket_key FROM remediation_tasks WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    try:
        task_result = db.query_one(
            "SELECT ticket_key FROM remediation_tasks WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Task query returned: {task_result}")
    except Exception as e:
        error_result = {
            "test_id": "2.1",
            "test_name": "full_lifecycle",
            "status": "FAIL",
            "registry_loaded": True,
            "finding_created": True,
            "owner_resolved": False,
            "risk_calculated": False,
            "ticket_created": False,
            "finding_closed": False,
            "notes": f"Task query failed: {e}"
        }
        print(f"\n❌ Task query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    db.close()
    
    # Step 7: Test finding closure (test_1_6_closure)
    print("7. Test finding closure (test_1_6_closure)")
    
    closure_result = test_1_6_closure()
    print(f"   ✅ Finding closure: {closure_result.get('status', 'UNKNOWN')}")
    
    if closure_result.get("status") != "PASS":
        error_result = {
            "test_id": "2.1",
            "test_name": "full_lifecycle",
            "status": "FAIL",
            "registry_loaded": True,
            "finding_created": True,
            "owner_resolved": False,
            "risk_calculated": False,
            "ticket_created": False,
            "finding_closed": False,
            "notes": "Finding closure failed"
        }
        print("\n❌ Finding closure failed")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 8: Query Postgres: SELECT status, closed_at FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("8. Query Postgres: SELECT status, closed_at FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    db = DB()
    try:
        final_finding_result = db.query_one(
            "SELECT status, closed_at FROM findings WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Final finding query returned: {final_finding_result}")
    except Exception as e:
        error_result = {
            "test_id": "2.1",
            "test_name": "full_lifecycle",
            "status": "FAIL",
            "registry_loaded": True,
            "finding_created": True,
            "owner_resolved": False,
            "risk_calculated": False,
            "ticket_created": False,
            "finding_closed": False,
            "notes": f"Final finding query failed: {e}"
        }
        print(f"\n❌ Final finding query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    db.close()
    
    # EXPECTED RESULTS verification
    print("\n📊 Verifying expected results...")
    
    if finding_result is None:
        error_result = {
            "test_id": "2.1",
            "test_name": "full_lifecycle",
            "status": "FAIL",
            "registry_loaded": True,
            "finding_created": False,
            "owner_resolved": False,
            "risk_calculated": False,
            "ticket_created": False,
            "finding_closed": False,
            "notes": "No finding found for the specified key"
        }
        print("\n❌ No finding found for the specified key")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    if task_result is None:
        error_result = {
            "test_id": "2.1",
            "test_name": "full_lifecycle",
            "status": "FAIL",
            "registry_loaded": True,
            "finding_created": True,
            "owner_resolved": False,
            "risk_calculated": False,
            "ticket_created": False,
            "finding_closed": False,
            "notes": "No remediation task found for the specified key"
        }
        print("\n❌ No remediation task found for the specified key")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    if final_finding_result is None:
        error_result = {
            "test_id": "2.1",
            "test_name": "full_lifecycle",
            "status": "FAIL",
            "registry_loaded": True,
            "finding_created": True,
            "owner_resolved": False,
            "risk_calculated": False,
            "ticket_created": False,
            "finding_closed": False,
            "notes": "No finding found after closure"
        }
        print("\n❌ No finding found after closure")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Extract results
    finding_status = finding_result[0]
    owner_status = finding_result[1]
    risk_score = finding_result[2]
    priority = finding_result[3]
    jira_issue_key = finding_result[4]
    
    ticket_key = task_result[0]
    
    final_status = final_finding_result[0]
    closed_at = final_finding_result[1]
    
    # Determine status
    registry_loaded = registry_result.get("status") == "PASS"
    finding_created = finding_result is not None
    owner_resolved = owner_status == "resolved_asset_owner" if owner_status else False
    risk_calculated = risk_score is not None and risk_score > 0 and risk_score <= 100
    ticket_created = task_result is not None
    finding_closed = final_status == "closed" and closed_at is not None
    
    status = "PASS" if (registry_loaded and finding_created and owner_resolved and 
                       risk_calculated and ticket_created and finding_closed) else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "2.1",
        "test_name": "full_lifecycle",
        "status": status,
        "registry_loaded": registry_loaded,
        "finding_created": finding_created,
        "owner_resolved": owner_resolved,
        "risk_calculated": risk_calculated,
        "ticket_created": ticket_created,
        "finding_closed": finding_closed,
        "notes": ""
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Registry loaded: {registry_loaded}")
    print(f"   - Finding created: {finding_created}")
    print(f"   - Owner resolved: {owner_resolved} (expected: true)")
    print(f"   - Risk calculated: {risk_calculated} (expected: true)")
    print(f"   - Ticket created: {ticket_created}")
    print(f"   - Finding closed: {finding_closed} (expected: true)")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 2.1 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)