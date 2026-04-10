# 免费视频下载工具 - 方案设计文档

> 版本：v2.0  
> 创建日期：2026-04-10  
> 最后更新：2026-04-11  
> 状态：已完成（视频下载 + AI 智能分析）

---

## 一、系统架构

### 1.1 整体架构

采用**前后端分离**架构，前端 Vue 3 + Vite 负责界面交互，后端 FastAPI 负责业务逻辑和视频下载。生产环境下由 FastAPI 统一托管前端静态资源，单端口部署。

```
┌──────────────────────────────────────────────────────────────┐
│                        用户浏览器                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │           Vue 3 前端应用（SaveAny 亮色风格）               │  │
│  │  NavBar → HeroSection → VideoResult → DownloadProgress  │  │
│  └──────────────────────┬─────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │ HTTP / SSE
┌─────────────────────────┼────────────────────────────────────┐
│                     FastAPI 后端                               │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌────────────────┐   │
│  │ 解析 API  │ │ 下载 API  │ │ 文件 API │ │ 图片代理 API    │   │
│  └────┬─────┘ └────┬─────┘ └────┬────┘ └───────┬────────┘   │
│       │            │            │               │            │
│  ┌────┴────────────┴────┐  ┌────┴────┐                      │
│  │   downloader.py       │  │downloads│                      │
│  │  ┌────────────────┐   │  └─────────┘                      │
│  │  │ 抖音链接？       │   │                                   │
│  │  │ ├ 是 → douyin_  │   │                                   │
│  │  │ │  downloader   │   │                                   │
│  │  │ └ 否 → yt-dlp   │   │                                   │
│  │  │      + ffmpeg    │   │                                   │
│  │  └────────────────┘   │                                   │
│  └───────────────────────┘                                   │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈

| 层级 | 技术 | 版本要求 | 选型理由 |
|------|------|----------|----------|
| 前端框架 | Vue 3 (Composition API) | 3.4+ | 轻量、响应式、生态成熟 |
| 前端构建 | Vite | 5+ | 极速 HMR、开箱即用 |
| 后端框架 | FastAPI | 0.110+ | Python 异步框架、自带 OpenAPI 文档、性能优秀 |
| ASGI 服务器 | Uvicorn | 0.29+ | FastAPI 官方推荐 |
| 通用下载引擎 | yt-dlp | 最新版 | 14 万+ Star、支持 1000+ 网站、活跃维护 |
| 抖音下载引擎 | 自研 douyin_downloader | - | 直调公开 API，无需 cookies，绕开 yt-dlp 限制 |
| HTTP 库 | requests | 2.31+ | 抖音模块网络请求 |
| 音视频处理 | ffmpeg | 6+ | yt-dlp 依赖、用于合并音视频流 |
| 前端网络 | Fetch API + EventSource (SSE) | 浏览器原生 | 无需额外依赖 |

### 1.3 项目目录结构

```
free-video-download/
├── docs/                       # 项目文档
│   ├── requirements.md         # 需求文档
│   ├── design.md               # 方案设计文档（本文件）
│   └── summary.md              # 项目总结文档
├── backend/
│   ├── app.py                  # FastAPI 主应用（路由、中间件、图片代理、静态文件托管）
│   ├── downloader.py           # yt-dlp 封装 + 抖音路由分流
│   ├── douyin_downloader.py    # 抖音专用解析下载模块（公开 API + 分享页兜底 + WAF 破解）
│   ├── requirements.txt        # Python 依赖清单
│   └── downloads/              # 临时下载文件目录（自动创建、定时清理）
├── frontend/
│   ├── index.html              # HTML 入口
│   ├── package.json            # Node.js 依赖
│   ├── vite.config.js          # Vite 配置（开发代理）
│   └── src/
│       ├── App.vue             # 根组件（组合各区块）
│       ├── main.js             # Vue 入口
│       ├── style.css           # 全局样式（SaveAny 亮色主题）
│       ├── api/
│       │   └── index.js        # 后端 API 请求封装（解析、下载、SSE）
│       └── components/
│           ├── NavBar.vue            # 顶部导航栏（品牌 + 锚点 + VIP）
│           ├── HeroSection.vue       # Hero 区：徽章 + 标题 + URL 输入 + 快捷链接
│           ├── PlatformBar.vue       # 支持平台标签栏
│           ├── FeatureCards.vue      # 功能亮点卡片
│           ├── VideoResult.vue       # 视频解析结果 + 2列格式选择
│           ├── DownloadProgress.vue  # 下载进度条 + 状态
│           └── PricingSection.vue    # 付费引导对比区
└── README.md                   # 项目说明 + 快速启动指南
```

---

## 二、后端设计

### 2.1 API 接口设计

#### 2.1.1 解析视频信息

```
GET /api/parse?url={video_url}
```

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 视频页面 URL |

**成功响应（200）：**

```json
{
  "success": true,
  "data": {
    "title": "视频标题",
    "thumbnail": "https://example.com/thumb.jpg",
    "duration": 360,
    "uploader": "上传者名称",
    "description": "视频简介（截断至 200 字符）",
    "view_count": 123456,
    "platform": {
      "name": "YouTube",
      "icon": "youtube",
      "color": "#FF0000"
    },
    "formats": [
      {
        "format_id": "137+140",
        "quality": "1080p",
        "ext": "mp4",
        "filesize": 52428800,
        "has_video": true,
        "has_audio": true,
        "is_merged": false,
        "note": "需合并音视频"
      },
      {
        "format_id": "18",
        "quality": "360p",
        "ext": "mp4",
        "filesize": 15728640,
        "has_video": true,
        "has_audio": true,
        "is_merged": true,
        "note": "已合一，可快速下载"
      }
    ]
  }
}
```

**错误响应（400/500）：**

```json
{
  "success": false,
  "error": "无法解析该链接，请检查 URL 是否正确",
  "error_code": "PARSE_FAILED"
}
```

#### 2.1.2 下载视频（SSE 流）

```
GET /api/download?url={video_url}&format_id={format_id}
```

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 视频页面 URL |
| format_id | string | 是 | 选择的格式 ID |

**SSE 事件流：**

```
event: progress
data: {"status": "downloading", "percent": 45.2, "speed": "2.5MB/s", "eta": "15s"}

