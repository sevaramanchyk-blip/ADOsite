import urllib.request, json

data = json.dumps({
    "method": "GET",
    "url": "https://ado-shop.com/",
    "timeout": "10",
    "redirects": "true",
    "headers": "{}",
    "body": ""
}).encode()

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/test",
    data=data,
    headers={"Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read())

print("Passed:", result["passed"], "Failed:", result["failed"])
print("Duration:", result["duration"])
for t in result["tests"]:
    s = "OK" if t["status"] == "passed" else "FAIL"
    extra = t.get("detail") or t.get("error") or ""
    print(f"  [{s}] {t['name']} ({t['duration']}) {extra}")
