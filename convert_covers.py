"""把外站(external)封面统一转为 notion.so/image 代理 URL，解决热链不稳定导致缩略图空白"""
import json, os, urllib.request, urllib.parse

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
rows, cursor = [], None
while True:
    body = {"page_size": 100}
    if cursor:
        body["start_cursor"] = cursor
    d = api(f"https://api.notion.com/v1/data_sources/{DS}/query", "POST", body)
    for r in d.get("results", []):
        props = r.get("properties", {})
        t = ''.join(x.get("plain_text", "") for x in (props.get("Name", {}) or {}).get("title", []))
        rows.append({"id": r["id"], "title": t, "cover": r.get("cover")})
    if d.get("has_more") and d.get("next_cursor"):
        cursor = d["next_cursor"]
    else:
        break

def is_external_hotlink(cover):
    """外站热链 = external 且不是 unsplash/notion 代理"""
    if not cover or cover.get("type") != "external":
        return False
    u = cover.get("external", {}).get("url", "")
    return not ("unsplash" in u or "notion.so/image" in u or "prod-files" in u)

def to_proxy(cover):
    u = cover["external"]["url"]
    proxy = "https://www.notion.so/image/" + urllib.parse.quote(u, safe='') + "?cache=v2"
    return {"type": "external", "external": {"url": proxy}}

ok, skip = 0, 0
for r in rows:
    if is_external_hotlink(r["cover"]):
        new_cover = to_proxy(r["cover"])
        try:
            api(f"https://api.notion.com/v1/pages/{r['id']}", "PATCH", {"cover": new_cover})
            ok += 1
            print(f"  ✅ {r['title'][:30]}")
        except Exception as e:
            print(f"  ❌ {r['title'][:30]}: {e}")
    else:
        skip += 1

print(f"\n完成: 转换 {ok} 篇, 跳过 {skip} 篇")
