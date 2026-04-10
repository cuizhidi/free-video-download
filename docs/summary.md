# 免费视频下载工具 - 项目总结文档

> 版本：v2.0  
> 日期：2026-04-11  
> 状态：已完成（视频下载 + AI 智能分析）

---

## 一、项目概述

**FreeVidGrab** 是一个在线视频下载工具，用户粘贴视频链接即可解析视频信息并下载。产品采用 Freemium（免费增值）模式定位，通过精致的界面设计和良好的使用体验吸引用户付费升级。

### 已完成功能（v1.0 MVP）

| 功能 | 状态 | 说明 |
|------|------|------|
| 视频链接解析 | ✅ | 粘贴 URL → 自动识别平台 → 返回标题、封面、时长、作者 |
| 多格式选择 | ✅ | 展示可用分辨率列表，标注是否含音频、文件大小 |
| 视频下载 | ✅ | 已合一格式直接下载，需合并格式服务端 ffmpeg 处理 |
| 实时下载进度 | ✅ | SSE 推送下载/合并进度，前端实时展示 |
| 多平台支持 | ✅ | YouTube、Bilibili、抖音、TikTok、Twitter/X 等 1000+ 平台 |
| 抖音专用模块 | ✅ | 绕开 yt-dlp 限制，直接调用公开 API，无需 cookies |
| 封面图代理 | ✅ | 后端代理加载封面图片，解决跨域 Referer 限制 |
| 付费引导 UI | ✅ | 免费/会员功能对比展示（v1.0 仅 UI，不含付费逻辑） |
| 响应式布局 | ✅ | 适配桌面端和移动端 |

### 已完成功能（v2.0 AI 智能分析）

| 功能 | 状态 | 说明 |
|------|------|------|
| AI 视频内容总结 | ✅ | DeepSeek AI 生成 200-300 字精炼摘要 |
| 章节大纲 | ✅ | AI 自动识别视频结构，生成带时间戳的章节列表 |
| 关键知识提取 | ✅ | 提取 5-10 个核心知识点，含标题和详细说明 |
| 字幕/转录展示 | ✅ | 带时间戳的字幕文本，支持关键词搜索 |
| 思维导图 | ✅ | markmap 可视化渲染，支持缩放和拖拽 |
| AI 问答 | ✅ | 基于视频内容的多轮对话式问答，流式输出 |
| 字幕三级回退 | ✅ | 手动字幕 → 自动字幕 → faster-whisper 语音识别 |
| 字幕缓存 | ✅ | 内存 LRU 缓存，避免重复提取 |

### 延期到 v3.0 的功能

- 用户注册/登录系统
- 批量下载 / 播放列表
- 音频提取（MP3/M4A）
- 字幕下载（SRT/VTT）
- 下载次数限制与付费系统
- 浏览器插件
- AI 自定义 Prompt
- 总结内容多格式导出（PDF/Word/Markdown）
- 知识库集成（Notion/Obsidian）

---

## 二、系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Vue 3 前端应用（SaveAny 风格）              │   │
│  │  NavBar → HeroSection → VideoResult → DownloadProgress │   │
│  └───────────────────────┬──────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTP / SSE
┌──────────────────────────┼──────────────────────────────────┐
│                     FastAPI 后端                              │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐  ┌────────────┐   │
│  │ 解析 API  │  │ 下载 API  │  │ 文件 API │  │ 图片代理 API│   │
│  └────┬─────┘  └────┬─────┘  └────┬────┘  └─────┬──────┘   │
│       │             │             │              │           │
│  ┌────┴─────────────┴───┐   ┌────┴────┐                    │
│  │    downloader.py      │   │downloads│                    │
│  │  ┌─────────────────┐  │   └─────────┘                    │
│  │  │ 抖音链接？        │  │                                  │
│  │  │  ├─ 是 → douyin_ │  │                                  │
│  │  │  │   downloader  │  │                                  │
│  │  │  └─ 否 → yt-dlp  │  │                                  │
│  │  └─────────────────┘  │                                  │
│  └───────────────────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 (Composition API) + Vite | 轻量响应式，极速 HMR |
| 后端框架 | FastAPI + Uvicorn | Python 异步框架，自带 OpenAPI 文档 |
| 通用下载引擎 | yt-dlp | 14 万+ Star，支持 1000+ 网站 |
| 抖音下载引擎 | 自研 douyin_downloader | 直调公开 API，无需 cookies |
| 音视频处理 | ffmpeg | 合并分离的音视频流 |
| HTTP 库 | requests | 抖音模块网络请求 |
| 前端网络 | Fetch API + EventSource (SSE) | 浏览器原生，无额外依赖 |
| AI 模型 | DeepSeek (deepseek-chat) | 通过 OpenAI 兼容 SDK 调用 |
| 语音识别 | faster-whisper (small, CPU) | 无字幕视频的语音转录兜底方案 |
| 思维导图 | markmap-view + markmap-lib | Markdown → 交互式 SVG 思维导图 |
| Markdown 渲染 | marked | 摘要和问答内容的富文本渲染 |

