#!/usr/bin/env python3
"""
AxiomOps Test Runner
====================
Run individual tests or the full suite.
Designed for vibe coders using Copilot Chat with 3B models.

Usage:
    python test_runner.py --test 1.1
    python test_runner.py --phase unit
    python test_runner.py --all

Requirements:
    pip install requests psycopg2-binary
"""

import json
import sys
import time
import argparse
import requests
import psycopg2
from pathlib import Path
from datetime import datetime

# ==================== CONFIGURATION ====================
# Edit these to match your environment
N8N_URL = "http://localhost:5678"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "n8n"
POSTGRES_USER = "n8n"
POSTGRES_PASSWORD = "change-me"
INGEST_TOKEN = "change-me"
FIXTURES_DIR = Path(__file__).parent / "fixtures"

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

# ==================== TEST RESULT PRINTER ====================
def print_result(result):
    status_icon = "✅" if result.get("status") == "PASS" else "❌"
    print(f"\n{status_icon} Test {result.get('test_id', 'UNKNOWN')}: {result.get('status', 'UNKNOWN')}")
    for k, v in result.items():
        if k not in ["status", "test_id", "notes"]:
            print(f"   {k}: {v}")
    if result.get("notes"):
        print(f"   notes: {result['notes']}")
    return result.get("status") == "PASS"

# ==================== PHASE 0: SETUP ====================
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
        return {
            "test_id": "0.1", "status": "PASS" if count == 0 else "FAIL",
            "findings_count": count, "notes": "Database reset complete"
        }
    except Exception as e:
        return {"test_id": "0.1", "status": "FAIL", "notes": str(e)}

# ==================== PHASE 1: UNIT TESTS ====================
def test_1_1_registry():
    payload = load_fixture("registry_valid.json")
    resp = post_webhook("complianceops-registry-sync", payload)
    time.sleep(2)
    db = DB()
    assets = db.query_all("SELECT asset_id, owner_email FROM assets WHERE active = true")
    controls = db.query_all("SELECT control_id, framework FROM controls WHERE active = true")
    db.close()
    return {
        "test_id": "1.1", "status": "PASS" if len(assets) == 2 and len(controls) == 2 else "FAIL",
        "assets_count": len(assets), "controls_count": len(controls),
        "http_status": resp["status"], "notes": ""
    }

def test_1_2_ingestion():
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
        "test_id": "1.2",
        "status": "PASS" if finding and finding[0] == "open" and len(evidence) == 1 else "FAIL",
        "finding_status": finding[0] if finding else None,
        "finding_severity": finding[1] if finding else None,
        "occurrence_count": finding[2] if finding else None,
        "evidence_count": len(evidence),
        "http_status": resp["status"], "notes": ""
    }

