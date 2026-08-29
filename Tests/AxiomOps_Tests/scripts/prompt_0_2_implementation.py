#!/usr/bin/env python3
"""
Prompt 0.2 — Verify n8n Workflows Are Active

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 0.2:
- Verify all 11 AxiomOps workflows exist and are active
- Check specific workflow names
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Use MCP to list workflows or call GET http://localhost:5678/api/v1/workflows
2. Check these exact workflow names exist:
   00_error_handler, 01_registry_sync,
   02_finding_ingestion,
   03_owner_resolver, 04_risk_prioritizer,
   05_remediation_orchestrator,
   06_exception_request, 06b_exception_decision, 07_aging_digest,
   08_closure_validator, 09_ollama_assistant
3. Check which ones are active.

EXPECTED OUTPUT FORMAT:
{
  "phase": "0.2",
  "status": "PASS or FAIL",
  "workflows_found": ["list of names found"],
  "workflows_missing": ["list of names missing"],
  "active_count": 0,
  "notes": ""
}

DO NOT:
- Activate workflows yourself
- Modify any workflow
- Ask me for API credentials
"""

import json
import requests
from datetime import datetime

# ==================== CONFIGURATION ====================
# These should match your actual n8n configuration
N8N_URL = "http://localhost:5678"
EXPECTED_WORKFLOWS = [
    "00_error_handler",
    "01_registry_sync",
    "02_finding_ingestion",
    "03_owner_resolver",
    "04_risk_prioritizer",
    "05_remediation_orchestrator",
    "06_exception_request",
    "06b_exception_decision",
    "07_aging_digest",
    "08_closure_validator",
    "09_ollama_assistant"
]

# ==================== HTTP HELPER ====================
class HTTPClient:
    """Manages HTTP requests to n8n API"""
    
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_workflows(self):
        """Get all workflows from n8n API"""
        try:
            url = f"{self.base_url}/api/v1/workflows"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to fetch workflows: {e}")
            return None

# ==================== MAIN IMPLEMENTATION ====================
def main():
    """Execute the exact steps from Prompt 0.2"""
    
    print("=" * 60)
    print("ROLE: n8n Health Check Agent")
    print("TASK: Verify all 11 AxiomOps workflows exist and are active.")
    print("=" * 60)
    print()
    
    # Step 1: Use MCP to list workflows or call GET http://localhost:5678/api/v1/workflows
    print("EXACT STEPS:")
    print("1. Use MCP to list workflows or call GET http://localhost:5678/api/v1/workflows")
    
    client = HTTPClient(N8N_URL)
    workflows_data = client.get_workflows()
    
    if workflows_data is None:
        # Return error format as specified
        error_result = {
            "phase": "0.2",
            "status": "FAIL",
            "workflows_found": [],
            "workflows_missing": EXPECTED_WORKFLOWS,
            "active_count": 0,
            "notes": "Failed to connect to n8n API"
        }
        print("\n❌ Failed to connect to n8n API")
        print("\nEXPECTED OUTPUT FORMAT (return ONLY this JSON):")
        print(json.dumps(error_result, indent=2))
        return error_result
    
    # Step 2: Check these exact workflow names exist
    print("2. Check these exact workflow names exist:")
    for wf in EXPECTED_WORKFLOWS:
        print(f"   - {wf}")
    
    # Extract workflow names from API response
    workflows_found = []
    workflows_missing = []
    active_count = 0
    
    # Handle different API response formats
    if isinstance(workflows_data, dict):
        if "workflows" in workflows_data:
            workflows_list = workflows_data["workflows"]
        elif "data" in workflows_data:
            workflows_list = workflows_data["data"]
        else:
            workflows_list = workflows_data
    elif isinstance(workflows_data, list):
        workflows_list = workflows_data
    else:
        workflows_list = []
    
    # Process each workflow
    for workflow in workflows_list:
        if isinstance(workflows, dict):
            name = workflow.get("name", "")
            active = workflow.get("active", False)
        else:
            name = str(workflow)
            active = False
        
        if name in EXPECTED_WORKFLOWS:
            workflows_found.append(name)
            if active:
                active_count += 1
        else:
            workflows_missing.append(name)
    
    # Check which expected workflows are missing
    for expected_wf in EXPECTED_WORKFLOWS:
        if expected_wf not in workflows_found:
            workflows_missing.append(expected_wf)
    
    # Determine status
    status = "PASS" if len(workflows_missing) == 0 else "FAIL"
    
    # Prepare result in exact format specified
    result = {
        "phase": "0.2",
        "status": status,
        "workflows_found": workflows_found,
        "workflows_missing": workflows_missing,
        "active_count": active_count,
        "notes": ""
    }
    
    print(f"\n📊 Verification Results:")
    print(f"   - Workflows found: {len(workflows_found)}/{len(EXPECTED_WORKFLOWS)}")
    print(f"   - Workflows missing: {len(workflows_missing)}")
    print(f"   - Active workflows: {active_count}")
    print(f"   - Overall status: {status}")
    
    if workflows_found:
        print(f"   - Found workflows: {', '.join(workflows_found)}")
    if workflows_missing:
        print(f"   - Missing workflows: {', '.join(workflows_missing)}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result, indent=2))
    
    return result

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 0.2 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)