---

## 三、关键技术决策与原因

### 3.1 为什么选择 yt-dlp 作为核心引擎

- GitHub 14 万+ Star，社区活跃，持续维护
- 原生支持 1000+ 视频网站，无需逐个适配
- Python 库形式调用，与 FastAPI 后端天然集成
- 支持格式选择、进度回调、ffmpeg 合并等高级功能

### 3.2 为什么抖音需要专用下载模块

**问题**：yt-dlp 对抖音要求 "Fresh cookies (not necessarily logged in)"，即使不需要登录也必须提供浏览器 cookies。这对线上服务不可行。

**方案**：创建 `douyin_downloader.py` 专用模块，完全绕开 yt-dlp：

1. **公开 API**：调用 `iesdouyin.com/web/api/v2/aweme/iteminfo/` 获取视频元数据，无需 cookies
2. **分享页兜底**：API 不可用时，解析分享页 HTML 中的 `window._ROUTER_DATA` 提取数据
3. **WAF 反爬破解**：自动解决抖音的 sha256 挑战验证
4. **去水印**：将视频 URL 中的 `playwm` 替换为 `play` 获取无水印版本
5. **URL 路由**：`downloader.py` 中通过 `is_douyin_url()` 自动分流，其他平台继续走 yt-dlp

**参考**：rathodpratham-dev/douyin_video_downloader（MIT License, 2026）

### 3.3 为什么用 SSE 而非 WebSocket 推送下载进度

- SSE 基于标准 HTTP，无需额外协议升级
- 单向推送（服务端 → 客户端）完全满足进度推送场景
- FastAPI 原生支持 `StreamingResponse`，无需额外依赖
- 浏览器原生 `EventSource` API，前端零依赖
- 自动重连机制，比 WebSocket 更稳定

### 3.4 为什么需要图片代理接口

部分平台（如 Bilibili）的视频封面图有 Referer 校验，浏览器直接加载 `<img>` 会被拒绝。后端 `/api/proxy-image` 接口代为请求并设置正确的 Referer 头，解决跨域封面加载问题。

### 3.5 UI 设计演变

项目 UI 经历了一次完整改版：

- **初版**：暗色科技风（Dark Tech），毛玻璃卡片，紫青渐变，参考 ai.codefather.cn
- **改版**：SaveAny 亮色简洁风，白色背景，蓝色主调，清爽卡片，更贴近主流下载工具的专业感

改版原因：亮色风格更适合工具类产品，降低用户认知负担，提升信任感。

---

## 四、API 接口一览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/parse?url=` | GET | 解析视频信息（标题、封面、格式列表） |
| `/api/download?url=&format_id=` | GET | 下载视频，SSE 推送进度 |
| `/api/file/{filename}` | GET | 获取已下载的文件 |
| `/api/proxy-image?url=` | GET | 代理加载图片，绕过 Referer 限制 |
| `/api/ai/status` | GET | 检查 AI 服务可用性（API Key 是否配置） |
| `/api/ai/check` | GET | AI API 连通性诊断（配置 + 实际调用测试） |
| `/api/ai/subtitle?url=` | GET | 提取视频字幕/转录文本 |
| `/api/ai/summarize` | POST | AI 视频内容总结（SSE 流式） |
| `/api/ai/chat` | POST | AI 视频问答（SSE 流式） |

### 错误码体系

| 错误码 | 含义 | 触发场景 |
|--------|------|----------|
| UNSUPPORTED | 平台不支持 | URL 不被 yt-dlp 识别 |
| NOT_FOUND | 视频不存在 | 视频已删除或不可用 |
| AUTH_REQUIRED | 需要登录 | 视频需要账号权限 |
| COOKIES_NEEDED | 需要 cookies | 平台要求浏览器 cookies |
| GEO_BLOCKED | 地区限制 | 视频在当前地区不可用 |
| PARSE_FAILED | 解析失败 | 其他解析错误 |

