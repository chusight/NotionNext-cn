"""将 LOFT 内容搬运到 NotionNext 标准数据库 (234a8ab8-5c9b-41a4-b0d9-51afd44f499a)
- Me / Idea / Connect 子页面 -> type=Page 单页
- BLOG 数据库 52 篇文章 -> type=Post
"""
import urllib.request, json, os, time, sys

KEY = os.environ['NOTION_KEY']
HDRS = {
    "Authorization": f"Bearer {KEY}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json"
}
NEW_DB = "234a8ab8-5c9b-41a4-b0d9-51afd44f499a"       # database ID (NotionNext NOTION_PAGE_ID 用)
NEW_COLLECTION = "a0b805bc-9c5b-45c9-8782-7a456cf9c97b"  # collection/data_source ID (API 查询行用)
LOFT = "ca1a6948-a53f-4562-a47c-e83a9412b4b7"
BLOG_DS = "7952a43e-0e19-4c86-baca-51624ece3789"

def api(url, method="GET", body=None, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, method=method, headers=HDRS,
                                         data=json.dumps(body).encode() if body else None)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:200]
            if e.code == 429:
                time.sleep(2 + i * 3)
                continue
            raise RuntimeError(f"HTTP {e.code}: {err}")
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(2)
    raise RuntimeError("retries exhausted")

def get_children(block_id):
    """分页获取所有子块"""
    out, cursor = [], None
    while True:
        url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        d = api(url)
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
        time.sleep(0.35)
    return out

def simplify_block(b, depth=0):
    """把 Notion 块转成可创建的块；跳过 child_database/child_page，复杂块降级为段落文本"""
    t = b.get("type")
    if depth > 4:
        return None
    if t in ("child_database", "child_page"):
        return None
    if t == "column_list":
        cols = []
        for cb in get_children(b["id"]):
            if cb.get("type") == "column":
                items = []
                for gb in get_children(cb["id"]):
                    s = simplify_block(gb, depth + 1)
                    if s:
                        items.append(s)
                if items:
                    cols.append({"object": "block", "type": "column",
                                 "column": {"children": items}})
        if len(cols) == 1:
            # 单列直接展开为内容块（column_list 要求至少 2 列）
            return cols[0]["column"]["children"]
        if len(cols) < 2:
            return None
        return {"object": "block", "type": "column_list", "column_list": {"children": cols}}
    if t in ("bulleted_list_item", "numbered_list_item", "to_do", "quote", "heading_1",
             "heading_2", "heading_3", "paragraph", "callout", "toggle", "code"):
        src = b.get(t, {})
        rich = src.get("rich_text", [])
        if not rich:
            return None
        kids = []
        if b.get("has_children"):
            for cb in get_children(b["id"]):
                s = simplify_block(cb, depth + 1)
                if s:
                    kids.append(s)
        new = {"object": "block", "type": t, t: {"rich_text": rich}}
        if kids:
            new[t]["children"] = kids
        return new
    if t in ("divider",):
        return {"object": "block", "type": "divider", "divider": {}}
    if t == "image":
        img = b.get("image", {})
        # file 类型（Notion 内部存储）转 external；prod-files-secure URL 可公开访问
        if img.get("type") == "file":
            url = img.get("file", {}).get("url", "")
            if url:
                img = {"type": "external", "external": {"url": url}}
            else:
                return None
        # data URI 或空 URL 的图片 Notion API 不接受，跳过
        url = (img.get("external") or {}).get("url", "")
        if not url or url.startswith("data:"):
            return None
        return {"object": "block", "type": "image", "image": img}
    if t == "bookmark":
        bm = b.get("bookmark", {})
        return {"object": "block", "type": "bookmark", "bookmark": bm}
    if t == "embed":
        em = b.get("embed", {})
        return {"object": "block", "type": "embed", "embed": em}
    if t == "equation":
        return {"object": "block", "type": "equation", "equation": b.get("equation", {})}
    if t == "table":
        return None  # 表格复制复杂，跳过
    # 其他类型降级为段落
    return None

def copy_page_blocks(src_id):
    """读取源页面所有块，转为可创建列表"""
    out = []
    for b in get_children(src_id):
        s = simplify_block(b)
        if isinstance(s, list):
            out.extend(s)
        elif s:
            out.append(s)
    return out

