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

IDEA = "3ae379f0-985f-81b7-a080-c2ae31de48f9"
d = api(f"https://api.notion.com/v1/blocks/{IDEA}/children?page_size=100")
for b in d.get("results", []):
    if b.get("type") == "child_database":
        bid = b["id"]
        title = json.dumps(b.get("child_database", {}).get("title", ""), ensure_ascii=False)
        print(f"child_database: {bid} title={title[:50]}")
        # 保留 Design Inspiration，删除两个乱码库
        if "Design" not in title:
            api(f"https://api.notion.com/v1/blocks/{bid}", "DELETE")
            print(f"  -> 已删除")
