import json, os, subprocess, urllib.request

# 从 git 凭据管理器拿 token
p = subprocess.run(['git', 'credential-manager', 'get'], input='protocol=https\nhost=github.com\n\n',
                   capture_output=True, text=True, timeout=20)
token = None
for line in p.stdout.splitlines():
    if line.startswith('password='):
        token = line.split('=', 1)[1]
        break
print(f"token 长度: {len(token) if token else 0}")

desc = "ligan.cc 生产站：NotionNext + Heo 主题深度定制，Cloudflare Pages 托管。News 每日新闻、Idea 每日设计图、自动分类、全自动部署。"
body = json.dumps({"description": desc}).encode()

req = urllib.request.Request(
    "https://api.github.com/repos/chusight/NotionNext-cn",
    method="PATCH",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
             "User-Agent": "hermes-agent"},
    data=body
)
# 走代理
proxy = urllib.request.ProxyHandler({"https": "http://Clash:9xZDY8dL@192.168.2.10:7893"})
opener = urllib.request.build_opener(proxy)
try:
    d = json.load(opener.open(req, timeout=30))
    print("success:", d.get("full_name"))
    print("description:", d.get("description"))
    if d.get("message"):
        print("错误:", d["message"])
except Exception as e:
    print("失败:", e)
    if hasattr(e, 'read'):
        print(e.read().decode()[:200])