---

## 五、前端组件架构

```
App.vue
├── NavBar.vue                # 顶部导航：品牌、锚点链接、VIP 按钮
├── HeroSection.vue           # Hero 区：绿色徽章 + 大标题 + URL 输入 + 快捷链接
├── VideoResult.vue           # 解析结果：封面 + 元信息 + 2列格式选择 + 下载按钮
├── DownloadProgress.vue      # 下载进度条 + 速度/ETA + 完成链接
├── AISummaryPanel.vue        # [v2.0 新增] AI 智能分析主面板
│   ├── SummaryTab.vue        #   视频摘要（Markdown 渲染）
│   ├── ChapterTab.vue        #   章节大纲（带时间戳卡片列表）
│   ├── KeyPointsTab.vue      #   关键知识点（2列卡片网格）
│   ├── TranscriptTab.vue     #   字幕文本（带时间戳 + 搜索）
│   ├── MindmapTab.vue        #   思维导图（markmap SVG 渲染）
│   └── AIChatTab.vue         #   AI 问答（对话式 UI + 流式显示）
├── PlatformBar.vue           # 支持平台标签栏
├── FeatureCards.vue          # 功能亮点卡片
├── PricingSection.vue        # 免费/会员对比
└── Footer（内联）             # 版权 + 免责声明
```

---

## 六、已知限制与注意事项

| 限制 | 说明 | 应对方案 |
|------|------|----------|
| 海外访问抖音 | 部分视频 `is_oversea=1` 但仍可通过分享页获取 | 分享页兜底方案已实现 |
| 抖音短链接过期 | `v.douyin.com` 短链接有有效期 | 长链接直接提取 ID，短链接失败时友好提示 |
| Bilibili 高清 | 1080P+ 需要登录 cookies | v1.0 暂不支持，v2.0 可加 cookies 配置 |
| Twitter/X | 可能需要 Bearer Token | yt-dlp 内置处理，大部分公开视频可用 |
| 临时文件占用 | 下载文件占用服务器磁盘 | 30 分钟自动清理，后台每 10 分钟扫描 |
| 下载速度 | 受限于服务器带宽和源站限速 | v2.0 可引入高速通道 |

---

## 七、测试记录

### 平台测试结果（2026-04-10）

| 平台 | 测试链接格式 | 解析 | 下载 | 备注 |
|------|-------------|------|------|------|
| YouTube | youtube.com/watch?v= | ✅ | ✅ | 多格式，需合并时走 ffmpeg |
| Bilibili | bilibili.com/video/BV | ✅ | ✅ | 海外访问部分视频受地区限制 |
| 抖音（长链接） | www.douyin.com/video/ | ✅ | ✅ | 专用模块，无水印 |
| 抖音（移动分享） | m.douyin.com/share/video/ | ✅ | ✅ | 专用模块 |
| 抖音（短链接） | v.douyin.com/ | ⚠️ | - | 短链接过期会提示 |

---

## 八、项目目录结构

```
free-video-download/
├── docs/
│   ├── requirements.md          # 需求文档
│   ├── design.md                # 方案设计文档
│   └── summary.md               # 项目总结文档（本文件）
├── backend/
│   ├── app.py                   # FastAPI 主应用（路由、中间件、静态文件）
│   ├── downloader.py            # yt-dlp 封装 + 抖音路由分流
│   ├── douyin_downloader.py     # 抖音专用解析下载模块
│   ├── ai_routes.py             # [v2.0] AI 相关 API 路由（APIRouter）
│   ├── ai_service.py            # [v2.0] DeepSeek AI 总结/问答服务
│   ├── subtitle_extractor.py    # [v2.0] 字幕提取 + faster-whisper 转录
│   ├── requirements.txt         # Python 依赖
│   └── downloads/               # 临时下载目录（自动创建、定时清理）
├── frontend/
│   ├── index.html               # HTML 入口
│   ├── package.json             # Node.js 依赖
│   ├── vite.config.js           # Vite 配置（开发代理）
│   └── src/
│       ├── App.vue              # 根组件
│       ├── main.js              # Vue 入口
│       ├── style.css            # 全局样式（SaveAny 亮色主题）
│       ├── api/
│       │   ├── index.js         # 后端 API 请求封装（下载相关）
│       │   └── ai.js            # [v2.0] AI API 请求封装
│       └── components/
│           ├── NavBar.vue       # 顶部导航栏
│           ├── HeroSection.vue  # Hero 区
│           ├── VideoResult.vue  # 视频解析结果
│           ├── DownloadProgress.vue  # 下载进度
│           ├── AISummaryPanel.vue    # [v2.0] AI 智能分析主面板
│           ├── SummaryTab.vue        # [v2.0] 视频摘要
│           ├── ChapterTab.vue        # [v2.0] 章节大纲
│           ├── KeyPointsTab.vue      # [v2.0] 关键知识点
│           ├── TranscriptTab.vue     # [v2.0] 字幕文本
│           ├── MindmapTab.vue        # [v2.0] 思维导图
│           ├── AIChatTab.vue         # [v2.0] AI 问答
│           ├── PlatformBar.vue  # 支持平台展示
│           ├── FeatureCards.vue # 功能亮点
│           └── PricingSection.vue  # 付费引导
└── README.md                    # 项目说明 + 快速启动
```

