# SaveAny SEO 优化文档

> 版本：v1.0  
> 创建日期：2026-04-15  
> 最后更新：2026-04-15  
> 状态：已完成首轮优化

---

## 一、优化背景

产品从 FreeVidGrab 品牌统一为 **SaveAny（万能视频下载总结器）**，域名为 `maxczd.com`。目标是让用户能在全网各个搜索引擎（Google、百度、搜狗、360、必应等）优先看到产品内容。

由于项目是 Vue 3 SPA（单页应用），不使用 SSR，SEO 优化重点放在以下方面：
1. 静态 HTML 的 Meta 标签全覆盖
2. JSON-LD 结构化数据增加富文本展示机会
3. noscript 备用内容覆盖不执行 JS 的爬虫（如百度）
4. 爬虫友好性配置（robots.txt + sitemap.xml）

---

## 二、TDK 规范

### 2.1 首页 TDK

| 项目 | 内容 |
|------|------|
| **Title** | `SaveAny - 万能视频下载总结器 \| 免费下载YouTube、Bilibili、抖音视频与AI智能总结` |
| **Description** | `SaveAny 是一款免费的万能视频下载与AI智能总结工具，支持 YouTube、Bilibili、抖音、TikTok、Twitter/X、Instagram、小红书等1000+平台。一键解析视频链接，多种清晰度高清下载，AI自动生成视频摘要、章节大纲、知识要点和思维导图。立即免费使用！` |
| **Keywords** | `视频下载,在线视频下载,YouTube下载,B站视频下载,抖音视频下载,TikTok下载,AI视频总结,视频解析,免费视频下载工具,SaveAny` |

### 2.2 TDK 设计原则

- **Title**：品牌名前置 + 核心功能关键词 + 平台关键词，控制在 60 字符内
- **Description**：自然融入功能关键词、平台名称、使用场景，150-200 字符，含 CTA
- **Keywords**：10 个以内，按重要性排序，兼顾品牌词和长尾词

---

## 三、Meta 标签清单

### 3.1 基础必需标签

| 标签 | 用途 | 文件位置 |
|------|------|----------|
| `<title>` | 搜索结果标题 | `index.html` |
| `meta[description]` | 搜索结果摘要 | `index.html` |
| `meta[keywords]` | 百度/搜狗/360 关键词参考 | `index.html` |
| `meta[charset]` | 字符编码 UTF-8 | `index.html` |
| `meta[viewport]` | 移动端适配 | `index.html` |
| `meta[robots]` | 爬虫控制 `index, follow` | `index.html` |
| `link[canonical]` | 规范链接 `https://maxczd.com/` | `index.html` |

### 3.2 Open Graph 标签（社交分享）

| 标签 | 值 |
|------|-----|
| `og:title` | SaveAny - 万能视频下载总结器 \| 免费下载与AI智能总结 |
| `og:description` | 免费在线视频下载与AI智能总结工具... |
| `og:image` | `https://maxczd.com/og-share-image.png` |
| `og:type` | website |
| `og:url` | `https://maxczd.com/` |
| `og:locale` | zh_CN |
| `og:site_name` | SaveAny |

### 3.3 Twitter Card 标签

| 标签 | 值 |
|------|-----|
| `twitter:card` | summary_large_image |
| `twitter:title` | SaveAny - 万能视频下载总结器 |
| `twitter:description` | 免费在线视频下载与AI智能总结工具... |
| `twitter:image` | `https://maxczd.com/og-share-image.png` |

### 3.4 Schema.org 标签

| 标签 | 值 |
|------|-----|
| `itemprop[name]` | SaveAny - 万能视频下载总结器 |
| `itemprop[description]` | 免费在线视频下载与AI智能总结工具... |
| `itemprop[image]` | `https://maxczd.com/og-share-image.png` |

### 3.5 其他优化标签

| 标签 | 值 | 用途 |
|------|-----|------|
| `meta[format-detection]` | telephone=no | 阻止手机号自动识别 |
| `meta[theme-color]` | #2563eb | 移动浏览器主题色 |
| `meta[apple-mobile-web-app-title]` | SaveAny | iOS 书签名称 |
| `meta[application-name]` | SaveAny | Windows 磁贴名称 |
| `meta[X-UA-Compatible]` | IE=edge | IE 渲染模式 |

---

## 四、JSON-LD 结构化数据

### 4.1 WebApplication

类型为 `WebApplication`，包含：
- 产品名称、别名（中文）、URL
- 产品描述
- 分类：MultimediaApplication
- 运行环境：Web Browser
- 价格：免费（CNY 0）
- 功能列表（11 项）
- 截图、帮助页面、创建者信息

### 4.2 FAQPage

