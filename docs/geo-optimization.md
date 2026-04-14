# SaveAny GEO 优化文档（Generative Engine Optimization）

> 版本：v1.0  
> 创建日期：2026-04-15  
> 最后更新：2026-04-15  
> 状态：已完成首轮优化

---

## 一、什么是 GEO

GEO（Generative Engine Optimization，生成式引擎优化）也称 AEO（Answer Engine Optimization），是针对 AI 对话引擎的优化策略。目标是让产品在用户与 AI 对话时（ChatGPT、Claude、Gemini、Perplexity、Kimi、豆包等）被引用、推荐或提及。

**GEO 与 SEO 的核心区别：**
- SEO 关注搜索结果中的链接排名和点击
- GEO 关注 AI 生成的回答中是否引用/推荐你的产品
- AI 模型依赖高质量、结构化、权威性强的内容来源

---

## 二、GEO 核心策略

### 2.1 技术可访问性

AI 爬虫需要能抓取到页面内容。关键措施：

1. **robots.txt 显式允许 AI 爬虫**（已实施）
2. **llms.txt / llms-full.txt**：为 AI 模型提供结构化产品索引（已实施）
3. **noscript 备用内容**：AI 爬虫大多不执行 JS，需要在 HTML 中直接提供内容（已实施）
4. **JSON-LD 结构化数据**：帮助 AI 理解页面内容语义（已实施）

### 2.2 Answer-First 内容格式

AI 模型偏好"先给答案"的内容结构：
- 每个问题/段落的首句直接给出核心答案
- 使用 200-400 字的自包含内容块
- 用 H2/H3 清晰划分主题，方便 AI 提取特定事实

### 2.3 实体权威性（Entity Authority）

在全网建立一致的品牌信息：
- 品牌名称：SaveAny
- 产品描述：万能视频下载总结器
- 网址：https://maxczd.com/
- 核心功能：视频下载 + AI 智能总结

### 2.4 第三方平台存在感

AI 模型经常从第三方平台抓取信息，建议在以下平台建立存在感：
- GitHub（开源项目）
- Reddit / V2EX / 知乎 等技术社区
- YouTube（产品演示视频）
- Product Hunt（产品发布）

---

## 三、已实施的 GEO 优化

### 3.1 llms.txt（AI 模型站点索引）

**文件**：`frontend/public/llms.txt` → `https://maxczd.com/llms.txt`

遵循 llms.txt 规范（Markdown 格式），包含：
- H1 产品名称 + 核心描述（blockquote）
- 产品基础信息（网址、类型、定价）
- 核心功能链接列表
- 支持平台链接列表
- 使用方法链接
- 价格方案链接
- 指向 llms-full.txt 的完整文档链接

### 3.2 llms-full.txt（完整产品文档）

**文件**：`frontend/public/llms-full.txt` → `https://maxczd.com/llms-full.txt`

一个完整的 Markdown 文档，AI 模型可一次性读取全部产品信息：
- 产品概述（目标用户、产品亮点）
- 核心功能详情（视频下载步骤、AI 总结各子功能、字幕获取策略）
- 支持平台清单（含各平台说明）
- 价格方案对比
- 10 个常见问题解答（answer-first 格式）
- 技术架构概览

### 3.3 robots.txt AI 爬虫规则

**文件**：`frontend/public/robots.txt` → `https://maxczd.com/robots.txt`

明确允许以下 AI 爬虫访问全站内容：

| 爬虫 User-Agent | 归属 | 用途 |
|-----------------|------|------|
| `ChatGPT-User` | OpenAI | ChatGPT 实时搜索 |
| `OAI-SearchBot` | OpenAI | OpenAI 搜索引擎 |
| `GPTBot` | OpenAI | 模型训练 |
| `ClaudeBot` | Anthropic | Claude 训练 |
| `anthropic-ai` | Anthropic | Claude Web 搜索 |
| `PerplexityBot` | Perplexity | AI 搜索引擎 |
| `Google-Extended` | Google | Gemini AI 训练 |
| `Applebot-Extended` | Apple | Apple Intelligence |
| `FacebookBot` | Meta | Meta AI |
| `Bingbot` | Microsoft | Copilot / Bing AI |
| `Bytespider` | 字节跳动 | 豆包 / Coze |

### 3.4 FAQ 页面组件

**文件**：`frontend/src/components/FAQSection.vue`

新增可折叠 FAQ 区块，包含 8 个常见问题，采用 answer-first 格式：
1. SaveAny 是什么？
2. 如何使用 SaveAny 下载视频？
3. SaveAny 支持哪些视频平台？
4. SaveAny 是免费的吗？
5. AI 智能总结功能怎么用？
6. 可以下载无水印的抖音视频吗？
7. 在手机上可以使用吗？
8. 下载的视频安全吗？会保留数据吗？

FAQ 内容同时体现在：
- 页面可见 FAQ 组件（JS 渲染）
- noscript 备用内容（HTML 静态）
- JSON-LD FAQPage 结构化数据
- llms-full.txt 完整文档

### 3.5 JSON-LD 结构化数据增强

在已有 WebApplication + FAQPage 基础上新增：

**HowTo 结构化数据**：
- 名称：如何使用 SaveAny 免费下载视频
- 总耗时：约 1 分钟
- 三步操作指南（复制链接 → 解析视频 → 选择下载）

**FAQPage 扩展**：从 4 个问题扩展到 8 个，覆盖更多用户可能在 AI 对话中提出的问题。

### 3.6 noscript 内容增强

将 noscript 备用内容从简单列表升级为完整的 answer-first 格式页面：
- 产品介绍（首句即核心答案）
- 使用步骤（HowTo 格式）
- 功能列表（带加粗标题）
- 平台清单（带各平台说明）
- FAQ 问答（H3 问题 + 直接回答段落）

---

## 四、新增/修改文件清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `frontend/public/llms.txt` | AI 模型站点索引（Markdown 格式） |
| `frontend/public/llms-full.txt` | 完整产品文档供 AI 全量读取 |
| `frontend/src/components/FAQSection.vue` | FAQ 可折叠组件（8 个问答） |
| `docs/geo-optimization.md` | GEO 优化沉淀文档（本文件） |

### 修改文件

| 文件 | 改动 |
|------|------|
| `frontend/public/robots.txt` | 新增 11 个 AI 爬虫的 Allow 规则 |
| `frontend/index.html` | FAQPage 扩展到 8 个问题 + 新增 HowTo JSON-LD + noscript 内容增强 |
| `frontend/src/App.vue` | 注册并引入 FAQSection 组件 |
| `frontend/src/components/NavBar.vue` | 导航新增"常见问题"锚点链接 |

---

## 五、后续建议

### 高优先级

- [ ] 在 GitHub、知乎、V2EX 等平台发布产品介绍，建立第三方引用
- [ ] 创建产品演示视频发布到 YouTube 和 Bilibili
- [ ] 定期更新 llms-full.txt 保持信息时效性

### 中优先级

- [ ] 考虑引入 SSR（Nuxt.js），彻底解决 AI 爬虫 JS 渲染问题
- [ ] 为"YouTube 视频下载"、"B 站视频下载"等长尾关键词创建独立落地页
- [ ] 在 Product Hunt 发布产品

### 监控指标

- [ ] 使用 Perplexity 搜索产品相关关键词，检查是否被引用
- [ ] 在 ChatGPT、Claude、Gemini 中提问相关问题，检查是否推荐 SaveAny
- [ ] 监控 llms.txt 和 llms-full.txt 的访问日志
