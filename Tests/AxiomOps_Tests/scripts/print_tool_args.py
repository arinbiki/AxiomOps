import json
import re

try:
    with open('out.json', 'r') as f:
        text = f.read()
    
    # Extract just the JSON part from the SSE event
    # Find the line starting with data:
    for line in text.splitlines():
        if line.startswith('data: {"jsonrpc"'):
            data = json.loads(line[6:])
            tools = data.get('result', {}).get('tools', [])
            for t in tools:
                if t['name'] in ['execute_workflow', 'test_workflow']:
                    print(json.dumps(t, indent=2))
except Exception as e:
    print(e)