event: progress
data: {"status": "merging", "percent": 80.0}

event: complete
data: {"status": "done", "filename": "abc123.mp4", "filesize": 52428800}

event: error
data: {"status": "error", "message": "下载失败：网络超时"}
```

#### 2.1.3 获取下载文件

```
GET /api/file/{filename}
```

**说明：** 返回文件流，前端通过 `Content-Disposition` 触发浏览器下载保存对话框。

#### 2.1.4 代理图片

```
GET /api/proxy-image?url={image_url}
```

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 原始图片 URL |

**说明：** 后端代为请求图片并设置正确的 Referer 头，解决部分平台（如 Bilibili）封面图的跨域加载问题。响应缓存 1 小时。

### 2.2 下载模块设计（downloader.py）

#### 2.2.1 核心类设计

```python
class VideoDownloader:
    """视频解析下载统一入口，自动路由到对应引擎"""

    def parse_video(self, url: str) -> dict:
        """
        解析视频信息，不下载文件。
        - 抖音链接 → douyin_downloader.parse_video()（公开 API，无需 cookies）
        - 其他平台 → yt_dlp.extract_info(url, download=False)
        返回标准化后的视频信息
        """

    def download_video(self, url: str, format_id: str,
                       progress_hook) -> str:
        """
        下载视频文件。
        - 抖音链接 → douyin_downloader.download_video()（直接流式下载无水印视频）
        - 其他平台 → yt-dlp 下载 + ffmpeg 合并（如需）
        - 通过 progress_hook 回调推送进度
        返回下载完成的文件名
        """

    def _normalize_video_info(self, raw_info: dict) -> dict:
        """
        将 yt-dlp 各平台的原始数据统一为标准格式。
        - 提取：title, thumbnail, duration, uploader, description, view_count
        - 识别平台：通过 extractor_key 匹配 PLATFORM_MAP
        - 标准化格式列表：过滤、分类、排序
        """
