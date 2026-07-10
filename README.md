# 新闻 HTML 日报 (JeekNews)

用于生成北京时间 HTML 新闻日报的工具。从中文热榜、科技新闻、财经新闻、开发者资讯和黄金金价等多个来源抓取内容，输出一份可直接阅读的自包含 HTML 报告，并可同步生成页面长截图。

支持在 Vercel 上一键部署为 Web 服务。

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Josia-doit/JeekNews)

## 功能概览

- 抓取黄金金价、中文热榜、科技新闻、财经新闻、Hacker News、Solidot 等多源内容。
- 按北京时间生成带时间戳的 HTML 文件，文件名格式为 `YYYYMMDD-HHMMSS.html`。
- 当本机存在 Edge/Chrome 兼容浏览器时，自动生成同名 PNG 长截图。
- 将各数据源渲染为卡片，并在页面顶部提供可点击的数据源快捷入口。
- 在网页右侧提供返回顶部按钮，截图时会自动隐藏该按钮。
- 对每个数据源做独立错误隔离，单个来源失败不会影响整份日报生成。

## Vercel 一键部署

点击上方 **Deploy with Vercel** 按钮即可一键部署到你的 Vercel 账号。

部署后你会获得一个在线服务，通过 Web 界面即可生成新闻日报：

- 首页（`/`）：Web 操作界面，设置参数后点击按钮即可在线生成日报
- API（`/api/generate?limit=20&timeout=15&retries=2`）：直接调用 API 获取日报 HTML

> **注意**：Vercel Serverless 环境不支持浏览器，因此部署版本不包含 PNG 截图功能。如需截图，请在本地运行脚本。

## 本地运行

### 安装为 Codex Skill

将仓库克隆到 Codex skills 目录：

```powershell
git clone https://github.com/guliacer/news-html-digest.git "$env:USERPROFILE\.codex\skills\news-html-digest"
```

安装或更新后重启 Codex，让 Codex 重新发现 `SKILL.md`。

### 直接运行脚本

```powershell
python scripts\generate_news_html.py --output-dir . --limit 20 --timeout 15 --retries 2
```

### 参数

```text
--output-dir PATH          HTML 和 PNG 文件输出目录
--limit 10..20            每个来源最多抓取的条目数，默认 20
--timeout SECONDS         单次请求超时时间，默认 15
--retries COUNT           首次请求失败后的重试次数，默认 2
--paper-node-id ID        澎湃新闻节点 ID，默认 25950
--no-screenshot           跳过 PNG 截图生成
--screenshot-width PX     浏览器截图宽度，默认 1200
--screenshot-height PX    浏览器截图高度，默认 60000
--screenshot-timeout SEC  截图超时时间，默认 60
```

## 数据源

当前生成器会查询：

- 通过金金号报价接口获取黄金金价，并使用东方财富 USD/CNH 汇率进行换算。
- 通过 `60s.viki.moe` 获取 60 秒每日要闻、微博热搜、知乎热榜和抖音热搜。
- 腾讯新闻科技、澎湃新闻、东方财富股票新闻、Bilibili 热搜、Bilibili 热门视频、IT之家、少数派、稀土掘金、百度热搜、今日头条热榜、Hacker News、参考消息、Solidot 和财联社。

失败、为空或被拦截的数据源会从页面中省略，不会显示为损坏卡片。

## 输出

成功运行后，输出目录会得到类似文件：

```text
20260706-081629.html
20260706-081629.png
```

HTML 是主要产物。PNG 是渲染页面的长截图；如果截图失败，HTML 仍会保留，并在命令输出中明确说明截图失败原因。

## 目录结构

```text
vercel.json              # Vercel 部署配置
api/generate.py          # Vercel Serverless Function (API 端点)
public/index.html        # Web 操作界面
scripts/generate_news_html.py  # 核心生成脚本
SKILL.md                 # Codex Skill 定义
agents/openai.yaml       # Skill Agent 配置
```

## 注意事项

- 生成的日报适合快速阅读与浏览，不承诺作为长期归档数据源。
- 远端站点可能调整结构、拦截请求或返回空数据；脚本会按来源隔离错误。
- 截图依赖本机 Edge/Chrome headless 模式。如自动检测不到浏览器，可通过 `NEWS_HTML_BROWSER` 指定浏览器可执行文件路径。
- Vercel 部署版本受 Serverless 环境限制：无截图功能，单个请求超时取决于你的 Vercel 计划（Hobby: 10s, Pro: 60s）。