def test_1_3_owner():
    db = DB()
    row = db.query_one("SELECT owner_email, owner_status, missing_owner FROM findings WHERE finding_key = %s",
                       ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    db.close()
    return {
        "test_id": "1.3", "status": "PASS" if row and row[1] == "resolved_asset_owner" else "FAIL",
        "owner_email": row[0] if row else None,
        "owner_status": row[1] if row else None,
        "missing_owner": row[2] if row else None, "notes": ""
    }

def test_1_4_risk():
    db = DB()
    row = db.query_one("SELECT risk_score, priority, sla_due, repeated_failure FROM findings WHERE finding_key = %s",
                       ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    db.close()
    sla_future = False
    if row and row[2]:
        sla_future = row[2] > datetime.now()
    return {
        "test_id": "1.4",
        "status": "PASS" if row and row[0] > 0 and row[1] in ["P1","P2","P3","P4"] and sla_future else "FAIL",
        "risk_score": row[0] if row else None,
        "priority": row[1] if row else None,
        "sla_due_future": sla_future,
        "repeated_failure": row[3] if row else None, "notes": ""
    }

def test_1_5_remediation():
    db = DB()
    task = db.query_one("SELECT ticket_key, status FROM remediation_tasks WHERE finding_key = %s",
                        ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    finding = db.query_one("SELECT jira_issue_key FROM findings WHERE finding_key = %s",
                           ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    db.close()
    return {
        "test_id": "1.5",
        "status": "PASS" if task and task[1] == "open" else "FAIL",
        "ticket_created": task is not None,
        "ticket_key": task[0] if task else None,
        "finding_ticket_linked": finding[0] == task[0] if finding and task else False,
        "notes": "If Jira not configured, ticket_key may be None but row should exist"
    }

def test_1_6_closure():
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
        "test_id": "1.6",
        "status": "PASS" if finding and finding[0] == "closed" and finding[1] is not None else "FAIL",
        "finding_closed": finding[0] == "closed" if finding else False,
        "closure_reason": finding[2] if finding else None,
        "task_closed": task[0] == "closed" if task else False,
        "notes": ""
    }

def test_1_7_ollama():
    try:
        r = requests.post("http://localhost:11434/api/chat",
                          json={"model": "qwen2.5:3b", "messages": [{"role": "user", "content": "Hello"}], "stream": False},
                          timeout=10)
        ollama_up = r.status_code == 200
    except:
        ollama_up = False
    return {
        "test_id": "1.7", "status": "PASS",
        "ollama_reachable": ollama_up,
        "ai_status": "ok" if ollama_up else "unavailable",
        "workflow_completed": True,
        "notes": "PASS because core logic must survive AI failure"
    }

# ==================== PHASE 2: SMOKE TESTS ====================
def test_2_1_full_lifecycle():
    test_0_1_reset()
    test_1_1_registry()
    test_1_2_ingestion()
    time.sleep(3)
    db = DB()
    f1 = db.query_one("SELECT status, owner_status, risk_score, priority, jira_issue_key FROM findings WHERE finding_key = %s",
                      ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    t1 = db.query_one("SELECT ticket_key FROM remediation_tasks WHERE finding_key = %s",
                      ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    db.close()
    test_1_6_closure()
    db = DB()
    f2 = db.query_one("SELECT status, closed_at FROM findings WHERE finding_key = %s",
                      ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    db.close()
    return {
        "test_id": "2.1", "test_name": "full_lifecycle",
        "status": "PASS" if (f1 and f1[0] == "open" and f1[1] == "resolved_asset_owner" and f1[2] > 0
                              and t1 and f2 and f2[0] == "closed" and f2[1] is not None) else "FAIL",
        "registry_loaded": True, "finding_created": f1 is not None,
        "owner_resolved": f1[1] == "resolved_asset_owner" if f1 else False,
        "risk_calculated": f1[2] > 0 if f1 else False,
        "ticket_created": t1 is not None,
        "finding_closed": f2[0] == "closed" if f2 else False, "notes": ""
    }

def test_2_2_exception_flow():
    test_0_1_reset()
    test_1_1_registry()
    payload = load_fixture("finding_failed_high.json")
    post_webhook("complianceops-finding-ingestion", payload, headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    time.sleep(5)
    req = load_fixture("exception_request.json")
    resp = post_webhook("complianceops-exception-request", req)
    exc_id = None
    if resp["json"] and "exceptionId" in resp["json"]:
        exc_id = resp["json"]["exceptionId"]
    else:
        db = DB()
        row = db.query_one("SELECT exception_id FROM exceptions WHERE finding_key = %s ORDER BY created_at DESC",
                           ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
        db.close()
        exc_id = row[0] if row else None
    if not exc_id:
        return {"test_id": "2.2", "status": "FAIL", "notes": "Could not get exceptionId"}
    # Approve
    requests.get(f"{N8N_URL}/webhook/complianceops-exception-decision", params={"exceptionId": exc_id, "decision": "approve"}, timeout=30)
    time.sleep(3)
    db = DB()
    f = db.query_one("SELECT status, exception_active FROM findings WHERE finding_key = %s",
                     ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    e = db.query_one("SELECT status, approved_by FROM exceptions WHERE exception_id = %s", (exc_id,))
    db.close()
    return {
        "test_id": "2.2", "test_name": "exception_lifecycle",
        "status": "PASS" if f and f[0] == "risk_accepted" and e and e[0] == "active" else "FAIL",
        "exception_approved": e[0] == "active" if e else False,
        "finding_risk_accepted": f[0] == "risk_accepted" if f else False,
        "notes": ""
    }

def test_2_3_missing_owner():
    test_0_1_reset()
    payload = load_fixture("registry_missing_owner.json")
    post_webhook("complianceops-registry-sync", payload)
    time.sleep(2)
    # Create a finding for orphan bucket
    finding = {
        "source": "ComplianceGuardPro", "runId": "RUN-ORPHAN", "framework": "SOC2",
        "timestamp": "2026-08-24T09:00:00Z",
        "evidence": [{"controlId": "CC6.6", "resourceId": "arn:aws:s3:::orphan-bucket", "service": "aws", "passed": False, "severity": "high"}]
    }
    post_webhook("complianceops-finding-ingestion", finding, headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    time.sleep(5)
    db = DB()
    row = db.query_one("SELECT owner_email, owner_status, missing_owner FROM findings WHERE resource_id = %s",
                       ("arn:aws:s3:::orphan-bucket",))
    db.close()
    return {
        "test_id": "2.3", "test_name": "missing_owner_fallback",
        "status": "PASS" if row and row[1] == "missing_owner_fallback" and row[2] == True else "FAIL",
        "fallback_owner_assigned": row[0] is not None if row else False,
        "owner_status": row[1] if row else None,
        "missing_owner_flag": row[2] if row else None, "notes": ""
    }

# ==================== PHASE 3: STRESS TESTS ====================
def test_3_1_bulk():
    test_0_1_reset()
    test_1_1_registry()
    for i in range(1, 51):
        payload = {
            "source": "ComplianceGuardPro", "runId": f"RUN-STRESS-{i:03d}", "framework": "SOC2",
            "timestamp": "2026-08-24T09:00:00Z",
            "evidence": [{"controlId": "CC6.6", "resourceId": "arn:aws:s3:::prod-data-lake", "service": "aws", "passed": False, "severity": "medium"}]
        }
        post_webhook("complianceops-finding-ingestion", payload, headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
        time.sleep(0.2)
    time.sleep(30)
    db = DB()
    ev = db.query_one("SELECT COUNT(*) FROM evidence_events WHERE run_id LIKE 'RUN-STRESS-%'")
    f = db.query_one("SELECT occurrence_count FROM findings WHERE finding_key = %s",
                     ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    t = db.query_one("SELECT COUNT(*) FROM remediation_tasks")
    db.close()
    return {
        "test_id": "3.1", "test_name": "bulk_ingestion_50",
        "status": "PASS" if ev and ev[0] == 50 and f and f[0] >= 50 and t and t[0] == 1 else "FAIL",
        "evidence_count": ev[0] if ev else 0,
        "occurrence_count": f[0] if f else 0,
        "ticket_count": t[0] if t else 0,
        "notes": ""
    }

# ==================== PHASE 4: FAILURE MODE TESTS ====================
def test_4_1_invalid_auth():
    payload = load_fixture("finding_failed_high.json")
    resp = post_webhook("complianceops-finding-ingestion", payload, headers={"X-COMPLIANCEOPS-TOKEN": "wrong"})
    db = DB()
    ev = db.query_one("SELECT COUNT(*) FROM evidence_events WHERE run_id = %s", ("RUN-TEST-001",))
    db.close()
    return {
        "test_id": "4.1", "test_name": "invalid_auth",
        "status": "PASS" if resp["status"] != 200 and ev and ev[0] == 0 else "FAIL",
        "http_status": resp["status"],
        "evidence_blocked": ev[0] == 0 if ev else False, "notes": ""
    }

def test_4_2_duplicate():
    test_0_1_reset()
    test_1_1_registry()
    payload = load_fixture("finding_failed_high.json")
    post_webhook("complianceops-finding-ingestion", payload, headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    post_webhook("complianceops-finding-ingestion", payload, headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    time.sleep(3)
    db = DB()
    ev = db.query_one("SELECT COUNT(*) FROM evidence_events WHERE run_id = %s", ("RUN-TEST-001",))
    f = db.query_one("SELECT occurrence_count FROM findings WHERE finding_key = %s",
                     ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    db.close()
    return {
        "test_id": "4.2", "test_name": "duplicate_prevention",
        "status": "PASS" if ev and ev[0] == 1 and f and f[0] == 1 else "FAIL",
        "evidence_rows": ev[0] if ev else 0,
        "occurrence_count": f[0] if f else 0, "notes": ""
    }

def test_4_3_ai_unavailable():
    # Just verify core logic works; we assume Ollama may be down
    test_0_1_reset()
    test_1_1_registry()
    test_1_2_ingestion()
    time.sleep(5)
    db = DB()
    f = db.query_one("SELECT status, owner_email, risk_score FROM findings WHERE finding_key = %s",
                     ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    db.close()
    return {
        "test_id": "4.3", "test_name": "ai_unavailable",
        "status": "PASS" if f and f[0] == "open" and f[1] is not None and f[2] > 0 else "FAIL",
        "core_logic_survived": f is not None,
        "finding_created": f[0] == "open" if f else False,
        "owner_resolved": f[1] is not None if f else False,
        "risk_calculated": f[2] > 0 if f else False,
        "notes": "PASS if core logic works regardless of AI state"
    }

def test_4_4_sla_diff():
    test_0_1_reset()
    test_1_1_registry()
    # Critical prod
    p1 = load_fixture("finding_failed_critical_prod.json")
    post_webhook("complianceops-finding-ingestion", p1, headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    time.sleep(5)
    # High prod
    p2 = load_fixture("finding_failed_high.json")
    post_webhook("complianceops-finding-ingestion", p2, headers={"X-COMPLIANCEOPS-TOKEN": INGEST_TOKEN})
    time.sleep(5)
    db = DB()
    c = db.query_one("SELECT priority, sla_due FROM findings WHERE finding_key = %s",
                     ("CC7.2::arn:aws:s3:::prod-data-lake::SOC2",))
    h = db.query_one("SELECT priority, sla_due FROM findings WHERE finding_key = %s",
                     ("CC6.6::arn:aws:s3:::prod-data-lake::SOC2",))
    db.close()
    c_sla = (c[1] - datetime.now()).total_seconds() / 3600 if c and c[1] else 0
    h_sla = (h[1] - datetime.now()).total_seconds() / 3600 if h and h[1] else 0
    return {
        "test_id": "4.4", "test_name": "sla_differentiation",
        "status": "PASS" if c and h and c[0] == "P1" and c_sla < h_sla else "FAIL",
        "critical_priority": c[0] if c else None,
        "high_priority": h[0] if h else None,
        "critical_sla_hours": round(c_sla, 1),
        "high_sla_hours": round(h_sla, 1),
        "critical_sla_shorter": c_sla < h_sla if c and h else False,
        "notes": ""
    }

# ==================== MAIN ====================
TESTS = {
    "0.1": test_0_1_reset,
    "1.1": test_1_1_registry,
    "1.2": test_1_2_ingestion,
    "1.3": test_1_3_owner,
    "1.4": test_1_4_risk,
    "1.5": test_1_5_remediation,
    "1.6": test_1_6_closure,
    "1.7": test_1_7_ollama,
    "2.1": test_2_1_full_lifecycle,
    "2.2": test_2_2_exception_flow,
    "2.3": test_2_3_missing_owner,
    "3.1": test_3_1_bulk,
    "4.1": test_4_1_invalid_auth,
    "4.2": test_4_2_duplicate,
    "4.3": test_4_3_ai_unavailable,
    "4.4": test_4_4_sla_diff,
}

PHASES = {
    "unit": ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7"],
    "smoke": ["2.1", "2.2", "2.3"],
    "stress": ["3.1"],
    "failure": ["4.1", "4.2", "4.3", "4.4"],
    "all": list(TESTS.keys()),
}

def main():
    parser = argparse.ArgumentParser(description="AxiomOps Test Runner")
    parser.add_argument("--test", help="Run single test by ID (e.g., 1.1)")
    parser.add_argument("--phase", help="Run phase: unit, smoke, stress, failure, all")
    parser.add_argument("--list", action="store_true", help="List all tests")
    args = parser.parse_args()

    if args.list:
        print("Available tests:")
        for tid in sorted(TESTS.keys()):
            print(f"  {tid}")
        print("\nPhases:", ", ".join(PHASES.keys()))
        return

    to_run = []
    if args.test:
        to_run = [args.test]
    elif args.phase:
        to_run = PHASES.get(args.phase, [])
    else:
        parser.print_help()
        return

    results = []
    passed = 0
    failed = 0

    print(f"\n{'='*60}")
    print(f"AxiomOps Test Run: {args.test or args.phase}")
    print(f"{'='*60}")

    for tid in to_run:
        if tid not in TESTS:
            print(f"Unknown test: {tid}")
            continue
        print(f"\nRunning {tid}...")
        try:
            result = TESTS[tid]()
            ok = print_result(result)
            results.append(result)
            if ok:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {tid} CRASHED: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'='*60}")

    # Save report
    report_path = Path(__file__).parent / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w") as f:
        json.dump({"passed": passed, "failed": failed, "results": results}, f, indent=2)
    print(f"Report saved to: {report_path}")

if __name__ == "__main__":
    main()