```

#### 2.2.2 抖音专用模块（douyin_downloader.py）

独立于 yt-dlp 的抖音解析下载模块，解决 yt-dlp 对抖音要求 cookies 的问题。

**核心流程：**

```
输入 URL
  │
  ├── 长链接 (douyin.com/video/{id})
  │     └── 直接从 URL 提取 video_id
  │
  └── 短链接 (v.douyin.com/xxx)
        └── 302 重定向 → 提取 video_id
  │
  ▼
获取视频元数据（两级策略）
  │
  ├── 1. 公开 API: iesdouyin.com/web/api/v2/aweme/iteminfo/
  │     └── 传入 item_ids → 返回 JSON 元数据
  │
  └── 2. 兜底：解析分享页 HTML
        ├── 请求 iesdouyin.com/share/video/{id}/
        ├── 遇到 WAF 挑战 → 解 sha256 → 设置 cookie → 重试
        └── 提取 window._ROUTER_DATA → videoInfoRes.item_list
  │
  ▼
标准化输出（与 yt-dlp 格式一致）
  ├── 去水印：playwm → play
  └── format_id = 直接视频 URL（非 yt-dlp 格式 ID）
```

#### 2.2.2 平台识别映射表

```python
PLATFORM_MAP = {
    "youtube":    {"name": "YouTube",    "icon": "youtube",    "color": "#FF0000"},
    "bilibili":   {"name": "Bilibili",   "icon": "bilibili",   "color": "#00A1D6"},
    "tiktok":     {"name": "TikTok",     "icon": "tiktok",     "color": "#000000"},
    "douyin":     {"name": "抖音",        "icon": "douyin",     "color": "#000000"},
    "twitter":    {"name": "X/Twitter",  "icon": "twitter",    "color": "#1DA1F2"},
    "instagram":  {"name": "Instagram",  "icon": "instagram",  "color": "#E4405F"},
    "xiaohongshu":{"name": "小红书",      "icon": "xiaohongshu","color": "#FF2442"},
    "weibo":      {"name": "微博",        "icon": "weibo",      "color": "#E6162D"},
    "vimeo":      {"name": "Vimeo",      "icon": "vimeo",      "color": "#1AB7EA"},
}
```

#### 2.2.3 下载模式策略

采用**混合策略**，根据格式特征自动选择最优下载方式：

```
用户选择格式
    │
    ├── 格式已合一（is_merged=true）
    │       │
    │       ├── 尝试提取 CDN 直链
    │       │       │
    │       │       ├── 成功 → 返回直链，前端 <a download> 直接下载
    │       │       │
    │       │       └── 失败 → 回退服务端下载，流式返回文件
    │       │
    │
    └── 格式需合并（is_merged=false）
            │
            └── 服务端下载
                    │
                    ├── 下载视频流 → SSE 推送进度
                    ├── 下载音频流 → SSE 推送进度
                    ├── ffmpeg 合并 → SSE 推送状态
                    └── 合并完成 → 返回文件下载链接
