import json, os, urllib.request

KEY = None
envf = os.path.expanduser("~/AppData/Local/hermes/.env")
with open(envf, encoding='utf-8') as f:
    for line in f:
        if line.startswith("NOTION_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"')
            break

def api(url, method="GET", body=None):
    req = urllib.request.Request(url, method=method, headers={
        "Authorization": f"Bearer {KEY}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json"
    }, data=json.dumps(body).encode() if body else None)
    return json.load(urllib.request.urlopen(req, timeout=30))

DS = "a0b805bc-9c5b-45c9-8782-7a456cf9c97b"
d = api(f"https://api.notion.com/v1/data_sources/{DS}/query", "POST", {"page_size": 100})
for r in d.get("results", []):
    props = r.get("properties", {})
    t = ''.join(x.get("plain_text", "") for x in (props.get("Name", {}) or {}).get("title", []))
    tp = ((props.get("type", {}) or {}).get("select") or {}).get("name")
    if not r.get("cover"):
        print(f"无封面: [{tp}] {t[:50]} | {r['id']}")
