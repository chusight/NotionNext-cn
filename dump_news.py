import json, os, urllib.request, time

KEY = None
envf = os.path.expanduser("~/AppData/Local/hermes/.env")
with open(envf, encoding='utf-8') as f:
    for line in f:
        if line.startswith("NOTION_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"')
            break

def api(url, method="GET", body=None, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, method=method, headers={
                "Authorization": f"Bearer {KEY}",
                "Notion-Version": "2025-09-03",
                "Content-Type": "application/json"
            }, data=json.dumps(body).encode() if body else None)
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2)

NEWS_PAGE = "3ae379f0-985f-819c-aca8-f4985cfb465c"
d = api(f"https://api.notion.com/v1/blocks/{NEWS_PAGE}/children?page_size=100")
blocks = d.get("results", [])
print(f"News 页面全部 {len(blocks)} 块:")
for i, b in enumerate(blocks):
    t = b.get("type")
    if t in ("heading_3", "heading_2", "paragraph", "bulleted_list_item", "callout"):
        txt = ''.join(x.get("plain_text", "") for x in b.get(t, {}).get("rich_text", []))
        print(f"  [{i}] {t}: {txt[:70]}")
    elif t == "divider":
        print(f"  [{i}] ---")
    else:
        print(f"  [{i}] {t}")