```

### 2.3 临时文件管理

- 下载文件存放于 `backend/downloads/` 目录
- 文件名使用 UUID + 原始扩展名，避免冲突：`{uuid}.{ext}`
- 启动时注册后台定时任务，每 10 分钟扫描清理超过 30 分钟的文件
- 配置最大存储空间阈值（默认 5GB），超过时优先清理最旧文件

### 2.4 错误处理策略

| 错误场景 | 错误码 | 用户提示 |
|----------|--------|----------|
| URL 格式不合法 | INVALID_URL | 请输入有效的视频链接 |
| 平台不支持 | UNSUPPORTED | 暂不支持该平台 |
| 视频不存在/已删除 | NOT_FOUND | 视频不存在或已被删除 |
| 需要登录/权限 | AUTH_REQUIRED | 该视频需要登录才能访问 |
| 需要 Cookies | COOKIES_NEEDED | 该平台需要浏览器 cookies 才能访问 |
| 地区限制 | GEO_BLOCKED | 该视频在当前地区不可用 |
| 解析失败 | PARSE_FAILED | 解析失败，请检查链接是否正确 |
| 下载超时 | TIMEOUT | 下载超时，请稍后重试 |
| 服务器内部错误 | INTERNAL_ERROR | 服务繁忙，请稍后重试 |

---

## 三、前端设计

### 3.1 组件架构

```
App.vue
├── NavBar.vue                # 顶部导航栏
│   ├── 品牌 Logo + 名称 + "万能视频下载" 标签
│   ├── 锚点导航链接
│   └── "开通 VIP" 按钮
├── HeroSection.vue           # Hero 区
│   ├── 绿色 "支持 1000+ 平台" 徽章
│   ├── 大标题 "万能视频下载器，一键保存"
│   ├── 白底 URL 输入框 + 蓝色解析按钮
│   └── 快捷平台链接（YouTube / Bilibili / Twitter）
├── VideoResult.vue           # 解析结果（条件渲染）
│   ├── 视频封面（代理加载）+ 时长 + 平台徽章
│   ├── 标题、作者、播放量、简介
│   ├── 2 列格式选择网格（蓝色高亮选中项）
│   └── 下载按钮
├── DownloadProgress.vue      # 下载进度（条件渲染）
│   ├── 蓝色进度条
│   ├── 速度 / ETA / 状态
│   └── 完成后文件链接 / 重试按钮
├── PlatformBar.vue           # 支持平台标签栏
│   └── Emoji + 平台名称 chips
├── FeatureCards.vue          # 功能亮点
│   └── 白色卡片 × 4（带阴影和 hover 效果）
├── PricingSection.vue        # 付费引导
│   ├── 免费栏
│   └── 会员栏（蓝色边框高亮）
└── Footer（内联）             # 版权 + 免责声明
```

### 3.2 状态管理

v1.0 不引入 Pinia/Vuex，使用 Vue 3 Composition API 的 `reactive`/`ref` 在 App.vue 中集中管理状态，通过 props 和 events 传递：

```javascript
// App.vue 中的核心状态
const state = reactive({
  url: '',                    // 用户输入的 URL
  loading: false,             // 是否正在解析
  videoInfo: null,            // 解析结果
  selectedFormat: null,       // 用户选择的格式
  downloading: false,         // 是否正在下载
  downloadProgress: {         // 下载进度
    status: 'idle',           // idle / downloading / merging / done / error
    percent: 0,
    speed: '',
    eta: '',
    filename: '',
  },
  error: null,                // 错误信息
})
```

### 3.3 API 调用封装（api/index.js）

```javascript
const API_BASE = '/api'

// 解析视频
async function parseVideo(url) {
  const res = await fetch(`${API_BASE}/parse?url=${encodeURIComponent(url)}`)
  return await res.json()
}

// 下载视频（SSE）
function downloadVideo(url, formatId, onProgress, onComplete, onError) {
  const eventSource = new EventSource(
    `${API_BASE}/download?url=${encodeURIComponent(url)}&format_id=${formatId}`
  )
  eventSource.addEventListener('progress', (e) => onProgress(JSON.parse(e.data)))
  eventSource.addEventListener('complete', (e) => {
    onComplete(JSON.parse(e.data))
    eventSource.close()
  })
  eventSource.addEventListener('error', (e) => {
    onError(e.data ? JSON.parse(e.data) : { message: '连接中断' })
    eventSource.close()
  })
  return eventSource // 返回以便取消
}

