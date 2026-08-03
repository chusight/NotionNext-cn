import json
import os
import subprocess
import sys

# Read NOTION_API_KEY from .env at runtime to avoid masking issues
env_path = os.path.expandvars(r"$APPDATA/hermes/.env")
notion_key = None
with open(env_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line.startswith("NOTION_API_KEY="):
            notion_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

if not notion_key:
    print("ERROR: NOTION_API_KEY not found in .env", file=sys.stderr)
    sys.exit(1)

# Read markdown article
md_path = r"C:\Users\Administrator\projects\notionnext-loft\blog_20260801.md"
with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

# Build payload
today = "2026-08-01"
payload = {
    "parent": {"type": "database_id", "database_id": "234a8ab8-5c9b-41a4-b0d9-51afd44f499a"},
    "properties": {
        "Name": {"title": [{"type": "text", "text": {"content": "AI 可穿戴传感器：在症状出现前读懂你的身体"}}]},
        "status": {"select": {"name": "Published"}},
        "type": {"select": {"name": "Post"}},
        "tags": {"multi_select": [{"name": "AI"}, {"name": "可穿戴"}, {"name": "传感器"}, {"name": "医疗器械"}, {"name": "前沿科技"}]},
        "category": {"select": {"name": "医疗器械"}},
        "date": {"date": {"start": today}},
        "summary": {"rich_text": [{"type": "text", "text": {"content": "从 McGill 炎症早检到 Apple Watch 92% 准确率健康模型，AI 可穿戴传感器正从运动记录器进化为随身病理实验室。"}}]},
        "slug": {"rich_text": [{"type": "text", "text": {"content": "ai-wearable-sensors-detect-inflammation-before-symptoms"}}]}
    },
    "markdown": md_content
}

# Write temp JSON
tmp_json = r"C:\Users\Administrator\projects\notionnext-loft\tmp_payload.json"
with open(tmp_json, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False)

# Build curl command
auth_header = "Bearer " + notion_key
curl_cmd = [
    "curl", "-s", "-X", "POST",
    "https://api.notion.com/v1/pages",
    "-H", "Authorization: Bearer " + notion_key,
    "-H", "Notion-Version: 2025-09-03",
    "-H", "Content-Type: application/json",
    "--data-binary", "@" + tmp_json
]

result = subprocess.run(curl_cmd, capture_output=True, text=True)

# Clean up temp file
try:
    os.remove(tmp_json)
except OSError:
    pass

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr, file=sys.stderr)

sys.exit(result.returncode)
