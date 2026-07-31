import json, os, urllib.request, sys

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

mode = sys.argv[1] if len(sys.argv) > 1 else "idea"

if mode == "idea":
    # Idea 页面结构
    d = api("https://api.notion.com/v1/blocks/3ae379f0-985f-81b7-a080-c2ae31de48f9/children?page_size=50")
    print("Idea 页面块:")
    for b in d.get("results", []):
        t = b.get("type")
        if t == "child_database":
            print(f"  [child_database] id={b['id']} title={json.dumps(b.get('child_database',{}).get('title',''), ensure_ascii=False)[:60]}")
        else:
            print(f"  [{t}]")
    # 查 Design Inspiration 数据库行数
    DS = "3f923550-e100-46e2-8488-a03768b08d30"
    q = api(f"https://api.notion.com/v1/data_sources/{DS}/query", "POST", {"page_size": 5})
    print(f"\nDesign Inspiration 数据库行数(前5): {len(q.get('results', []))}")
    for r in q.get("results", [])[:3]:
        props = r.get("properties", {})
        t = ''.join(x.get("plain_text","") for x in (props.get("Name",{}) or {}).get("title",[]))
        img = (props.get("image",{}) or {}).get("url","")
        print(f"  {t[:30]} | img: {img[:60]}")
elif mode == "connect":
    d = api("https://api.notion.com/v1/blocks/3ae379f0-985f-810e-b790-de500f1d0fb6/children?page_size=50")
    print("Connect 页面块:")
    for b in d.get("results", []):
        t = b.get("type")
        if t in ("paragraph","heading_2","heading_3"):
            txt = ''.join(x.get("plain_text","") for x in b.get(t,{}).get("rich_text",[]))
            print(f"  [{t}] {txt[:50]}")
        else:
            print(f"  [{t}]")