包含 4 个常见问题：
1. SaveAny 支持哪些视频平台？
2. SaveAny 是免费的吗？
3. SaveAny 的 AI 智能总结功能是什么？
4. 如何使用 SaveAny 下载视频？

FAQPage 结构化数据可在 Google 搜索结果中获得 FAQ 富文本摘要展示。

---

## 五、爬虫友好性配置

### 5.1 robots.txt

位置：`frontend/public/robots.txt` → 构建后 `dist/robots.txt`

```
User-agent: *
Allow: /
Disallow: /api/
Disallow: /downloads/
Sitemap: https://maxczd.com/sitemap.xml
```

- 允许爬虫抓取所有前端页面
- 禁止抓取 API 接口和临时下载目录
- 指向 sitemap 文件

### 5.2 sitemap.xml

位置：`frontend/public/sitemap.xml` → 构建后 `dist/sitemap.xml`

当前仅包含首页（SPA 单页应用）。如后续增加多页面路由，需同步更新 sitemap。

### 5.3 noscript 备用内容

在 `<body>` 中添加了 `<noscript>` 标签，为不执行 JavaScript 的搜索引擎爬虫（如早期百度爬虫）提供完整的 HTML 内容，包含：
- H1 产品标题
- 产品介绍段落
- 核心功能列表（H2 + ul）
- 支持平台列表（H2 + p）
- 使用方法步骤（H2 + ol）

---

## 六、页面结构优化

### 6.1 标题层级（Heading Hierarchy）

```
H1: 万能视频下载总结器，一键保存        (HeroSection.vue)
├── H2: 为什么选择 SaveAny              (FeatureCards.vue)
│   ├── H3: 极速解析
│   ├── H3: 多格式选择
│   ├── H3: AI 智能总结
│   ├── H3: AI 视频问答
│   ├── H3: 安全无忧
│   └── H3: 全端适配
├── H2: 支持的视频下载平台              (PlatformBar.vue)
├── H2: 解锁全部能力                    (PricingSection.vue)
│   ├── H3: 免费版
│   └── H3: 会员版
└── (动态) H3: 视频标题                  (VideoResult.vue)
```

### 6.2 语义化改进

| 改动 | 说明 |
|------|------|
| NavBar 品牌区 `<div>` → `<a>` | 可点击链接，添加 `title` 属性 |
| NavBar 品牌 Logo 添加 `role="img" aria-label` | 无障碍访问 |
| Footer 品牌名添加 `<a>` 链接 | 内链权重传递 |
| Footer 新增平台关键词文案 | 增加页面关键词密度 |
| VideoResult 缩略图 `alt` | 已有 `:alt="info.title"`（原始代码已正确） |

---

## 七、社交分享图片

- 文件：`frontend/public/og-share-image.png`
- 尺寸：1200 × 630px
- 用途：微信、Facebook、Twitter、LinkedIn 等平台分享预览
- 内容：SaveAny 品牌名 + 中文产品名 + 平台标签 + 功能图标

---

## 八、新增/修改文件清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `frontend/public/robots.txt` | 搜索引擎爬虫控制 |
| `frontend/public/sitemap.xml` | XML 网站地图 |
| `frontend/public/og-share-image.png` | 社交分享图片 |
| `docs/seo-optimization.md` | SEO 优化文档（本文件） |

### 修改文件

| 文件 | 改动 |
|------|------|
| `frontend/index.html` | 完整 SEO Meta 标签体系 + JSON-LD + noscript |
| `frontend/src/App.vue` | Footer 品牌名统一 + 关键词文案 + 链接样式 |
| `frontend/src/components/HeroSection.vue` | H1 关键词优化 + 副标题内容 |
| `frontend/src/components/NavBar.vue` | 品牌区语义化 `<a>` + 标签文字 |
| `frontend/src/components/FeatureCards.vue` | 新增 AI 功能卡片 + H2 品牌词 + 网格布局 |
| `frontend/src/components/PlatformBar.vue` | H2 关键词优化 + 副标题内容 |

---

## 九、上线后待办

### 必做项

- [ ] 提交 sitemap 到 Google Search Console
- [ ] 提交 sitemap 到百度站长平台
- [ ] 提交 sitemap 到必应 Webmaster Tools
- [ ] 用 Google Rich Results Test 验证结构化数据
- [ ] 用 Facebook Sharing Debugger 验证 OG 标签
- [ ] 确保 HTTPS 已启用

### 建议项

- [ ] 注册 Google Analytics 或百度统计
- [ ] 每月审查关键词排名和收录情况
- [ ] 如新增页面路由，同步更新 sitemap.xml
- [ ] 考虑引入 SSR（Nuxt.js）进一步提升 SEO 效果
- [ ] 为高价值长尾词创建独立落地页（如"YouTube 视频下载"、"B站视频下载"）
