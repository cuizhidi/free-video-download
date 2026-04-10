# FreeVidGrab - 免费在线视频下载 & AI 智能分析工具

免费在线视频下载工具，支持 YouTube、Bilibili、抖音、TikTok 等 1000+ 平台，极速解析，高清下载。v2.0 新增 AI 智能分析功能：视频总结、章节大纲、关键知识提取、思维导图、AI 问答。

## 特色功能

### 视频下载（v1.0）

- **1000+ 平台支持**：基于 yt-dlp 引擎，覆盖 YouTube、Bilibili、TikTok、Twitter/X、Instagram 等主流平台
- **抖音原生下载**：专用下载模块，直调公开 API，无需 cookies，自动去水印
- **多格式选择**：展示所有可用分辨率，标注文件大小和音视频信息
- **实时进度推送**：SSE 实时推送下载和合并进度
- **封面图代理**：自动解决跨域图片加载问题

### AI 智能分析（v2.0）

- **视频内容总结**：AI 生成 200-300 字精炼摘要
- **章节大纲**：自动识别视频结构，生成带时间戳的章节列表
- **关键知识提取**：提取 5-10 个核心知识点
- **字幕/转录展示**：带时间戳字幕文本，支持关键词搜索
- **思维导图**：markmap 可视化渲染，支持缩放和拖拽
- **AI 问答**：基于视频内容的多轮对话式问答，流式输出
- **字幕三级回退**：手动字幕 → 自动字幕 → faster-whisper 语音识别
- **多 AI 提供商**：支持 DeepSeek、Ollama 本地模型、硅基流动、OpenRouter 等

## 技术栈

- **前端**: Vue 3 + Vite（SaveAny 亮色简洁风格）
- **后端**: Python FastAPI + Uvicorn
- **下载引擎**: yt-dlp（通用）+ 自研 douyin_downloader（抖音专用）
- **音视频处理**: ffmpeg（合并分离的音视频流）
- **AI 模型**: DeepSeek（默认），支持任何 OpenAI 兼容 API
- **语音识别**: faster-whisper（无字幕视频兜底方案）
- **思维导图**: markmap-view + markmap-lib

## 快速启动

### 前置条件

- Python 3.10+
- Node.js 18+
- ffmpeg（用于合并音视频流）

### 1. 配置 AI（可选）

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入你的 AI API Key
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### 3. 启动前端（开发模式）

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 Vite 输出的地址（默认 `http://localhost:5173`），即可使用。

### 4. 生产部署

```bash
# 构建前端
cd frontend && npm run build

# 启动后端（自动托管前端静态文件）
cd ../backend && uvicorn app:app --host 0.0.0.0 --port 8000
```

## 项目结构

```
├── docs/                           # 项目文档
│   ├── requirements.md             # 需求文档
│   ├── design.md                   # 方案设计文档
│   └── summary.md                  # 项目总结文档
├── backend/
│   ├── app.py                      # FastAPI 主应用
│   ├── downloader.py               # yt-dlp 封装 + 抖音路由分流
│   ├── douyin_downloader.py        # 抖音专用解析下载模块
│   ├── ai_routes.py                # AI 相关 API 路由
│   ├── ai_service.py               # AI 总结/问答服务（多提供商）
│   ├── subtitle_extractor.py       # 字幕提取 + faster-whisper 转录
│   ├── requirements.txt            # Python 依赖
│   ├── .env.example                # 环境变量模板
│   └── downloads/                  # 临时下载目录（自动创建、定时清理）
├── frontend/
│   ├── src/
│   │   ├── App.vue                 # 根组件
│   │   ├── api/
│   │   │   ├── index.js            # 下载相关 API 封装
│   │   │   └── ai.js              # AI API 封装（SSE 流式）
│   │   ├── style.css               # 全局样式
│   │   └── components/
│   │       ├── NavBar.vue          # 顶部导航栏
│   │       ├── HeroSection.vue     # Hero 区
│   │       ├── VideoResult.vue     # 视频解析结果
│   │       ├── DownloadProgress.vue # 下载进度
│   │       ├── AISummaryPanel.vue  # AI 智能分析主面板
│   │       ├── SummaryTab.vue      # 视频摘要
│   │       ├── ChapterTab.vue      # 章节大纲
│   │       ├── KeyPointsTab.vue    # 关键知识点
│   │       ├── TranscriptTab.vue   # 字幕文本
│   │       ├── MindmapTab.vue      # 思维导图
│   │       ├── AIChatTab.vue       # AI 问答
│   │       └── ...
│   ├── vite.config.js              # Vite 配置（开发代理）
│   └── package.json
└── README.md
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/parse?url=` | GET | 解析视频信息（标题、封面、格式列表） |
| `/api/download?url=&format_id=` | GET | 下载视频（SSE 进度推送） |
| `/api/file/{filename}` | GET | 获取已下载文件 |
| `/api/proxy-image?url=` | GET | 代理加载图片 |
| `/api/ai/status` | GET | 检查 AI 服务可用性 |
| `/api/ai/check` | GET | AI API 连通性诊断 |
| `/api/ai/subtitle?url=` | GET | 提取视频字幕/转录文本 |
| `/api/ai/summarize` | POST | AI 视频内容总结（SSE 流式） |
| `/api/ai/chat` | POST | AI 视频问答（SSE 流式） |

## 文档

- [需求文档](docs/requirements.md)
- [方案设计文档](docs/design.md)
- [项目总结](docs/summary.md)

## License

MIT
