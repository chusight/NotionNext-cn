"""每日 Idea 图片任务（4:30 cron 调用）
成功方法复用：抓图 → 去重 → 直接作为 image block 追加到 Idea 页面（notion.so/image 代理，非数据库 URL）
"""
import json, os, re, urllib.request, urllib.parse, time

PAGE_ID = "3ae379f0-985f-81b7-a080-c2ae31de48f9"  # Idea 页面

# Clash 代理（Pexels 需要）
PROXY = "http://Clash:9xZDY8dL@192.168.2.10:7893"

def get_key():
    envf = os.path.expanduser("~/AppData/Local/hermes/.env")
    with open(envf, encoding='utf-8') as f:
        for line in f:
            if line.startswith("NOTION_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("找不到 NOTION_API_KEY")

def api(url, method="GET", body=None, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, method=method, headers={
                "Authorization": f"Bearer {get_key()}",
                "Notion-Version": "2025-09-03",
                "Content-Type": "application/json"
            }, data=json.dumps(body).encode() if body else None)
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))

def fetch_pexels():
    """抓取 Pexels 工业设计搜索页的图片 URL 列表（带 Openverse 备选）"""
    try:
        handler = urllib.request.ProxyHandler({"https": PROXY, "http": PROXY})
        opener = urllib.request.build_opener(handler)
        req = urllib.request.Request(
            "https://www.pexels.com/search/industrial%20design/",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0"})
        html = opener.open(req, timeout=30).read().decode('utf-8', errors='ignore')
        ids = re.findall(r'images\.pexels\.com/photos/(\d+)/pexels-photo-\d+\.(jpeg|jpg|png)', html)
        seen, urls = set(), []
        for pid, ext in ids:
            if pid in seen:
                continue
            seen.add(pid)
            urls.append(f'https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.{ext}?auto=compress&cs=tinysrgb&w=1200')
        if urls:
            return urls
    except Exception as e:
        print(f"Pexels 抓取失败({e})，切换到 Openverse")
    return fetch_openverse()

def fetch_openverse():
    """Openverse API 备选图源（免费无需 key）"""
    queries = [
        "industrial design product",
        "product design technology",
        "modern industrial product",
        "design prototype manufacturing"
    ]
    seen, urls = set(), []
    for q in queries:
        try:
            url = f"https://api.openverse.org/v1/images/?q={urllib.parse.quote(q)}&page_size=20&license_type=commercial"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            d = json.load(urllib.request.urlopen(req, timeout=25))
            for r in d.get("results", []):
                u = r.get("url", "")
                if u and u not in seen:
                    seen.add(u)
                    urls.append(u)
        except Exception as e:
            print(f"  Openverse 查询 {q} 失败: {e}")
        time.sleep(0.5)
    return urls

def get_existing_ids():
    """读取 Idea 页面已有 image block 的 pexels 图片 ID（去重用）"""
    existing = set()
    d = api(f"https://api.notion.com/v1/blocks/{PAGE_ID}/children?page_size=100")
    for b in d.get("results", []):
        if b.get("type") == "image":
            img = b.get("image", {})
            url = (img.get("external", {}) or {}).get("url", "") or (img.get("file", {}) or {}).get("url", "")
            # 提取 pexels 图片 ID
            m = re.search(r'/photos/(\d+)/', url)
            if m:
                existing.add(m.group(1))
            else:
                # notion.so/image 代理 URL 解码后提取
                dec = urllib.parse.unquote(url)
                m2 = re.search(r'/photos/(\d+)/', dec)
                if m2:
                    existing.add(m2.group(1))
                else:
                    existing.add(url)
    return existing

def notion_image_url(image_url):
    """转成 notion.so/image 代理 URL（之前成功的方式）"""
    return "https://www.notion.so/image/" + urllib.parse.quote(image_url, safe='') + "?cache=v2"

def append_image_block_to_idea(image_url):
    """把图片作为 image block 追加到 Idea 页面"""
    body = {"children": [{
        "object": "block",
        "type": "image",
        "image": {"type": "external", "external": {"url": notion_image_url(image_url)}}
    }]}
    api(f"https://api.notion.com/v1/blocks/{PAGE_ID}/children", "PATCH", body)

def main():
    # 1. 抓图
    urls = fetch_pexels()
    print(f"抓取到 {len(urls)} 张图")

    # 2. 去重（按 pexels ID）
    existing = get_existing_ids()
    print(f"Idea 页面已有 {len(existing)} 张")

    new_urls = []
    for u in urls:
        m = re.search(r'/photos/(\d+)/', u)
        pid = m.group(1) if m else u
        if pid not in existing:
            new_urls.append(u)
    print(f"可用新图 {len(new_urls)} 张")

    if not new_urls:
        print("今日无可新增图片（图库已用完，等待图源更新）")
        return

    # 3. 选一张追加为 image block（直接复制粘贴效果）
    pick = new_urls[0]
    m = re.search(r'/photos/(\d+)/', pick)
    pid = m.group(1) if m else 'new'
    append_image_block_to_idea(pick)
    print(f"✅ 已追加 image block 到 Idea 页面")
    print(f"   图片 ID: {pid}")
    print(f"   URL: {pick[:90]}")

if __name__ == "__main__":
    main()
