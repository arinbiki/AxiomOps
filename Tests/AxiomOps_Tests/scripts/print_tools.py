import re

try:
    with open('out.json', 'r') as f:
        text = f.read()
    names = re.findall(r'"name":"([^"]+)"', text)
    print("Found tools:", set(names))
except Exception as e:
    print(e)
