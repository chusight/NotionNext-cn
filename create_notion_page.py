"""在 LOFT 数据库创建名为 notion 的 Page 类型页面，用于导航栏"""
import json, os, urllib.request

KEY = None
envf = os.path.expanduser("~/AppData/Local/hermes/.env")
with open(envf, encoding='utf-8') as f:
    for line in f:
        if line.startswith("NOTION_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"')
            break

LOFT_DB = "234a8ab8-5c9b-41a4-b0d9-51afd44f499a"  # LOFT 数据库

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

def callout(text, emoji="📖"):
    return {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": text}}], "icon": {"type": "emoji", "emoji": emoji}}}

children = [
    callout("本站是 lee 用 NotionNext + Cloudflare Pages 搭建的个人博客，本页分享搭建相关的资源与经验。", "🌐"),
    h2("Notion 相关资源"),
    bullet("NotionNext 项目：github.com/notionnext-org/NotionNext"),
    bullet("官方文档：docs.notionnext.com"),
    bullet("主题预览：preview.tangly1024.com"),
    bullet("Notion API 文档：developers.notion.com"),
    h2("搭建教程"),
    para("想自己搭建一个这样的网站？可以参考本站的教程文章：《手把手教你用 NotionNext + Cloudflare Pages 搭建免费静态博客站》。"),
    para("教程涵盖了：Notion 数据库配置、NotionNext 部署、静态构建、Cloudflare Pages 托管、自定义域名绑定、自动化更新，以及常见问题排查。"),
    h2("本站使用的技术栈"),
    bullet("内容管理：Notion 数据库（公开分享）"),
    bullet("网站框架：NotionNext 4.10.8"),
    bullet("主题：Heo"),
    bullet("托管：Cloudflare Pages（免费 CDN + HTTPS）"),
    bullet("域名：ligan.cc（Cloudflare DNS）"),
]

# 检查是否已存在名为 notion 的行
DS = "a0b805bc-9c5b-45c9-8782-7a456cf9c97b"
q = api(f"https://api.notion.com/v1/data_sources/{DS}/query", "POST", {"page_size": 100})
for r in q.get("results", []):
    props = r.get("properties", {})
    t = ''.join(x.get("plain_text", "") for x in (props.get("Name", {}) or {}).get("title", []))
    tp = ((props.get("type", {}) or {}).get("select") or {}).get("name")
    if t == "notion" and tp == "Page":
        print("已存在 notion 页面:", r["id"])
        raise SystemExit(0)

body = {
    "parent": {"database_id": LOFT_DB},
    "properties": {
        "Name": {"title": [{"type": "text", "text": {"content": "notion"}}]},
        "status": {"select": {"name": "Published"}},
        "type": {"select": {"name": "Page"}},
        "date": {"date": {"start": "2026-08-01"}},
        "summary": {"rich_text": [{"type": "text", "text": {"content": "Notion 搭建相关资源与教程"}}]},
        "slug": {"rich_text": [{"type": "text", "text": {"content": "notion"}}]}
    },
    "children": children
}
d = api("https://api.notion.com/v1/pages", "POST", body)
print("✅ notion 页面已创建!")
print("   ID:", d.get("id"))
print("   URL:", d.get("url"))
