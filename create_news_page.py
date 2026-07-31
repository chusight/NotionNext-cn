"""创建 News 导航页面：简要文字瀑布流展示每日科技新闻
方案：News 页面用 database 内嵌 + 简洁文字列表，NotionNext 渲染时用现有瀑布流 CSS
"""
import json, os, urllib.request

KEY = None
envf = os.path.expanduser("~/AppData/Local/hermes/.env")
with open(envf, encoding='utf-8') as f:
    for line in f:
        if line.startswith("NOTION_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"')
            break

LOFT_DB = "234a8ab8-5c9b-41a4-b0d9-51afd44f499a"

def api(url, method="GET", body=None):
    req = urllib.request.Request(url, method=method, headers={
        "Authorization": f"Bearer {KEY}",
        "Notion-Version": "2025-09-03",
        "Content-Type": "application/json"
    }, data=json.dumps(body).encode() if body else None)
    return json.load(urllib.request.urlopen(req, timeout=30))

def h2(text):
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def para(text):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def bullet(text):
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def callout(text, emoji="📰"):
    return {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": text}}], "icon": {"type": "emoji", "emoji": emoji}}}

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

# 检查是否已存在 News 行
DS = "a0b805bc-9c5b-45c9-8782-7a456cf9c97b"
q = api(f"https://api.notion.com/v1/data_sources/{DS}/query", "POST", {"page_size": 100})
for r in q.get("results", []):
    props = r.get("properties", {})
    t = ''.join(x.get("plain_text", "") for x in (props.get("Name", {}) or {}).get("title", []))
    if t == "News":
        print("已存在 News 页面:", r["id"])
        raise SystemExit(0)

children = [
    callout("每日科技新闻速览：聚焦 AI、芯片、AR/VR、医疗器械等前沿领域。每天更新，欢迎常来看看。", "📰"),
    divider(),
    h2("今日要闻"),
    para("（每日任务自动更新：从下方「每日科技新闻」数据库读取最新内容）"),
    divider(),
    h2("每日科技新闻"),
    para("以下为每日自动生成的科技新闻汇总："),
]

body = {
    "parent": {"database_id": LOFT_DB},
    "properties": {
        "Name": {"title": [{"type": "text", "text": {"content": "News"}}]},
        "status": {"select": {"name": "Published"}},
        "type": {"select": {"name": "Page"}},
        "date": {"date": {"start": "2026-08-01"}},
        "summary": {"rich_text": [{"type": "text", "text": {"content": "每日科技新闻速览"}}]},
        "slug": {"rich_text": [{"type": "text", "text": {"content": "news"}}]}
    },
    "children": children
}
d = api("https://api.notion.com/v1/pages", "POST", body)
print("✅ News 页面已创建!")
print("   ID:", d.get("id"))
print("   URL:", d.get("url"))
