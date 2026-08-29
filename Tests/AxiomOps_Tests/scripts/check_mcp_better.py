import urllib.request
import json
import uuid
import sys

url = 'https://ubuntu.arindam818.cloud/mcp-server/http'
headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5YjU2NzE0My02MGI4LTQxNTUtYmFiOS1mYjM2OTE3YjVlMjgiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6IjFjOTI1MDAxLTcxMDAtNGYzZS05ZGFhLWU0OTBiYjAxNTNkNCIsImlhdCI6MTc4NTkxMTE4Nn0.iMC_j_etacSudRvidSAELSrXKH1rXvXH6cFjA3ElfSs',
    'Accept': 'application/json, text/event-stream',
    'Content-Type': 'application/json'
}
payload = {
    'jsonrpc': '2.0',
    'id': str(uuid.uuid4()),
    'method': 'tools/list',
    'params': {}
}
req = urllib.request.Request(url, json.dumps(payload).encode('utf-8'), headers)

try:
    with urllib.request.urlopen(req) as res:
        data = res.read().decode('utf-8')
        with open('out.json', 'w') as f:
            f.write(data)
        print("Success, wrote to out.json")
except urllib.error.HTTPError as e:
    data = e.read().decode('utf-8')
    with open('out.json', 'w') as f:
        f.write(data)
    print(f"HTTP Error {e.code}, wrote to out.json")
except Exception as e:
    print(f"Exception: {e}")
