import urllib.request
import json
import uuid
import time

class MCPFramework:
    def __init__(self, url, auth_token):
        self.url = url
        self.auth_token = auth_token
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Accept': 'application/json, text/event-stream',
            'Content-Type': 'application/json'
        }

    def _call_tool(self, tool_name, args):
        payload = {
            'jsonrpc': '2.0',
            'id': str(uuid.uuid4()),
            'method': 'tools/call',
            'params': {
                'name': tool_name,
                'arguments': args
            }
        }
        
        req = urllib.request.Request(self.url, json.dumps(payload).encode('utf-8'), self.headers)
        try:
            with urllib.request.urlopen(req) as res:
                content = res.read().decode('utf-8')
                
                # Because the endpoint uses SSE, we need to parse the event stream
                # to extract the response. The 'tools/call' JSON-RPC response might be 
                # in one of the SSE 'message' events.
                for line in content.splitlines():
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            if 'result' in data:
                                return data['result']
                            elif 'error' in data:
                                raise Exception(f"MCP Error: {data['error']}")
                        except json.JSONDecodeError:
                            pass
                return None
        except urllib.error.HTTPError as e:
            error_text = e.read().decode('utf-8')
            raise Exception(f"HTTPError {e.code}: {error_text}")

    def execute_workflow(self, workflow_id, execution_mode="manual", webhook_method="POST", payload=None):
        if not payload:
            payload = {}

        # 1. Ask MCP which nodes need pin data
        prepare_res = self._call_tool("prepare_test_pin_data", {"workflowId": workflow_id})
        if not prepare_res or not prepare_res.get("content"):
            return None, None
            
        pin_data_payload = {}
        trigger_node_name = None
        
        try:
            content_json = prepare_res["content"][0]["text"]
            prep_data = json.loads(content_json)
            
            # Nodes that need schema generation
            schemas = prep_data.get("nodeSchemasToGenerate", {})
            for node_name, schema in schemas.items():
                # Just mock with empty dict by default, since LLM doesn't easily have a schema fuzzer here
                pin_data_payload[node_name] = [{"json": {}}]
                # If it looks like a trigger, save it for our payload
                if 'trigger' in node_name.lower() or 'webhook' in node_name.lower():
                    trigger_node_name = node_name
                    
            # Nodes without schema
            no_schema = prep_data.get("nodesWithoutSchema", [])
            for node_name in no_schema:
                pin_data_payload[node_name] = [{"json": {}}]
                if 'trigger' in node_name.lower() or 'webhook' in node_name.lower():
                    trigger_node_name = node_name
                    
        except (json.JSONDecodeError, KeyError):
            pass

        # If we couldn't confidently find a trigger by name, we might just inject the payload into the first node that needed pinning
        if not trigger_node_name and pin_data_payload:
            trigger_node_name = list(pin_data_payload.keys())[0]

        # Inject our actual test payload into the trigger node
        if trigger_node_name:
            pin_data_payload[trigger_node_name] = [{"json": payload}]

        args = {
            "workflowId": workflow_id,
            "pinData": pin_data_payload
        }
        
        result = self._call_tool("test_workflow", args)
        if result and "content" in result and len(result["content"]) > 0:
            content_json = result["content"][0]["text"]
            try:
                data = json.loads(content_json)
                return data.get("executionId"), data.get("status")
            except json.JSONDecodeError:
                return None, None
        return None, None

    def get_execution(self, workflow_id, execution_id, include_data=False):
        args = {
            "workflowId": workflow_id,
            "executionId": execution_id,
            "includeData": include_data
        }
        result = self._call_tool("get_execution", args)
        if result and "content" in result and len(result["content"]) > 0:
            content_json = result["content"][0]["text"]
            try:
                data = json.loads(content_json)
                return data
            except json.JSONDecodeError:
                return None
        return None

    def wait_for_execution(self, workflow_id, execution_id, timeout_seconds=30, poll_interval=2):
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            execution_data = self.get_execution(workflow_id, execution_id, include_data=False)
            if execution_data and "execution" in execution_data and execution_data["execution"]:
                status = execution_data["execution"].get("status")
                # Typical n8n statuses: 'success', 'error', 'canceled', 'running', 'waiting'
                if status in ["success", "error", "canceled"]:
                    return execution_data
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Execution {execution_id} did not complete within {timeout_seconds} seconds")
