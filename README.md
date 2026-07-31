<div align="center">

# LOFT · ligan.cc

用 Notion 管理内容，NotionNext 构建，Cloudflare Pages 免费托管

> 这是 **ligan.cc** 的生产代码库 —— 基于 [NotionNext](https://github.com/notionnext-org/NotionNext) 深度定制的个人站点。

</div>

## ✨ 站点特点

- 🎨 **Heo 主题深度定制**：英雄区、通知条、侧栏、目录、瀑布流
- 📰 **News 每日新闻页**：自动采集科技新闻，日期倒序 + 摘要 + 跳转详情
- 💡 **Idea 灵感页**：每日自动追加一张高清工业设计产品图（瀑布流展示）
- 🏷 **自动分类**：文章按内容关键词自动归类（AI/芯片/AR-VR/医疗器械等）
- 🖼 **封面体系**：52 篇文章封面各异，失效封面自动修复
- 🚀 **全自动部署**：cron 任务 → Notion 更新 → 自动构建 → Cloudflare Pages 发布

## 🏗 架构

```
Notion 数据库（内容源）→ NotionNext 构建 → Cloudflare Pages 静态托管
```

| 组件 | 说明 |
|---|---|
| 内容管理 | Notion「LOFT」数据库（公开分享，免 token） |
| 网站框架 | NotionNext 4.10.8（Next.js 静态导出） |
| 主题 | Heo（深度定制） |
| 托管 | Cloudflare Pages（免费 CDN + HTTPS） |
| 域名 | ligan.cc（Cloudflare DNS） |

## ⏰ 每日自动化

| 时间 | 任务 | 产出 |
|---|---|---|
| 3:00 | 网关监控 | Hermes 保活 |
| 4:00 | 科技新闻日报 | News 页面更新（子页面详情 + 倒序摘要条目） |
| 4:30 | Idea 每日设计图 | Idea 页面新增一张高清工业设计图 |
| 5:00 | LOFT 每日科技 Blog | 撰写科技文章 → 自动重新构建部署 |

## 🛠 本地开发

```bash
# 安装依赖
yarn install

# 配置环境变量（.env.local）
NOTION_PAGE_ID=你的Notion数据库ID（无横线32位hex）
NEXT_PUBLIC_THEME=heo
NEXT_PUBLIC_TITLE=LOFT
NEXT_PUBLIC_AUTHOR=lee

# 本地开发
yarn dev

# 静态构建（产物在 out/）
yarn export
```

## 🚀 部署到 Cloudflare Pages

```bash
npm i -g wrangler
wrangler pages project create loft --production-branch=main
export CLOUDFLARE_API_TOKEN=你的Token
wrangler pages deploy out --project-name=loft
```

## 📁 目录结构

```
themes/heo/           # Heo 主题定制（导航/英雄区/瀑布流 CSS/单页头部）
components/SEO.js     # 首页标题只保留站点名
blog.config.js        # 全局配置（CUSTOM_MENU=false 修复导航）
daily_design_task.py  # Idea 每日设计图脚本（4:30 cron）
public/logo-nav.png   # 站点 logo（导航栏/侧栏/头像统一引用）
```

## 📄 License

MIT © [NotionNext](https://github.com/notionnext-org/NotionNext)

---

**在线访问**：[https://ligan.cc](https://ligan.cc)