// 获取文件下载链接
function getFileUrl(filename) {
  return `${API_BASE}/file/${filename}`
}
```

### 3.4 UI 视觉规范

> 注：UI 已从初版暗色科技风改版为 SaveAny 亮色简洁风格，以下为当前实现。

#### 3.4.1 配色系统

```css
:root {
  /* 背景 */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-card: #ffffff;
  --bg-card-hover: #f8fafc;

  /* 强调色 */
  --accent-blue: #2563eb;
  --accent-blue-hover: #1d4ed8;
  --accent-blue-light: #eff6ff;
  --accent-gradient: linear-gradient(135deg, #2563eb, #1e90ff);

  /* 文字 */
  --text-primary: #1a1a2e;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;

  /* 边框 */
  --border-color: #e2e8f0;

  /* 状态 */
  --color-success: #22c55e;
  --color-error: #ef4444;
  --color-warning: #f59e0b;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.08);
}
```

#### 3.4.2 卡片样式

```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: var(--shadow-card);
  transition: all 0.25s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
}
```

#### 3.4.3 CTA 按钮样式

```css
.btn-primary {
  background: var(--accent-blue);
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 12px 32px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--accent-blue-hover);
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}
```

#### 3.4.4 响应式断点

```css
/* 移动端 */
@media (max-width: 768px) { ... }
/* 平板 */
@media (max-width: 1024px) { ... }
/* 桌面 */
@media (min-width: 1025px) { ... }
```

---

## 四、数据流设计

### 4.1 视频解析流程

```
[用户] 输入 URL，点击解析
   │
   ▼
[前端] POST /api/parse?url=xxx → loading = true
   │
   ▼
[后端] URL 校验 → yt_dlp.extract_info(url, download=False)
   │
   ├── 成功 → normalize_video_info() → 返回 JSON
   │
   └── 失败 → 返回错误码 + 友好提示
   │
   ▼
[前端] 收到响应 → loading = false
   │
   ├── 成功 → 渲染 VideoResult 组件（封面、标题、格式列表）
   │
   └── 失败 → 显示错误提示 toast
```

### 4.2 视频下载流程

```
[用户] 选择格式，点击下载
   │
   ▼
[前端] 判断 is_merged？
   │
   ├── true（已合一）
   │       │
   │       ▼
   │   [前端] 建立 SSE 连接 GET /api/download?url=xxx&format_id=yyy
   │       │
   │       ▼
   │   [后端] 尝试提取直链
   │       │
   │       ├── 直链可用 → SSE 推送 complete 事件（含直链 URL）
   │       │                → [前端] 用 <a download> 直接从 CDN 下载
   │       │
   │       └── 直链不可用 → 服务端下载 → SSE 推送 progress 事件
   │                         → 下载完成 → SSE 推送 complete 事件（含 filename）
   │                         → [前端] 从 /api/file/{filename} 下载
   │
   └── false（需合并）
           │
           ▼
       [前端] 建立 SSE 连接 GET /api/download?url=xxx&format_id=yyy
           │
           ▼
       [后端] yt-dlp 下载视频流 + 音频流 → SSE 推送 progress
           │
           ▼
       [后端] ffmpeg 合并 → SSE 推送 merging 状态
           │
           ▼
       [后端] 合并完成 → SSE 推送 complete（含 filename）
           │
           ▼
       [前端] 从 /api/file/{filename} 下载合并后的文件
```

---

## 五、部署方案

### 5.1 开发环境

```bash
# 终端 1：启动后端
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# 终端 2：启动前端
cd frontend
npm install
npm run dev    # Vite 开发服务器，自动代理 /api 到 localhost:8000
```

### 5.2 生产环境

```bash
# 1. 构建前端
cd frontend && npm run build    # 产出 dist/

# 2. FastAPI 托管前端静态文件
# app.py 中：
#   app.mount("/", StaticFiles(directory="../frontend/dist", html=True))

# 3. 启动服务
cd backend && uvicorn app:app --host 0.0.0.0 --port 8000
```

### 5.3 Vite 开发代理配置

```javascript
// vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

---

## 六、扩展性设计

### 6.1 为 v2.0 预留的扩展点

| 扩展方向 | 当前预留 | 扩展方式 |
|----------|----------|----------|
| 用户系统 | API 无鉴权 | 添加 JWT 中间件 + 用户路由 |
| 数据库 | 无 | 引入 SQLite/PostgreSQL + SQLAlchemy |
| 批量下载 | 单 URL 解析 | 新增 /api/batch-parse 接口 |
| 下载限制 | 无限制 | 中间件中检查用户配额 |
| 国际化 | 仅中文 | 前端 vue-i18n 插件 |
| 配置管理 | 硬编码 | 引入 .env + pydantic Settings |