---

## 九、v2.0 AI 功能技术决策

### 9.1 为什么选择 DeepSeek 作为 AI 模型

- 完全兼容 OpenAI API 协议，使用 openai Python SDK 即可调用
- 性价比高，按需计费，支持流式输出
- 中文理解和生成能力优秀，适合中文视频内容分析
- 无硬性速率限制，适合个人/小团队产品

### 9.2 为什么用 faster-whisper 而非 openai-whisper

- 推理速度是原版 Whisper 的 4 倍
- 内存占用更低，small 模型 CPU 运行约 500MB
- 不需要系统安装 FFmpeg（通过 PyAV 内置解码）
- 支持 VAD 过滤静音片段，减少无效转录

### 9.3 为什么用 markmap 渲染思维导图

- 轻量级，Markdown 输入即可渲染
- 交互式 SVG，支持缩放、拖拽、折叠
- 与 AI 输出的 Markdown 层级列表天然兼容
- 无需后端参与，纯前端渲染

### 9.4 AI 模块的开闭原则设计

- 新增 `ai_routes.py` 作为独立 APIRouter，通过 `app.include_router()` 注册
- 不修改 `app.py` 中已有的路由和逻辑
- 前端新增独立的 `api/ai.js`，不修改已有的 `api/index.js`
- `AISummaryPanel.vue` 作为独立组件插入 App.vue，不修改已有组件
- AI 功能依赖环境变量 `AI_API_KEY`，未配置时 AI 功能优雅降级（按钮置灰），不影响下载功能

### 9.5 多 AI 提供商支持

v2.0 的 AI 后端被重构为**通用 OpenAI 兼容层**，通过环境变量即可切换不同提供商：

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `AI_BASE_URL` | API 基础地址 | `https://api.deepseek.com` |
| `AI_API_KEY` | API 密钥（必填） | — |
| `AI_MODEL` | 模型名称 | `deepseek-chat` |
| `AI_MAX_TOKENS` | 最大输出 token 数 | `4096` |

已验证支持的提供商：

| 提供商 | BASE_URL | 模型示例 | 说明 |
|--------|----------|----------|------|
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` | 推荐，中文最佳 |
| Ollama 本地 | `http://localhost:11434/v1` | `gpt-oss:20b` | 离线可用，需增大 `AI_MAX_TOKENS` |
| 硅基流动 | `https://api.siliconflow.cn/v1` | `deepseek-ai/DeepSeek-V3` | 国内备选 |
| OpenRouter | `https://openrouter.ai/api/v1` | `meta-llama/llama-3.3-70b-instruct:free` | 有免费模型可用 |

### 9.6 推理模型（Reasoning Model）兼容

使用 Ollama 的推理模型（如 `gpt-oss:20b`）时，模型会将大量 token 用于内部推理（`delta.reasoning`），实际输出内容（`delta.content`）可能很少。解决方案：

- `AI_MAX_TOKENS` 设为 `16384` 或更高，为推理 + 内容留足空间
- 前端 `extractJSON` 解析器支持跳过 `<think>` 块和 Markdown 代码围栏
- 若内容为空，前端会显示诊断提示而非静默失败

### 9.7 `/api/ai/check` 连通性诊断

新增 `GET /api/ai/check` 端点，返回 AI API 的配置信息和实际连通性测试结果，方便快速排查网络/密钥/余额等问题。
