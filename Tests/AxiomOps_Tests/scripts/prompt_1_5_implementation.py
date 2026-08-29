#!/usr/bin/env python3
"""
Prompt 1.5 — Test 05 Remediation Orchestrator

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 1.5:
- Verify ticket creation logic.
- Query Postgres database to verify remediation task creation
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Query Postgres: SELECT ticket_key, status FROM remediation_tasks WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
2. Query Postgres: SELECT jira_issue_key FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';

EXPECTED RESULTS:
- remediation_tasks has 1 row with status='open' and ticket_key is not null
- findings.jira_issue_key matches remediation_tasks.ticket_key
- If Jira is not configured, ticket_key may be null but task row should still exist

EXPECTED OUTPUT FORMAT:
{
  "test_id": "1.5",
  "workflow": "05_remediation_orchestrator",
  "status": "PASS or FAIL",
  "ticket_created": true,
  "ticket_key": "",
  "finding_ticket_linked": true,
  "notes": "If Jira not configured, note that here"
}

DO NOT:
- Create a real Jira ticket if this is a test environment
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
    """Execute the exact steps from Prompt 1.5"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 05")
    print("TASK: Verify ticket creation logic.")
    print("=" * 60)
    print()
    
    # Step 1: Query Postgres: SELECT ticket_key, status FROM remediation_tasks WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("EXACT STEPS:")
    print("1. Query Postgres: SELECT ticket_key, status FROM remediation_tasks WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    db = DB()
    try:
        task_result = db.query_one(
            "SELECT ticket_key, status FROM remediation_tasks WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Task query returned: {task_result}")
    except Exception as e:
        error_result = {
            "test_id": "1.5",
            "workflow": "05_remediation_orchestrator",
            "status": "FAIL",
            "ticket_created": False,
            "ticket_key": "",
            "finding_ticket_linked": False,
            "notes": f"Task query failed: {e}"
        }
        print(f"\n❌ Task query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    # Step 2: Query Postgres: SELECT jira_issue_key FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';
    print("2. Query Postgres: SELECT jira_issue_key FROM findings WHERE finding_key = 'CC6.6::arn:aws:s3:::prod-data-lake::SOC2';")
    
    try:
        finding_result = db.query_one(
            "SELECT jira_issue_key FROM findings WHERE finding_key = %s",
            ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",)
        )
        print(f"   ✅ Finding query returned: {finding_result}")
    except Exception as e:
        error_result = {
            "test_id": "1.5",
            "workflow": "05_remediation_orchestrator",
            "status": "FAIL",
            "ticket_created": task_result is not None,
            "ticket_key": task_result[0] if task_result else "",
            "finding_ticket_linked": False,
            "notes": f"Finding query failed: {e}"
        }
        print(f"\n❌ Finding query failed: {e}")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        db.close()
        return error_result
    
    db.close()
    
    # EXPECTED RESULTS verification
    print("\n📊 Verifying expected results...")
    
    if task_result is None:
        error_result = {
            "test_id": "1.5",
            "workflow": "05_remediation_orchestrator",
            "status": "FAIL",
            "ticket_created": False,
            "ticket_key": "",
            "finding_ticket_linked": False,
            "notes": "No remediation task found for the specified key"
        }
        print("\n❌ No remediation task found for the specified key")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    ticket_key = task_result[0]
    task_status = task_result[1]
    finding_jira_key = finding_result[0] if finding_result else None
    
    # Determine status
    ticket_created = task_result is not None
    finding_ticket_linked = finding_jira_key == ticket_key if finding_jira_key and ticket_key else False
    
    # Notes for Jira not configured
    notes = ""
    if ticket_key is None:
        notes = "If Jira not configured, ticket_key may be null but task row should still exist"
    
    status = "PASS" if (ticket_created and task_status == "open" and finding_ticket_linked) else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "1.5",
        "workflow": "05_remediation_orchestrator",
        "status": status,
        "ticket_created": ticket_created,
        "ticket_key": ticket_key or "",
        "finding_ticket_linked": finding_ticket_linked,
        "notes": notes
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Ticket created: {ticket_created}")
    print(f"   - Task status: {task_status} (expected: open)")
    print(f"   - Ticket key: {ticket_key}")
    print(f"   - Finding Jira key: {finding_jira_key}")
    print(f"   - Finding ticket linked: {finding_ticket_linked} (expected: true)")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 1.5 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)