def create_row(db_id, title, type_val, status_val, blocks, date=None, tags=None, slug=None):
    props = {
        "Name": {"title": [{"type": "text", "text": {"content": title[:1900]}}]},
        "type": {"select": {"name": type_val}},
        "status": {"select": {"name": status_val}},
    }
    if date:
        props["date"] = {"date": {"start": date}}
    if tags:
        props["tags"] = {"multi_select": [{"name": t} for t in tags[:10]]}
    if slug:
        props["slug"] = {"rich_text": [{"type": "text", "text": {"content": slug}}]}
    body = {"parent": {"database_id": db_id}, "properties": props}
    if blocks:
        body["children"] = blocks[:100]
    r = api("https://api.notion.com/v1/pages", "POST", body)
    return r.get("id")

def main():
    step = sys.argv[1] if len(sys.argv) > 1 else "pages"

    if step == "pages":
        # 1. 搬运 Me/Idea/Connect 子页面
        print("=== 读取 LOFT 子页面 ===")
        loft_blocks = get_children(LOFT)
        sub_pages = []
        for b in loft_blocks:
            if b.get("type") == "column_list":
                for col in get_children(b["id"]):
                    if col.get("type") == "column":
                        for gb in get_children(col["id"]):
                            if gb.get("type") == "child_page":
                                raw = gb.get("child_page", {}).get("title", "")
                                if isinstance(raw, list):
                                    t = "".join(x.get("plain_text", "") if isinstance(x, dict) else str(x) for x in raw)
                                else:
                                    t = str(raw)
                                sub_pages.append((t, gb["id"]))
        print(f"找到子页面: {[t for t, _ in sub_pages]}")
        for title, pid in sub_pages:
            blocks = copy_page_blocks(pid)
            print(f"  搬运 '{title}' ({len(blocks)} 块)...")
            row = create_row(NEW_DB, title, "Page", "Published", blocks, slug=title.lower().replace(" ", "-"))
            print(f"    -> {row}")

    elif step == "posts":
        # 2. 搬运 BLOG 52 篇文章
        print("=== 读取 BLOG 文章列表 ===")
        articles, cursor = [], None
        while True:
            body = {"page_size": 100}
            if cursor:
                body["start_cursor"] = cursor
            d = api(f"https://api.notion.com/v1/data_sources/{BLOG_DS}/query", "POST", body)
            articles.extend(d.get("results", []))
            if not d.get("has_more"):
                break
            cursor = d.get("next_cursor")
            time.sleep(0.35)
        # 已存在的行（幂等保护）
        existing = set()
        cur2 = None
        while True:
            body = {"page_size": 100}
            if cur2:
                body["start_cursor"] = cur2
            d = api(f"https://api.notion.com/v1/data_sources/{NEW_COLLECTION}/query", "POST", body)
            for r in d.get("results", []):
                for p in r.get("properties", {}).values():
                    if p.get("type") == "title":
                        existing.add("".join(t.get("plain_text", "") for t in p.get("title", [])))
                        break
            if not d.get("has_more"):
                break
            cur2 = d.get("next_cursor")
            time.sleep(0.35)
        print(f"共 {len(articles)} 篇，已存在 {len(existing)} 条")
        ok, fail = 0, []
        for i, a in enumerate(articles):
            props = a.get("properties", {})
            title = ""
            for p in props.values():
                if p.get("type") == "title":
                    title = "".join(t.get("plain_text", "") for t in p.get("title", []))
                    break
            if title in existing:
                print(f"[{i+1}/{len(articles)}] 跳过(已存在): {title[:30]}")
                ok += 1
                continue
            tags = [t.get("name") for t in props.get("标签", {}).get("multi_select", [])]
            date = props.get("属性", {}).get("date", {})
            start = date.get("start") if date else None
            blocks = copy_page_blocks(a["id"])
            print(f"[{i+1}/{len(articles)}] {title[:36]} ({len(blocks)}块)")
            try:
                row = create_row(NEW_DB, title, "Post", "Published", blocks, date=start, tags=tags)
                ok += 1
            except Exception as e:
                fail.append((title, str(e)[:120]))
                print(f"    !! 失败: {str(e)[:100]}")
            time.sleep(0.4)
        print(f"\n=== 完成: 成功 {ok}, 失败 {len(fail)} ===")
        for t, e in fail[:10]:
            print(f"  FAIL: {t[:40]} -> {e}")

if __name__ == "__main__":
    main()
