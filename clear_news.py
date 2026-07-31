"""第一步：彻底清空 News 页面的内容块（保留开头的 callout/说明）"""
import json, os, urllib.request, time

KEY = None
envf = os.path.expanduser("~/AppData/Local/hermes/.env")
with open(envf, encoding='utf-8') as f:
    for line in f:
        if line.startswith("NOTION_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"')
            break

NEWS_PAGE = "3ae379f0-985f-819c-aca8-f4985cfb465c"

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

# 分页读取所有块
def get_all_blocks(page_id):
    blocks, cursor = [], None
    while True:
        url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        c = api(url)
        blocks.extend(c.get("results", []))
        if c.get("has_more") and c.get("next_cursor"):
            cursor = c["next_cursor"]
        else:
            break
    return blocks

blocks = get_all_blocks(NEWS_PAGE)
print(f"News 页面共 {len(blocks)} 个块")

# 保留前 5 个（callout/divider/今日要闻/说明/divider/每日科技新闻/说明），删除其余
KEEP = 7  # callout, divider, 今日要闻, 说明, divider, 每日科技新闻, 说明
to_delete = blocks[KEEP:]
print(f"保留 {KEEP} 个，删除 {len(to_delete)} 个")

for i, b in enumerate(to_delete):
    try:
        api(f"https://api.notion.com/v1/blocks/{b['id']}", "DELETE")
        if (i + 1) % 20 == 0:
            print(f"  已删除 {i+1}/{len(to_delete)}")
    except Exception as e:
        print(f"  删除失败 {b['id'][:12]}: {e}")
    time.sleep(0.2)

print(f"完成! 剩余块数: {len(get_all_blocks(NEWS_PAGE))}")
