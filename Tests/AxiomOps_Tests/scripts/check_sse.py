import urllib.request
import json

url = "https://ubuntu.arindam818.cloud/mcp-server/http"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5YjU2NzE0My02MGI4LTQxNTUtYmFiOS1mYjM2OTE3YjVlMjgiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6IjFjOTI1MDAxLTcxMDAtNGYzZS05ZGFhLWU0OTBiYjAxNTNkNCIsImlhdCI6MTc4NTkxMTE4Nn0.iMC_j_etacSudRvidSAELSrXKH1rXvXH6cFjA3ElfSs",
    "Accept": "text/event-stream"
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        for _ in range(5): # read first 5 lines
            print(response.readline().decode('utf-8').strip())
except Exception as e:
    print(e)