### 6.2 代码扩展约定

- 新增平台特殊处理：在 `PLATFORM_MAP` 中添加映射，在 `_normalize_video_info` 中添加分支
- 新增平台专用模块（如抖音模式）：创建 `xxx_downloader.py`，在 `downloader.py` 的 `parse_video`/`download_video` 入口处添加路由判断
- 新增 API：创建独立路由模块 `xxx_routes.py`，通过 `app.include_router()` 注册（遵循开闭原则）
- 新增前端页面区块：创建 Vue 组件，在 `App.vue` 中引入
- 新增下载策略：在 `download_video` 方法中扩展策略分支

---

## 七、AI 智能分析模块设计（v2.0）

### 7.1 模块架构

```
┌──────────────────────────────────────────────────────────────────────┐
│                        用户浏览器                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    AISummaryPanel.vue                           │  │
│  │  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐  │  │
│  │  │ 视频摘要  │ 章节大纲  │ 知识要点  │ 字幕文本  │ 思维导图 │AI问答│  │  │
│  │  └──────────┴──────────┴──────────┴──────────┴──────────────┘  │  │
│  └───────────────────────────┬────────────────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────────────┘
                               │ HTTP / SSE
┌──────────────────────────────┼──────────────────────────────────────┐
│                          FastAPI 后端                                 │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    ai_routes.py (APIRouter)                     │ │
│  │  GET /api/ai/status     — AI 服务可用性检查                       │ │
│  │  GET /api/ai/subtitle   — 字幕/转录提取                          │ │
│  │  POST /api/ai/summarize — AI 内容总结 (SSE 流式)                  │ │
│  │  POST /api/ai/chat      — AI 视频问答 (SSE 流式)                  │ │
│  └──────────┬───────────────────────────┬────────────────────────┘ │
│             │                           │                          │
│  ┌──────────┴──────────┐   ┌───────────┴──────────┐               │
│  │ subtitle_extractor.py│   │   ai_service.py       │               │
│  │                      │   │                        │               │
│  │ 1. yt-dlp 手动字幕    │   │ DeepSeek API 调用       │               │
│  │ 2. yt-dlp 自动字幕    │   │ (OpenAI 兼容 SDK)       │               │
│  │ 3. faster-whisper     │   │                        │               │
│  │    语音识别（兜底）    │   │ - summarize_stream()   │               │
│  └───────────────────────┘   │ - chat_stream()        │               │
│                              └────────────────────────┘               │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                          ┌─────────┴─────────┐
                          │   DeepSeek API     │
                          │ api.deepseek.com   │
                          └────────────────────┘
```

### 7.2 AI API 接口设计

#### 7.2.1 检查 AI 服务状态

```
GET /api/ai/status
```

**成功响应（200）：**

```json
{ "available": true }
```

#### 7.2.2 提取字幕/转录

```
GET /api/ai/subtitle?url={video_url}
```

**成功响应（200）：**

```json
{
  "success": true,
  "data": {
    "segments": [
      { "start": 0.0, "end": 5.2, "text": "大家好..." },
      { "start": 5.2, "end": 10.1, "text": "今天我们..." }
    ],
    "full_text": "完整文本...",
    "language": "zh",
    "source": "subtitle"
  }
}
```

`source` 取值：`subtitle`（手动字幕）/ `auto_caption`（自动字幕）/ `whisper`（语音识别）

#### 7.2.3 AI 内容总结（SSE 流式）

```
POST /api/ai/summarize
Content-Type: application/json

{
  "transcript": "字幕全文...",
  "title": "视频标题",
  "language": "zh"
}
```

**SSE 事件流：**

```
event: chunk
data: {"content": "部分文本..."}

event: done
data: {"full_content": "完整JSON字符串"}

event: error
data: {"message": "错误信息"}
```

AI 返回的完整 JSON 结构：

