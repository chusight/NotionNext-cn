"""把 LOFT 数据库中的每日科技新闻以简要文字形式（标题+日期+摘要）写入 News 页面"""
import json, os, urllib.request, time

KEY = None
envf = os.path.expanduser("~/AppData/Local/hermes/.env")
with open(envf, encoding='utf-8') as f:
    for line in f:
        if line.startswith("NOTION_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"')
            break

NEWS_PAGE = "3ae379f0-985f-819c-aca8-f4985cfb465c"

def api(url, method="GET", body=None):
    req = urllib.request.Request(url, method=method, headers={
        "Authorization": f"Bearer {KEY}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json"
    }, data=json.dumps(body).encode() if body else None)
    return json.load(urllib.request.urlopen(req, timeout=30))

# 1. 查询 LOFT 数据库所有 Post 文章
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
        tp = ((props.get("type", {}) or {}).get("select") or {}).get("name")
        summary = ''.join(x.get("plain_text", "") for x in (props.get("summary", {}) or {}).get("rich_text", []))
        date = ((props.get("date", {}) or {}).get("date") or {}).get("start", "")
        rows.append({"title": t, "type": tp, "summary": summary, "date": date})
    if d.get("has_more") and d.get("next_cursor"):
        cursor = d["next_cursor"]
    else:
        break

posts = [r for r in rows if r["type"] == "Post"]
posts.sort(key=lambda x: x["date"], reverse=True)
print(f"找到 {len(posts)} 篇 Post 文章")

# 2. 生成简要条目 blocks（标题 + 日期 + 摘要，用 bullet + callout 形式）
children = []
for p in posts[:60]:
    date_str = p["date"][:10] if p["date"] else ""
    title = p["title"]
    summary = p["summary"] if p["summary"] else "（暂无摘要）"
    # 每条新闻：heading_3 标题 + paragraph 摘要
    children.append({
        "object": "block", "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": title}}]}
    })
    children.append({
        "object": "block", "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"📅 {date_str} · {summary}"}}]}
    })

# 3. 分批写入（每批 20 块）
print(f"生成 {len(children)} 个块")
for i in range(0, len(children), 20):
    batch = children[i:i+20]
    api(f"https://api.notion.com/v1/blocks/{NEWS_PAGE}/children", "PATCH", {"children": batch})
    print(f"  已写入 {i+len(batch)}/{len(children)}")
    time.sleep(1)
print("完成!")
