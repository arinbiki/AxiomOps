import json
import os
import uuid
from datetime import datetime

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), '..', 'fixtures')

def get_fixture(filename):
    filepath = os.path.join(FIXTURES_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}

def generate_finding(status="passed", severity="low", environment="development"):
    finding = {
        "id": f"find_{uuid.uuid4().hex[:12]}",
        "service_name": "api-gateway",
        "check_id": "SEC-001",
        "status": status,
        "severity": severity,
        "environment": environment,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "remediation_required": (status == "failed")
    }
    return finding

def get_unit_test_data(test_name):
    """Retrieve specific payloads based on the test type"""
    if test_name == "valid_registry":
        return get_fixture("registry_valid.json")
    elif test_name == "finding_passed":
        return get_fixture("finding_passed.json")
    elif test_name == "finding_failed_high":
        return get_fixture("finding_failed_high.json")
    elif test_name == "finding_failed_critical_prod":
        return get_fixture("finding_failed_critical_prod.json")
    elif test_name == "exception_request":
        return get_fixture("exception_request.json")
    else:
        return {}

def generate_stress_batch(size=100, status="passed"):
    """Generate a batch of findings for stress testing"""
    batch = []
    for _ in range(size):
        batch.append(generate_finding(status=status))
    return batch