```json
{
  "summary": "200-300字视频摘要",
  "chapters": [
    { "title": "章节标题", "start_time": "00:00", "summary": "章节概括" }
  ],
  "key_points": [
    { "point": "知识要点", "detail": "详细说明" }
  ],
  "mindmap": "# 主题\n## 子主题1\n### 要点1\n## 子主题2"
}
```

#### 7.2.4 AI 视频问答（SSE 流式）

```
POST /api/ai/chat
Content-Type: application/json

{
  "transcript": "字幕全文...",
  "title": "视频标题",
  "messages": [
    { "role": "user", "content": "这个视频主要讲了什么？" }
  ]
}
```

**SSE 事件流：** 同总结接口。

### 7.3 字幕提取模块设计（subtitle_extractor.py）

**三级回退策略：**

```
输入 URL
  │
  ├── 抖音链接？
  │     └── 是 → 直接跳到 faster-whisper 转录
  │
  └── 否 → yt-dlp 提取字幕
        │
        ├── 1. 手动字幕 (subtitles)
        │     ├── 语言优先级: zh-Hans > zh > en > 任意
        │     ├── 格式优先级: json3 > srv1 > vtt > srt
        │     └── 成功 → 返回 segments
        │
        ├── 2. 自动字幕 (automatic_captions)
        │     └── 同上策略
        │
        └── 3. 无字幕 → 下载音频 → faster-whisper 转录
              ├── 模型: small, CPU, int8
              ├── VAD 过滤静音片段
              └── 返回带时间戳的 segments
```

**缓存策略：** 内存 LRU 缓存（OrderedDict），上限 50 条，同 URL 不重复提取。

**faster-whisper 懒加载：** 模型仅在首次需要转录时加载，避免启动时占用内存（small 模型约 500MB）。

### 7.4 AI 服务模块设计（ai_service.py）

- 通过 OpenAI Python SDK 调用任意 OpenAI 兼容 API（默认 DeepSeek）
- 通过环境变量 `AI_BASE_URL`、`AI_API_KEY`、`AI_MODEL`、`AI_MAX_TOKENS` 灵活配置
- 向后兼容旧版 `DEEPSEEK_*` 环境变量
- 已验证支持 DeepSeek、Ollama 本地模型、硅基流动、OpenRouter 等提供商
- 总结使用 temperature=0.3（稳定性优先），问答使用 temperature=0.5（灵活性适中）
- 转录文本超长时自动截取前 60000 字符（约 2 小时视频内容）
- 使用 `httpx.Client(verify=False)` 绕过受限网络环境的 SSL 拦截
- 新增 `test_api_connection()` 诊断函数，暴露为 `/api/ai/check` 端点

### 7.5 前端 AI 组件架构

```
App.vue
├── ... (原有组件不变)
├── AISummaryPanel.vue           # AI 分析主面板（Tab 容器）
│   ├── SummaryTab.vue           # 视频摘要（Markdown 渲染）
│   ├── ChapterTab.vue           # 章节大纲（带时间戳卡片列表）
│   ├── KeyPointsTab.vue         # 关键知识点（2列卡片网格）
│   ├── TranscriptTab.vue        # 字幕文本（带时间戳 + 搜索）
│   ├── MindmapTab.vue           # 思维导图（markmap SVG 渲染）
│   └── AIChatTab.vue            # AI 问答（对话式 UI + 流式显示）
└── ... (原有组件不变)
```

**前端新增依赖：**

| 依赖 | 用途 |
|------|------|
| markmap-view | 思维导图 SVG 渲染引擎 |
| markmap-lib | Markdown → mindmap 数据转换 |
| marked | Markdown 渲染（用于摘要和问答内容） |

### 7.6 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| AI_BASE_URL | 否 | AI API 基础地址（默认 `https://api.deepseek.com`） |
| AI_API_KEY | 是（AI 功能） | AI API 密钥，未配置时 AI 功能不可用但不影响下载功能 |
| AI_MODEL | 否 | 模型名称（默认 `deepseek-chat`） |
| AI_MAX_TOKENS | 否 | 最大输出 token 数（默认 `4096`，推理模型建议 `16384`+） |

> 向后兼容：若 `AI_*` 变量未设置，将自动回退读取 `DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`。
