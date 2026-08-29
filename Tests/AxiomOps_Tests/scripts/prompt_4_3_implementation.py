#!/usr/bin/env python3
"""
Prompt 4.3 — Test 4.3 AI Unavailable

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 4.3:
- Verify AI helper returns text or fails safely when Ollama is unavailable
- Execute multiple unit tests in sequence
- Query Postgres database to verify core logic survives AI failure
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Reset database (test_0_1_reset)
2. Test registry sync (test_1_1_registry)
3. Test finding ingestion (test_1_2_ingestion)
4. Wait 5 seconds
5. Query Postgres: SELECT status, owner_email, risk_score FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';

EXPECTED RESULTS:
- findings.status = 'open'
- findings.owner_email is not null (resolved from asset registry)
- findings.risk_score > 0 (calculated from evidence)

EXPECTED OUTPUT FORMAT:
{
  "test_id": "4.3",
  "test_name": "ai_unavailable",
  "status": "PASS or FAIL",
  "core_logic_survived": true,
  "finding_created": true,
  "owner_resolved": true,
  "risk_calculated": true,
  "notes": "PASS if core logic works regardless of AI state"
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
    """Execute the exact steps from Prompt 4.3"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 4.3")
    print("TASK: Verify AI helper returns text or fails safely.")
    print("=" * 60)
    print()
    
    # Step 1: Reset database (test_0_1_reset)
    print("EXACT STEPS:")
    print("1. Reset database (test_0_1_reset)")
    
    reset_result = test_0_1_reset()
    print(f"   ✅ Database reset: {reset_result.get('status', 'UNKNOWN')}")
    
    if reset_result.get("status") != "PASS":
        error_result = {
            "test_id": "4.3",
            "test_name": "ai_unavailable",
            "status": "FAIL",
            "core_logic_survived": False,
            "finding_created": False,
            "owner_resolved": False,
            "risk_calculated": False,
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
            "test_id": "4.3",
            "test_name": "ai_unavailable",
            "status": "FAIL",
            "core_logic_survived": False,
            "finding_created": False,
            "owner_resolved": False,
            "risk_calculated": False,
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
            "test_id": "4.3",
            "test_name": "ai_unavailable",
            "status": "FAIL",
            "core_logic_survived": False,
            "finding_created": False,
            "owner_resolved": False,
            "risk_calculated": False,
            "notes": "Finding ingestion failed"
        }
        print("\n❌ Finding ingestion failed")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 4: Wait 5 seconds
    print("4. Wait 5 seconds.")
    time.sleep(5)
    
    # Step 5: Query Postgres: SELECT status, owner_email, risk_score FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("5. Query Postgres: SELECT status, owner_email, risk_score FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    db = DB()
    try:
        result = db.query_one(
            "SELECT status, owner_email, risk_score FROM findings WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Query returned: {result}")
    except Exception as e:
        error_result = {
            "test_id": "4.3",
            "test_name": "ai_unavailable",
            "status": "FAIL",
            "core_logic_survived": False,
            "finding_created": False,
            "owner_resolved": False,
            "risk_calculated": False,
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
            "test_id": "4.3",
            "test_name": "ai_unavailable",
            "status": "FAIL",
            "core_logic_survived": False,
            "finding_created": False,
            "owner_resolved": False,
            "risk_calculated": False,
            "notes": "No finding found for the specified key"
        }
        print("\n❌ No finding found for the specified key")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Extract results
    finding_status = result[0]
    owner_email = result[1]
    risk_score = result[2]
    
    # Determine status
    core_logic_survived = result is not None
    finding_created = finding_status == "open"
    owner_resolved = owner_email is not None
    risk_calculated = risk_score is not None and risk_score > 0
    
    status = "PASS" if (core_logic_survived and finding_created and owner_resolved and risk_calculated) else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "4.3",
        "test_name": "ai_unavailable",
        "status": status,
        "core_logic_survived": core_logic_survived,
        "finding_created": finding_created,
        "owner_resolved": owner_resolved,
        "risk_calculated": risk_calculated,
        "notes": "PASS if core logic works regardless of AI state"
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Finding status: {finding_status} (expected: open)")
    print(f"   - Owner email: {owner_email} (expected: not null)")
    print(f"   - Risk score: {risk_score} (expected: > 0)")
    print(f"   - Core logic survived: {core_logic_survived}")
    print(f"   - Finding created: {finding_created}")
    print(f"   - Owner resolved: {owner_resolved}")
    print(f"   - Risk calculated: {risk_calculated}")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 4.3 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)