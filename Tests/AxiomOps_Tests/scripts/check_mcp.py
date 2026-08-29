import urllib.request
import json
import uuid

url = "https://ubuntu.arindam818.cloud/mcp-server/http"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5YjU2NzE0My02MGI4LTQxNTUtYmFiOS1mYjM2OTE3YjVlMjgiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6IjFjOTI1MDAxLTcxMDAtNGYzZS05ZGFhLWU0OTBiYjAxNTNkNCIsImlhdCI6MTc4NTkxMTE4Nn0.iMC_j_etacSudRvidSAELSrXKH1rXvXH6cFjA3ElfSs",
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json"
}

payload = {
    "jsonrpc": "2.0",
    "id": str(uuid.uuid4()),
    "method": "tools/list",
    "params": {}
}

req = urllib.request.Request(url, json.dumps(payload).encode('utf-8'), headers)
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code} {e.reason}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(e)
