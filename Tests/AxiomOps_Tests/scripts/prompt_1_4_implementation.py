#!/usr/bin/env python3
"""
Prompt 1.4 — Test 04 Risk Prioritizer

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 1.4:
- Verify risk score, priority, and SLA calculation.
- Query Postgres database to verify risk calculation results
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Query Postgres: SELECT risk_score, priority, sla_due, repeated_failure FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';

EXPECTED RESULTS:
- risk_score > 0 and <= 100
- priority is one of: P1, P2, P3, P4
- sla_due is a timestamp in the future
- repeated_failure = false (first occurrence)

EXPECTED OUTPUT FORMAT:
{
  "test_id": "1.4",
  "workflow": "04_risk_prioritizer",
  "status": "PASS or FAIL",
  "risk_score": 0,
  "priority": "",
  "sla_due_future": true,
  "repeated_failure": false,
  "notes": ""
}

DO NOT:
- Accept null values for risk_score or priority
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
    """Execute the exact steps from Prompt 1.4"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 04")
    print("TASK: Verify risk score, priority, and SLA calculation.")
    print("=" * 60)
    print()
    
    # Step 1: Query Postgres: SELECT risk_score, priority, sla_due, repeated_failure FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("EXACT STEPS:")
    print("1. Query Postgres: SELECT risk_score, priority, sla_due, repeated_failure FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    db = DB()
    try:
        result = db.query_one(
            "SELECT risk_score, priority, sla_due, repeated_failure FROM findings WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Query returned: {result}")
    except Exception as e:
        error_result = {
            "test_id": "1.4",
            "workflow": "04_risk_prioritizer",
            "status": "FAIL",
            "risk_score": 0,
            "priority": "",
            "sla_due_future": True,
            "repeated_failure": False,
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
            "test_id": "1.4",
            "workflow": "04_risk_prioritizer",
            "status": "FAIL",
            "risk_score": 0,
            "priority": "",
            "sla_due_future": True,
            "repeated_failure": False,
            "notes": "No finding found for the specified key"
        }
        print("\n❌ No finding found for the specified key")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    risk_score = result[0]
    priority = result[1]
    sla_due = result[2]
    repeated_failure = result[3]
    
    # Calculate if SLA is in the future
    sla_due_future = False
    if sla_due:
        sla_due_future = sla_due > datetime.now()
    
    # Determine status
    status = "PASS" if (risk_score is not None and risk_score > 0 and risk_score <= 100 and
                       priority in ["P1", "P2", "P3", "P4"] and
                       sla_due_future and
                       repeated_failure == False) else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "1.4",
        "workflow": "04_risk_prioritizer",
        "status": status,
        "risk_score": risk_score,
        "priority": priority,
        "sla_due_future": sla_due_future,
        "repeated_failure": repeated_failure,
        "notes": ""
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Risk score: {risk_score} (expected: > 0 and <= 100)")
    print(f"   - Priority: {priority} (expected: P1, P2, P3, or P4)")
    print(f"   - SLA due future: {sla_due_future} (expected: True)")
    print(f"   - Repeated failure: {repeated_failure} (expected: False)")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 1.4 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)