#!/usr/bin/env python3
"""
Prompt 1.1 — Test 01 Registry Sync (Valid Payload)

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 1.1:
- Test that Registry Sync correctly upserts assets and controls
- Read fixture file and send via POST to webhook
- Wait for processing
- Query Postgres database to verify results
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Read the file at D:\web project\AxiomOps\Tests\fixtures\registry_valid.json
2. Send it via POST to http://localhost:5678/webhook/complianceops-registry-sync
3. Wait 3 seconds.
4. Query Postgres: SELECT asset_id, owner_email FROM assets WHERE active = true;
5. Query Postgres: SELECT control_id, framework FROM controls WHERE active = true;

EXPECTED RESULTS:
- assets table has 2 rows: asset-001 (owner: data-platform@example.com) and asset-002
- controls table has 2 rows: CC6.6/SOC2 and CC7.2/SOC2
- HTTP response status was 200

EXPECTED OUTPUT FORMAT:
{
  "test_id": "1.1",
  "workflow": "01_registry_sync",
  "status": "PASS or FAIL",
  "assets_count": 2,
  "controls_count": 2,
  "asset_owner_match": true,
  "http_status": 200,
  "notes": ""
}

DO NOT:
- Modify the fixture file
- Skip the SQL verification
- Assume success without checking the database
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
    """Execute the exact steps from Prompt 1.1"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 01")
    print("TASK: Test that Registry Sync correctly upserts assets and controls.")
    print("=" * 60)
    print()
    
    # Step 1: Read the file at D:\web project\AxiomOps\Tests\fixtures\registry_valid.json
    print("EXACT STEPS:")
    print("1. Read the file at D:\web project\AxiomOps\Tests\fixtures\registry_valid.json")
    
    try:
        payload = load_fixture("registry_valid.json")
        print("   ✅ Fixture loaded successfully")
    except Exception as e:
        error_result = {
            "test_id": "1.1",
            "workflow": "01_registry_sync",
            "status": "FAIL",
            "assets_count": 0,
            "controls_count": 0,
            "asset_owner_match": False,
            "http_status": 0,
            "notes": f"Failed to load fixture: {e}"
        }
        print(f"\n❌ Failed to load fixture: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 2: Send it via POST to http://localhost:5678/webhook/complianceops-registry-sync
    print("2. Send it via POST to http://localhost:5678/webhook/complianceops-registry-sync")
    
    resp = post_webhook("complianceops-registry-sync", payload)
    print(f"   ✅ HTTP response status: {resp['status']}")
    
    # Step 3: Wait 3 seconds
    print("3. Wait 3 seconds.")
    time.sleep(3)
    
    # Step 4: Query Postgres: SELECT asset_id, owner_email FROM assets WHERE active = true;
    print("4. Query Postgres: SELECT asset_id, owner_email FROM assets WHERE active = true;")
    
    db = DB()
    try:
        assets = db.query_all("SELECT asset_id, owner_email FROM assets WHERE active = true")
        print(f"   ✅ Assets query returned {len(assets)} rows")
    except Exception as e:
        error_result = {
            "test_id": "1.1",
            "workflow": "01_registry_sync",
            "status": "FAIL",
            "assets_count": 0,
            "controls_count": 0,
            "asset_owner_match": False,
            "http_status": resp["status"],
            "notes": f"Assets query failed: {e}"
        }
        print(f"\n❌ Assets query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    # Step 5: Query Postgres: SELECT control_id, framework FROM controls WHERE active = true;
    print("5. Query Postgres: SELECT control_id, framework FROM controls WHERE active = true;")
    
    try:
        controls = db.query_all("SELECT control_id, framework FROM controls WHERE active = true")
        print(f"   ✅ Controls query returned {len(controls)} rows")
    except Exception as e:
        error_result = {
            "test_id": "1.1",
            "workflow": "01_registry_sync",
            "status": "FAIL",
            "assets_count": len(assets),
            "controls_count": 0,
            "asset_owner_match": False,
            "http_status": resp["status"],
            "notes": f"Controls query failed: {e}"
        }
        print(f"\n❌ Controls query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    db.close()
    
    # EXPECTED RESULTS verification
    print("\n📊 Verifying expected results...")
    
    # Check assets count and specific asset
    assets_count = len(assets)
    expected_assets = 2
    asset_001_found = any(a[0] == "asset-001" and a[1] == "data-platform@example.com" for a in assets)
    asset_002_found = any(a[0] == "asset-002" for a in assets)
    
    # Check controls count and specific controls
    controls_count = len(controls)
    expected_controls = 2
    cc66_soc2_found = any(c[0] == "CC6.6/SOC2" for c in controls)
    cc72_soc2_found = any(c[0] == "CC7.2/SOC2" for c in controls)
    
    # Determine asset_owner_match
    asset_owner_match = asset_001_found and asset_002_found
    
    # Determine overall status
    status = "PASS" if (assets_count == expected_assets and controls_count == expected_controls and 
                       asset_owner_match and cc66_soc2_found and cc72_soc2_found and resp["status"] == 200) else "FAIL"
    
    # Prepare result in exact format specified
    result = {
        "test_id": "1.1",
        "workflow": "01_registry_sync",
        "status": status,
        "assets_count": assets_count,
        "controls_count": controls_count,
        "asset_owner_match": asset_owner_match,
        "http_status": resp["status"],
        "notes": ""
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Assets count: {assets_count} (expected: {expected_assets})")
    print(f"   - Controls count: {controls_count} (expected: {expected_controls})")
    print(f"   - Asset owner match: {asset_owner_match}")
    print(f"   - HTTP status: {resp['status']} (expected: 200)")
    print(f"   - Overall status: {status}")
    
    if assets:
        print(f"   - Found assets: {', '.join([f'{a[0]} ({a[1]})' for a in assets])}")
    if controls:
        print(f"   - Found controls: {', '.join([c[0] for c in controls])}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result, indent=2))
    
    return result

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 1.1 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)