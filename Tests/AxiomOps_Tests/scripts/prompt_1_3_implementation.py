#!/usr/bin/env python3
"""
Prompt 1.3 — Test 03 Owner Resolver

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 1.3:
- Verify owner resolution logic.
- Query Postgres database to verify owner resolution results
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Query Postgres: SELECT owner_email, owner_status, missing_owner FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';

EXPECTED RESULTS:
- owner_email = 'data-platform@example.com' (from asset registry)
- owner_status = 'resolved_asset_owner'
- missing_owner = false

EXPECTED OUTPUT FORMAT:
{
  "test_id": "1.3",
  "workflow": "03_owner_resolver",
  "status": "PASS or FAIL",
  "owner_email": "",
  "owner_status": "",
  "missing_owner": false,
  "notes": ""
}

DO NOT:
- Trigger the workflow manually
- Trust the HTTP response from test 1.2
"""

import json
import psycopg2
from datetime import datetime

# ==================== CONFIGURATION ====================
# These should match your actual environment
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "n8n"
POSTGRES_USER = "n8n"
POSTGRES_PASSWORD = "change-me"

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

# ==================== MAIN IMPLEMENTATION ====================
def main():
    """Execute the exact steps from Prompt 1.3"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 03")
    print("TASK: Verify owner resolution logic.")
    print("=" * 60)
    print()
    
    # Step 1: Query Postgres: SELECT owner_email, owner_status, missing_owner FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("EXACT STEPS:")
    print("1. Query Postgres: SELECT owner_email, owner_status, missing_owner FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    db = DB()
    try:
        result = db.query_one(
            "SELECT owner_email, owner_status, missing_owner FROM findings WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Query returned: {result}")
    except Exception as e:
        error_result = {
            "test_id": "1.3",
            "workflow": "03_owner_resolver",
            "status": "FAIL",
            "owner_email": "",
            "owner_status": "",
            "missing_owner": False,
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
            "test_id": "1.3",
            "workflow": "03_owner_resolver",
            "status": "FAIL",
            "owner_email": "",
            "owner_status": "",
            "missing_owner": False,
            "notes": "No finding found for the specified key"
        }
        print("\n❌ No finding found for the specified key")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    owner_email = result[0]
    owner_status = result[1]
    missing_owner = result[2]
    
    # Determine status
    status = "PASS" if (owner_email == "data-platform@example.com" and 
                       owner_status == "resolved_asset_owner" and 
                       missing_owner == False) else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "1.3",
        "workflow": "03_owner_resolver",
        "status": status,
        "owner_email": owner_email,
        "owner_status": owner_status,
        "missing_owner": missing_owner,
        "notes": ""
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Owner email: {owner_email} (expected: data-platform@example.com)")
    print(f"   - Owner status: {owner_status} (expected: resolved_asset_owner)")
    print(f"   - Missing owner: {missing_owner} (expected: False)")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 1.3 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)