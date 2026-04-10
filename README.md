# FreeVidGrab - 免费在线视频下载工具

免费在线视频下载工具，支持 YouTube、Bilibili、抖音、TikTok 等 1000+ 平台，极速解析，高清下载。

## 特色功能

- **1000+ 平台支持**：基于 yt-dlp 引擎，覆盖 YouTube、Bilibili、TikTok、Twitter/X、Instagram 等主流平台
- **抖音原生下载**：专用下载模块，直调公开 API，无需 cookies，自动去水印
- **多格式选择**：展示所有可用分辨率，标注文件大小和音视频信息
- **实时进度推送**：SSE 实时推送下载和合并进度
- **封面图代理**：自动解决跨域图片加载问题

## 技术栈

- **前端**: Vue 3 + Vite（SaveAny 亮色简洁风格）
- **后端**: Python FastAPI + Uvicorn
- **下载引擎**: yt-dlp（通用）+ 自研 douyin_downloader（抖音专用）
- **音视频处理**: ffmpeg（合并分离的音视频流）
- **HTTP 库**: requests（抖音模块网络请求）

## 快速启动

### 前置条件

- Python 3.10+
- Node.js 18+
- ffmpeg（用于合并音视频流）

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### 2. 启动前端（开发模式）

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 Vite 输出的地址（默认 `http://localhost:5173`），即可使用。

### 3. 生产部署

```bash
# 构建前端
cd frontend && npm run build

# 启动后端（自动托管前端静态文件）
cd ../backend && uvicorn app:app --host 0.0.0.0 --port 8000
```

## 项目结构

```
├── docs/                        # 项目文档
│   ├── requirements.md          # 需求文档
│   ├── design.md                # 方案设计文档
│   └── summary.md               # 项目总结文档
├── backend/
│   ├── app.py                   # FastAPI 主应用（路由、中间件、图片代理）
│   ├── downloader.py            # yt-dlp 封装 + 抖音路由分流
│   ├── douyin_downloader.py     # 抖音专用解析下载模块
│   ├── requirements.txt         # Python 依赖
│   └── downloads/               # 临时下载目录（自动创建、定时清理）
├── frontend/
│   ├── src/
│   │   ├── App.vue              # 根组件
│   │   ├── api/index.js         # API 封装
│   │   ├── style.css            # 全局样式（SaveAny 亮色主题）
│   │   └── components/          # Vue 组件
│   │       ├── NavBar.vue       # 顶部导航栏
│   │       ├── HeroSection.vue  # Hero 区
│   │       ├── VideoResult.vue  # 视频解析结果
│   │       └── ...
│   ├── vite.config.js           # Vite 配置（开发代理）
│   └── package.json
└── README.md
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/parse?url=` | GET | 解析视频信息 |
| `/api/download?url=&format_id=` | GET | 下载视频（SSE 进度推送） |
| `/api/file/{filename}` | GET | 获取已下载文件 |
| `/api/proxy-image?url=` | GET | 代理加载图片 |

## 文档

- [需求文档](docs/requirements.md)
- [方案设计文档](docs/design.md)
- [项目总结](docs/summary.md)

## License

MIT
