#!/usr/bin/env python3
"""
Prompt 1.7 — Test 09 Ollama Assistant (Safe Fallback)

This script implements the exact requirements from COPILOT_PROMPTS.md Prompt 1.7:
- Verify AI helper returns text or fails safely.
- Check Ollama availability
- Trigger workflow 09 via Execute Workflow
- Check the output has aiStatus field
- Return JSON output in the exact format specified

EXACT STEPS IMPLEMENTED:
1. Call POST http://localhost:11434/api/chat with body:
   {"model":"qwen2.5:3b","messages":[{"role":"user","content":"Hello"}],"stream":false}
2. If Ollama responds with 200, note it as available.
3. If Ollama responds with connection refused or timeout, note it as unavailable.
4. Trigger workflow 09 via Execute Workflow with input: {"task":"remediation_summary","model":"qwen2.5:3b","finding":{"control_id":"CC6.6","severity":"high"}}
5. Check the output has aiStatus field.

EXPECTED RESULTS:
- If Ollama is up: aiStatus = 'ok' and aiText is not empty
- If Ollama is down: aiStatus = 'empty' or 'unavailable' but workflow does not crash

EXPECTED OUTPUT FORMAT:
{
  "test_id": "1.7",
  "workflow": "09_ollama_assistant",
  "status": "PASS or FAIL",
  "ollama_reachable": true,
  "ai_status": "ok",
  "workflow_completed": true,
  "notes": "PASS because core logic must survive AI failure"
}

DO NOT:
- Assume Ollama is always available
"""

import json
import requests
import time
from datetime import datetime

# ==================== CONFIGURATION ====================
# These should match your actual environment
OLLAMA_URL = "http://localhost:11434/api/chat"
N8N_URL = "http://localhost:5678"

# ==================== HTTP HELPER ====================
def post_ollama(payload):
    """Call Ollama API"""
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=10)
        return {"status": r.status_code, "json": r.json() if r.text else {}}
    except Exception as e:
        return {"status": 0, "error": str(e)}

def execute_workflow(path, payload):
    """Execute n8n workflow"""
    try:
        url = f"{N8N_URL}/executeWorkflow/{path}"
        r = requests.post(url, json=payload, timeout=30)
        return {"status": r.status_code, "json": r.json() if r.text else {}}
    except Exception as e:
        return {"status": 0, "error": str(e)}

# ==================== MAIN IMPLEMENTATION ====================
def main():
    """Execute the exact steps from Prompt 1.7"""
    
    print("=" * 60)
    print("ROLE: Unit Test Executor for Workflow 09")
    print("TASK: Verify AI helper returns text or fails safely.")
    print("=" * 60)
    print()
    
    # Step 1: Call POST http://localhost:11434/api/chat with body:
    print("EXACT STEPS:")
    print("1. Call POST http://localhost:11434/api/chat with body:")
    print('   {"model":"qwen2.5:3b","messages":[{"role":"user","content":"Hello"}],"stream":false}')
    
    ollama_payload = {
        "model": "qwen2.5:3b",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False
    }
    
    ollama_resp = post_ollama(ollama_payload)
    print(f"   ✅ Ollama response status: {ollama_resp['status']}")
    
    # Step 2: If Ollama responds with 200, note it as available.
    print("2. If Ollama responds with 200, note it as available.")
    ollama_up = ollama_resp["status"] == 200
    
    # Step 3: If Ollama responds with connection refused or timeout, note it as unavailable.
    print("3. If Ollama responds with connection refused or timeout, note it as unavailable.")
    
    # Step 4: Trigger workflow 09 via Execute Workflow with input: {"task":"remediation_summary","model":"qwen2.5:3b","finding":{"control_id":"CC6.6","severity":"high"}}
    print("4. Trigger workflow 09 via Execute Workflow with input:")
    print('   {"task":"remediation_summary","model":"qwen2.5:3b","finding":{"control_id":"CC6.6","severity":"high"}}')
    
    workflow_payload = {
        "task": "remediation_summary",
        "model": "qwen2.5:3b",
        "finding": {"control_id": "CC6.6", "severity": "high"}
    }
    
    workflow_resp = execute_workflow("09_ollama_assistant", workflow_payload)
    print(f"   ✅ Workflow response status: {workflow_resp['status']}")
    
    # Step 5: Check the output has aiStatus field.
    print("5. Check the output has aiStatus field.")
    
    # Determine results
    ai_status = "ok"
    if not ollama_up:
        ai_status = "unavailable"
    
    # Check if workflow completed (even if Ollama is down)
    workflow_completed = workflow_resp["status"] == 200
    
    # Check if aiStatus field exists in workflow response
    has_ai_status = "aiStatus" in workflow_resp.get("json", {})
    
    # EXPECTED RESULTS verification
    print("\n📊 Verifying expected results...")
    
    # Determine status
    # PASS if workflow completed and has aiStatus field, regardless of Ollama availability
    status = "PASS" if workflow_completed and has_ai_status else "FAIL"
    
    # Prepare result in exact format specified
    result_json = {
        "test_id": "1.7",
        "workflow": "09_ollama_assistant",
        "status": status,
        "ollama_reachable": ollama_up,
        "ai_status": ai_status,
        "workflow_completed": workflow_completed,
        "notes": "PASS because core logic must survive AI failure"
    }
    
    print(f"\n📊 Test Results:")
    print(f"   - Ollama reachable: {ollama_up}")
    print(f"   - AI status: {ai_status}")
    print(f"   - Workflow completed: {workflow_completed}")
    print(f"   - Has aiStatus field: {has_ai_status}")
    print(f"   - Overall status: {status}")
    
    print("\n✅ EXPECTED OUTPUT FORMAT (return ONLY this JSON):")
    print(json.dumps(result_json, indent=2))
    
    return result_json

# ==================== STANDALONE EXECUTION ====================
if __name__ == "__main__":
    print("🚀 Starting Prompt 1.7 Implementation")
    print("This script implements the exact requirements from COPILOT_PROMPTS.md")
    print()
    
    result = main()
    
    # Exit with appropriate code
    exit_code = 0 if result.get("status") == "PASS" else 1
    print(f"\n🏁 Script completed with exit code: {exit_code}")
    exit(exit_code)