"""按文章内容自动生成 category：基于标题+摘要关键词规则分类"""
import json, os, urllib.request, time, re

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

# 分类规则：关键词 → category（按优先级顺序）
RULES = [
    (["GPT", "OpenAI", "Claude", "Anthropic", "LLM", "大模型", "AI智能体", "智能体", "AI模型", "AI创业", "AI 50", "Forbes AI", "AI治理", "人工智能模型", "AI助手"], "AI"),
    (["芯片", "半导体", "Snapdragon", "骁龙", "RTX", "NVIDIA", "TSMC", "算力", "GPU", "晶圆", "1纳米", "亚1纳米", "制程"], "芯片"),
    (["AR", "VR", "MR", "XR", "头显", "智能眼镜", "眼镜", "Vision Pro", "AR眼镜", "VR头显", "空间计算", "近眼显示", "SteamVR", "HoloLens"], "AR/VR"),
    (["医疗器械", "医疗", "视锥细胞", "干细胞", "医生", "诊疗", "健康", "生物医学", "细胞", "手术", "患者", "临床", "FDA", "药械"], "医疗器械"),
    (["传感器", "电子皮肤", "可穿戴", "柔性", "感应", "触觉", "肌电", "脑机", "神经接口"], "传感器"),
    (["机器人", "人形机器人", "Figure", "具身智能", "机械臂", "自动驾驶", "汽车", "宝马"], "机器人"),
    (["图形学", "渲染", "GAN", "3D", "三维", "动作合成", "图像生成", "SIGGRAPH", "动画", "建模", "网格"], "计算机图形学"),
    (["工业设计", "设计", "人体工程学", "HF/E", "人机工程", "产品", "工艺", "美学", "造型"], "工业设计"),
    (["脑", "神经", "大脑", "脉冲神经网络", "认知", "心理学"], "脑科学"),
    (["量子", "量子计算"], "量子计算"),
]

def classify(title, summary):
    text = f"{title} {summary}"
    for cats, category in RULES:
        for kw in cats:
            if kw.lower() in text.lower():
                return category
    return "前沿科技"  # 默认

# 读取分析数据
posts = json.load(open('/tmp/posts_data.json', encoding='utf-8'))

updated = 0
for p in posts:
    if p["type"] != "Post" or p["category"]:
        continue
    cat = classify(p["title"], p["summary"])
    try:
        api(f"https://api.notion.com/v1/pages/{p['id']}", "PATCH", {
            "properties": {"category": {"select": {"name": cat}}}
        })
        updated += 1
        print(f"  ✅ {p['title'][:35]} -> {cat}")
    except Exception as e:
        print(f"  ❌ {p['title'][:35]}: {e}")
    time.sleep(0.3)

print(f"\n更新 {updated} 篇文章的 category")
