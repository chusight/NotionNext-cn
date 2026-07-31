"""在 Notion 创建教程文章：如何用 NotionNext + Cloudflare Pages 搭建自己的静态博客站"""
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

def h3(text):
    return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def para(text):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def bullet(text):
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def numbered(text):
    return {"object": "block", "type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

def code(text, lang="bash"):
    return {"object": "block", "type": "code", "code": {"rich_text": [{"type": "text", "text": {"content": text}}], "language": lang}}

def callout(text, emoji="💡"):
    return {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": text}}], "icon": {"type": "emoji", "emoji": emoji}}}

children = [
    callout("本教程完整记录了 ligan.cc 的搭建过程：从 Notion 数据源 → NotionNext 项目 → 静态构建 → Cloudflare Pages 部署 → 绑定自定义域名。跟着做，你也能拥有自己的博客站。", "🚀"),
    divider(),
    h2("一、整体架构"),
    para("这个方案的核心思路：用 Notion 作为内容管理系统（CMS），用 NotionNext 把 Notion 内容渲染成网站，再用 Cloudflare Pages 免费托管静态文件。"),
    bullet("内容管理：Notion 数据库（免费，可随时编辑）"),
    bullet("网站框架：NotionNext（开源，支持 20+ 主题）"),
    bullet("静态构建：yarn export（Next.js 静态导出）"),
    bullet("托管部署：Cloudflare Pages（免费 CDN + HTTPS）"),
    bullet("域名绑定：Cloudflare DNS 托管 + 自定义域名"),
    divider(),
    h2("二、准备 Notion 数据源"),
    h3("2.1 创建博客数据库"),
    para("NotionNext 要求数据源是一个「数据库」（Database），不是普通页面。创建一个包含以下属性的数据库："),
    bullet("Name（标题，必选）— 文章标题"),
    bullet("status（状态）— Published 表示发布"),
    bullet("type（类型）— Post=文章，Page=单页（如关于页）"),
    bullet("category（分类）— 如 前沿科技 / AI / 工业设计"),
    bullet("tags（标签）— 多选标签"),
    bullet("date（日期）— 文章发布日期"),
    bullet("summary（摘要）— 列表页显示的简介"),
    bullet("slug（别名）— 英文短横线格式的 URL 别名"),
    h3("2.2 设置数据库为公开"),
    para("在 Notion 页面右上角点击「Share / 分享」→「Publish / 发布到网页」，让数据库可被公开访问（NotionNext 免 token 模式需要）。"),
    callout("关键经验：NOTION_PAGE_ID 必须填数据库的 ID，且要写成无横线的 32 位十六进制格式（如 234a8ab85c9b41a4b0d951afd44f499a），否则会构建失败。", "⚠️"),
    divider(),
    h2("三、部署 NotionNext 项目"),
    h3("3.1 克隆项目"),
    code("git clone https://github.com/notionnext-org/NotionNext.git\ncd NotionNext\nyarn install"),
    h3("3.2 配置环境变量"),
    para("创建 .env.local 文件，写入："),
    code("NOTION_PAGE_ID=你的数据库ID（无横线格式）\nNEXT_PUBLIC_THEME=heo\nNEXT_PUBLIC_TITLE=你的站点名\nNEXT_PUBLIC_AUTHOR=你的昵称\nNEXT_PUBLIC_LINK=https://你的域名\nNEXT_PUBLIC_LANG=zh-CN", "bash"),
    h3("3.3 静态构建"),
    code("yarn export"),
    para("构建完成后会生成 out/ 目录，这就是纯静态网站文件。"),
    callout("注意：构建前先停掉占用 out 目录的本地服务器（如 python -m http.server），否则会报 EBUSY 错误。", "🔧"),
    divider(),
    h2("四、部署到 Cloudflare Pages"),
    h3("4.1 安装 wrangler CLI"),
    code("npm i -g wrangler"),
    h3("4.2 上传静态文件"),
    code("wrangler pages project create 你的项目名 --production-branch=main\nexport CLOUDFLARE_API_TOKEN=你的Token\nwrangler pages deploy out --project-name=你的项目名"),
    para("部署完成后会得到一个 *.pages.dev 的免费域名，可以直接访问。"),
    divider(),
    h2("五、绑定自定义域名"),
    h3("5.1 在 Cloudflare 添加站点"),
    para("登录 dash.cloudflare.com → Add site → 输入你的域名 → 选择 Free 计划。Cloudflare 会分配两个 NS 地址。"),
    h3("5.2 修改域名 NS"),
    para("到你购买域名的服务商（如 DNSPod/腾讯云）控制台，把域名的 NS 修改为 Cloudflare 分配的地址。等待生效（注册局 RDAP 可查）。"),
    h3("5.3 添加 DNS 记录"),
    para("在 Cloudflare DNS 页面添加："),
    code("CNAME  你的域名   →  你的项目.pages.dev  （代理开启）\nCNAME  www        →  你的项目.pages.dev  （代理开启）"),
    h3("5.4 绑定 Pages 域名"),
    code("wrangler pages project 里添加自定义域名，或控制台 Pages → Custom domains → 添加。"),
    para("Cloudflare 会自动签发 SSL 证书（Google CA），几分钟后 HTTPS 生效。"),
    divider(),
    h2("六、日常更新流程"),
    para("因为是静态站点，每次修改 Notion 内容后需要重新构建部署："),
    code("cd NotionNext\nyarn export\nwrangler pages deploy out --project-name=你的项目名"),
    callout("自动化建议：可以用定时任务（cron）每天自动构建部署。本项目就配置了「每日科技博客」任务：自动搜索新闻 → 写文章 → 写入 Notion → 自动构建部署。", "🤖"),
    divider(),
    h2("七、常见问题"),
    h3("Q1: 页面空白 / 无法获取 Notion 数据？"),
    para("检查 NOTION_PAGE_ID 是否为数据库 ID（不是页面 ID），且为无横线格式；确认数据库已公开分享。"),
    h3("Q2: 导航栏消失？"),
    para("检查 blog.config.js 中 CUSTOM_MENU 是否为 false。若为 true 且 Notion 中没有 Menu 类型页面，导航会被空菜单覆盖。"),
    h3("Q3: 文章封面一样？"),
    para("在 Notion 中给每篇文章设置 page cover（封面图），构建后列表页会自动显示。"),
    h3("Q4: 图片不显示？"),
    para("外部 URL 图片建议用 Notion 能访问的图源（如 Unsplash），或直接把图片粘贴进 Notion 页面。"),
    divider(),
    h2("八、资源链接"),
    bullet("NotionNext 项目：github.com/notionnext-org/NotionNext"),
    bullet("主题预览：preview.tangly1024.com/?theme=heo"),
    bullet("Cloudflare：dash.cloudflare.com"),
    bullet("示例站点：ligan.cc（本文作者站点）"),
    callout("如果你按这个教程搭好了自己的站，欢迎来 ligan.cc 留言交流！", "🙌"),
]

# 在 LOFT 数据库创建文章
body = {
    "parent": {"database_id": LOFT_DB},
    "properties": {
        "Name": {"title": [{"type": "text", "text": {"content": "手把手教你用 NotionNext + Cloudflare Pages 搭建免费静态博客站"}}]},
        "status": {"select": {"name": "Published"}},
        "type": {"select": {"name": "Post"}},
        "category": {"select": {"name": "前沿科技"}},
        "tags": {"multi_select": [{"name": "教程"}, {"name": "NotionNext"}, {"name": "Cloudflare"}]},
        "date": {"date": {"start": "2026-08-01"}},
        "summary": {"rich_text": [{"type": "text", "text": {"content": "从 Notion 数据源到 Cloudflare Pages 静态部署的完整教程：数据库配置、NotionNext 部署、域名绑定、自动化更新，一次讲清楚。"}}]},
        "slug": {"rich_text": [{"type": "text", "text": {"content": "notionnext-cloudflare-pages-tutorial"}}]}
    },
    "children": children
}
d = api("https://api.notion.com/v1/pages", "POST", body)
print("✅ 教程文章已创建!")
print("   ID:", d.get("id"))
print("   URL:", d.get("url"))
