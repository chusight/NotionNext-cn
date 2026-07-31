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

def query_all(source_id):
    rows, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        d = api(f"https://api.notion.com/v1/data_sources/{source_id}/query", "POST", body)
        for r in d.get("results", []):
            props = r.get("properties", {})
            t = ''
            for p in props.values():
                if p.get("type") == "title":
                    t = ''.join(x.get("plain_text", "") for x in p.get("title", []))
                    break
            rows.append({"id": r["id"], "title": t, "cover": r.get("cover")})
        if d.get("has_more") and d.get("next_cursor"):
            cursor = d["next_cursor"]
        else:
            break
    return rows

OLD_SOURCE = "7952a43e-0e19-4c86-baca-51624ece3789"
NEW_SOURCE = "a0b805bc-9c5b-45c9-8782-7a456cf9c97b"

old_rows = query_all(OLD_SOURCE)
new_rows = query_all(NEW_SOURCE)
new_by_title = {}
for r in new_rows:
    if r["title"] not in new_by_title:
        new_by_title[r["title"]] = r

def to_external_cover(cover):
    """file 类型封面转 external（用 notion.so/image 代理）"""
    if cover.get("type") == "external":
        return cover
    url = cover.get("file", {}).get("url", "")
    if not url:
        return None
    proxy = "https://www.notion.so/image/" + urllib.parse.quote(url, safe='')
    return {"type": "external", "external": {"url": proxy + "?cache=v2"}}

ok, fail = 0, 0
for o in old_rows:
    if not o["cover"] or o["cover"].get("type") != "file":
        continue
    n = new_by_title.get(o["title"])
    if not n or n.get("cover"):
        continue
    ext = to_external_cover(o["cover"])
    if not ext:
        fail += 1
        continue
    try:
        api(f"https://api.notion.com/v1/pages/{n['id']}", "PATCH", {"cover": ext})
        ok += 1
        print(f"  ✅ {o['title'][:35]}")
    except Exception as e:
        fail += 1
        print(f"  ❌ {o['title'][:35]}: {e}")

print(f"\n完成: 复制 {ok} 篇, 失败 {fail} 篇")
