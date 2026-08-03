"""修复 News 页面：恢复被 cron 误删的旧条目（06-18 ~ 07-31，倒序追加到 08-01 之后）"""
import json, os, urllib.request, time, re
from datetime import datetime
from collections import OrderedDict

KEY = None
envf = os.path.expanduser("~/AppData/Local/hermes/.env")
with open(envf, encoding='utf-8') as f:
    for line in f:
        if line.startswith("NOTION_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"')
            break

NEWS_PAGE = "3ae379f0-985f-819c-aca8-f4985cfb465c"
OLD_PAGE = "382379f0-985f-80e0-bdb8-efa8014fed03"

def api(url, method="GET", body=None, retries=4):
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
            time.sleep(2 * (attempt + 1))

def parse_date(title):
    m = re.search(r'(\d{4})[年\-](\d{1,2})[月\-](\d{1,2})', title)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None

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

# 1. 读取 News 页面现有条目日期（避免重复）
existing_blocks = get_all_blocks(NEWS_PAGE)
existing_dates = set()
for b in existing_blocks:
    if b.get("type") == "heading_3":
        txt = ''.join(x.get("plain_text", "") for x in b.get("heading_3", {}).get("rich_text", []))
        m = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', txt)
        if m:
            existing_dates.add(f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}")
print(f"News 已有条目: {sorted(existing_dates)}")

# 2. 读取旧页面子页面，按日期去重、倒序
d = api(f"https://api.notion.com/v1/blocks/{OLD_PAGE}/children?page_size=100")
children = [b for b in d.get("results", []) if b.get("type") == "child_page"]
by_date = OrderedDict()
for child in children:
    title = child.get("child_page", {}).get("title", "")
    dt = parse_date(title)
    if not dt:
        continue
    key = dt.strftime("%Y-%m-%d")
    if key not in by_date:
        by_date[key] = {"id": child["id"], "title": title, "dt": dt}

# 只恢复缺失的（不含 08-01）
missing = [v for k, v in by_date.items() if k not in existing_dates]
missing.sort(key=lambda x: x["dt"], reverse=True)
print(f"需恢复: {len(missing)} 天")

# 3. 提取摘要
def extract_summary(child_id, max_items=5):
    try:
        c = api(f"https://api.notion.com/v1/blocks/{child_id}/children?page_size=100")
    except Exception:
        return []
    items, in_top = [], False
    for b in c.get("results", []):
        t = b.get("type")
        if t == "heading_2":
            txt = ''.join(x.get("plain_text", "") for x in b.get(t, {}).get("rich_text", []))
            in_top = "要闻" in txt or "🔥" in txt
        elif t == "heading_3" and in_top:
            txt = ''.join(x.get("plain_text", "") for x in b.get(t, {}).get("rich_text", []))
            if txt and len(items) < max_items:
                items.append(txt.lstrip("0123456789. ").strip())
    return items

# 4. 追加到 News 页面（倒序，08-01 已在最前）
print("\n恢复中...")
for idx, day in enumerate(missing):
    display = day["dt"].strftime("%Y年%m月%d日")
    page_url = f"https://www.notion.so/{day['id'].replace('-', '')}"
    summary = extract_summary(day["id"])
    blocks_out = [
        {"object": "block", "type": "heading_3",
         "heading_3": {"rich_text": [{"type": "text", "text": {"content": f"📅 {display}"}}]}}
    ]
    for s in summary:
        blocks_out.append({
            "object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": s[:60]}}]}
        })
    blocks_out.append({
        "object": "block", "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {
            "content": "点击查看当日完整新闻 →", "link": {"url": page_url}}}]}
    })
    blocks_out.append({"object": "block", "type": "divider", "divider": {}})
    try:
        api(f"https://api.notion.com/v1/blocks/{NEWS_PAGE}/children", "PATCH", {"children": blocks_out})
        print(f"  [{idx+1}/{len(missing)}] {display} ({len(summary)} 条)")
    except Exception as e:
        print(f"  ❌ {display}: {e}")
    time.sleep(0.4)

print("\n完成!")
