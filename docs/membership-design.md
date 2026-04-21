# 会员订阅支付系统 - 方案设计文档

> 版本：v2.0
> 创建日期：2026-04-16
> 最后更新：2026-04-21
> 状态：已实现（Phase 1-6 全部完成）

---

## 一、需求概述

为「万能视频下载器 SaveAny」增加 **用户购买会员** 功能，实现从注册登录到订阅支付的完整链路。

### 1.1 功能清单

| 编号 | 功能 | 说明 |
|------|------|------|
| M-001 | 邮箱注册/登录 | 用户通过邮箱 + 密码注册和登录 |
| M-002 | Google/GitHub OAuth | 第三方社交登录 |
| M-003 | JWT 认证 | Access Token + Refresh Token 双令牌机制 |
| M-004 | Stripe 嵌入式支付 | 在站内完成订阅支付（Embedded Checkout） |
| M-005 | 月付/年付套餐 | ¥9.9/月 或 ¥99/年（省 ¥19.8） |
| M-006 | Webhook 订阅同步 | 通过 Stripe Webhook 实时同步订阅状态 |
| M-007 | 幂等事件处理 | webhook_events 表防止重复处理 |
| M-008 | 客户门户 | Stripe Customer Portal 管理订阅（升降级/取消/换卡） |
| M-009 | 账户管理页 | 查看个人信息和订阅状态 |
| M-010 | 路由守卫 | 认证保护页面 + 已登录跳过登录页 |
| M-011 | VIP 状态持久化与展示 | 支付后轮询同步 VIP 状态，NavBar / 账户页实时显示 |
| M-012 | 画质限制 | 免费用户最高 720p，VIP 用户解锁 4K 原画 |
| M-013 | 字幕下载限制 | SRT/VTT 字幕文件下载仅限 VIP 用户 |
| M-014 | AI 分析次数限制 | 免费用户每日 3 次，VIP 无限次（基于 UsageCounter） |
| M-015 | 头像上传 | 支持 JPG/PNG/WebP/GIF，限制 2MB，本地文件存储 |
| M-016 | 下载历史 | 记录并展示用户的视频下载历史，分页加载 |

### 1.2 技术选型

| 层级 | 技术 | 选型理由 |
|------|------|----------|
| 数据库 | SQLite + SQLAlchemy 2.0 | 零配置、单文件、适合个人/小型项目 |
| 密码哈希 | bcrypt | 行业标准，抗 GPU 暴力破解 |
| JWT | PyJWT | 轻量、主流、主动维护 |
| 支付 | Stripe（stripe-python + @stripe/stripe-js） | 全球主流支付平台，API 设计优秀 |
| OAuth | httpx + 手写实现 | 无需引入重量级框架（authlib 等） |
| 文件上传 | python-multipart | FastAPI 文件上传依赖 |
| 前端路由 | vue-router 4 | Vue 3 官方路由 |

---

## 二、系统架构

### 2.1 整体数据流

```
┌────────────────────────────────────────────────────────────────────┐
│                          用户浏览器                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Vue 3 + Vue Router                                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐   │  │
│  │  │ 登录/注册 │ │ 首页     │ │ 支付页   │ │ 账户管理      │   │  │
│  │  │ (JWT)     │ │ (现有)   │ │(Stripe.js│ │ (订阅状态)    │   │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───────┬───────┘   │  │
│  └───────┼────────────┼────────────┼────────────────┼───────────┘  │
└──────────┼────────────┼────────────┼────────────────┼──────────────┘
           │ JWT        │ HTTP       │ Stripe.js      │ JWT
┌──────────┼────────────┼────────────┼────────────────┼──────────────┐
│          ▼            ▼            │                ▼              │
│  ┌──────────────┐ ┌────────┐      │  ┌──────────────────────┐    │
│  │ Auth Routes  │ │Video/AI│      │  │ Payment Routes       │    │
│  │ /api/auth/*  │ │(现有)  │      │  │ /api/payment/*       │    │
│  └──────┬───────┘ └────────┘      │  └──────┬──────┬────────┘    │
│         │                         │         │      │              │
│         ▼                         │         ▼      ▼              │
│  ┌─────────────┐                  │  ┌──────────┐ ┌────────┐     │
│  │ SQLite      │                  │  │ Stripe   │ │Webhook │     │
│  │ users       │◄─────────────────┘  │ Checkout │ │Handler │     │
│  │ subscriptions│                    └──────────┘ └───┬────┘     │
│  │ payments    │                                      │          │
│  │ webhook_evts│◄─────────────────────────────────────┘          │
│  └─────────────┘                                                  │
│                        FastAPI 后端                                │
└──────────────────────────────────────────────────────────────────┘
                                    ▲ Webhook
                           ┌────────┴────────┐
                           │  Stripe 服务器   │
                           └─────────────────┘
```

### 2.2 新增文件结构

```
free-video-download/
├── backend/
│   ├── database.py              # NEW: SQLAlchemy 引擎、Session、建表
│   ├── models.py                # NEW: ORM 模型 (User, Subscription, Payment, WebhookEvent, UsageCounter, DownloadHistory)
│   ├── auth.py                  # NEW: JWT + bcrypt 工具函数
│   ├── deps.py                  # NEW: FastAPI 依赖注入 (get_current_user, require_vip, check_and_increment_usage 等)
│   ├── auth_routes.py           # NEW: 认证路由 (注册/登录/OAuth/头像上传/下载历史)
│   ├── oauth.py                 # NEW: Google/GitHub OAuth 工具
│   ├── payment_routes.py        # NEW: Stripe 支付路由 (Checkout/Webhook)
│   ├── ai_routes.py             # MODIFIED: AI 分析添加用量限制
│   ├── app.py                   # MODIFIED: 注册新路由、初始化数据库、画质限制、下载历史记录
│   ├── data/avatars/            # NEW: 用户头像文件存储目录（自动创建，已 gitignore）
│   ├── requirements.txt         # MODIFIED: +6 依赖
│   └── .env.example             # MODIFIED: +JWT/Stripe/OAuth 配置
├── frontend/
│   ├── src/
│   │   ├── router/index.js      # NEW: Vue Router 配置 + 路由守卫
│   │   ├── stores/auth.js       # NEW: 认证状态管理 (JWT + localStorage)
│   │   ├── composables/useToast.js # NEW: 全局 Toast 通知
│   │   ├── api/auth.js          # NEW: 认证 API 封装 (含头像上传、下载历史、记录下载)
│   │   ├── api/ai.js            # MODIFIED: AI API 添加认证头、配额查询、超限处理
│   │   ├── api/index.js         # MODIFIED: parseVideo 添加认证头
│   │   ├── api/payment.js       # NEW: 支付 API 封装
│   │   ├── views/
│   │   │   ├── HomeView.vue     # NEW: 首页 (从 App.vue 迁出)
│   │   │   ├── LoginView.vue    # NEW: 登录页
│   │   │   ├── RegisterView.vue # NEW: 注册页
│   │   │   ├── OAuthCallbackView.vue  # NEW: OAuth 回调处理
│   │   │   ├── CheckoutView.vue       # NEW: 嵌入式支付页
│   │   │   ├── CheckoutReturnView.vue # NEW: 支付完成页
│   │   │   └── AccountView.vue        # NEW+MODIFIED: 账户管理页 (VIP/免费标识、头像上传、下载历史)
│   │   ├── App.vue              # MODIFIED: 重构为 router-view 布局
│   │   ├── main.js              # MODIFIED: 挂载 router
│   │   └── components/
│   │       ├── NavBar.vue       # MODIFIED: 认证感知 + 自动刷新 VIP 状态
│   │       ├── PricingSection.vue # MODIFIED: 跳转支付页 + VIP 已开通状态
│   │       ├── VideoResult.vue  # MODIFIED: 非 VIP 画质限制提示
│   │       ├── TranscriptTab.vue # MODIFIED: 字幕下载 VIP 门控
│   │       └── AISummaryPanel.vue # MODIFIED: AI 分析次数配额显示
│   └── package.json             # MODIFIED: +vue-router, @stripe/stripe-js
└── docs/
    └── membership-design.md     # NEW: 本文档
```

---

## 三、数据库设计

### 3.1 ER 图

```
┌─────────────────────┐     ┌─────────────────────────┐
│       users          │     │     subscriptions         │
├─────────────────────┤     ├─────────────────────────┤
│ id (PK, UUID)       │◄────│ user_id (FK)             │
│ email (UNIQUE)      │     │ id (PK, UUID)            │
│ password_hash       │     │ stripe_subscription_id   │
│ name                │     │ stripe_price_id          │
│ avatar_url          │     │ plan_type / status        │
│ auth_provider       │     │ current_period_start/end │
│ auth_provider_id    │     │ cancel_at_period_end     │
│ stripe_customer_id  │     │ created_at / updated_at  │
│ is_vip              │     └─────────────────────────┘
│ vip_expire_at       │
│ is_active           │     ┌─────────────────────────┐
│ created_at          │     │       payments            │
│ updated_at          │◄────├─────────────────────────┤
│                     │     │ user_id (FK)             │
│                     │     │ stripe_payment_intent_id │
└────────┬────────────┘     │ amount / currency        │
         │                  │ status / created_at      │
         │                  └─────────────────────────┘
         │
         │  ┌─────────────────────────┐
         │  │   webhook_events        │
         │  ├─────────────────────────┤
         │  │ stripe_event_id (UQ)    │
         │  │ event_type / processed  │
         │  └─────────────────────────┘
         │
         ├──┌─────────────────────────┐
         │  │   usage_counters        │
         │  ├─────────────────────────┤
         │  │ user_id (FK) / ip_addr  │
         │  │ usage_type / usage_date │
         │  │ count                   │
         │  └─────────────────────────┘
         │
         └──┌─────────────────────────┐
            │   download_history      │
            ├─────────────────────────┤
            │ user_id (FK)            │
            │ video_url / video_title │
            │ thumbnail / platform    │
            │ quality / filesize      │
            │ created_at              │
            └─────────────────────────┘
```

### 3.2 字段说明

#### users 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | TEXT (UUID) | PK | 用户唯一 ID |
| email | TEXT | UNIQUE, NOT NULL, INDEX | 登录邮箱 |
| password_hash | TEXT | NULLABLE | bcrypt 哈希（OAuth 用户无密码） |
| name | TEXT | NOT NULL | 显示名称 |
| avatar_url | TEXT | NULLABLE | 头像 URL |
| auth_provider | TEXT | NOT NULL, DEFAULT 'email' | 注册方式：email / google / github |
| auth_provider_id | TEXT | NULLABLE | OAuth 提供商用户 ID |
| stripe_customer_id | TEXT | NULLABLE, UNIQUE, INDEX | Stripe Customer ID |
| is_vip | BOOLEAN | DEFAULT FALSE | VIP 状态（冗余字段，由 Webhook 更新） |
| vip_expire_at | DATETIME | NULLABLE | VIP 过期时间 |
| is_active | BOOLEAN | DEFAULT TRUE | 账户是否启用 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

#### subscriptions 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | TEXT (UUID) | PK | 记录 ID |
| user_id | TEXT | FK → users.id, INDEX | 关联用户 |
| stripe_subscription_id | TEXT | UNIQUE, INDEX | Stripe Subscription ID |
| stripe_price_id | TEXT | NOT NULL | Stripe Price ID |
| plan_type | TEXT | NOT NULL | monthly / yearly |
| status | TEXT | NOT NULL | active / past_due / canceled / incomplete / trialing |
| current_period_start | DATETIME | | 当前计费周期开始 |
| current_period_end | DATETIME | | 当前计费周期结束 |
| cancel_at_period_end | BOOLEAN | DEFAULT FALSE | 是否到期后取消 |
| created_at / updated_at | DATETIME | | 时间戳 |

#### payments 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | TEXT (UUID) | PK | 记录 ID |
| user_id | TEXT | FK → users.id, INDEX | 关联用户 |
| stripe_payment_intent_id | TEXT | UNIQUE, INDEX | 防重复支付的关键字段 |
| stripe_invoice_id | TEXT | NULLABLE | Stripe Invoice ID |
| amount | INTEGER | NOT NULL | 金额（最小货币单位，如 990 = ¥9.90） |
| currency | TEXT | DEFAULT 'cny' | 币种 |
| status | TEXT | NOT NULL | succeeded / failed / pending / refunded |
| created_at | DATETIME | | 创建时间 |

#### webhook_events 表（幂等性保证）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | TEXT (UUID) | PK | 记录 ID |
| stripe_event_id | TEXT | UNIQUE, INDEX | Stripe Event ID（幂等关键） |
| event_type | TEXT | NOT NULL | 事件类型 |
| processed | BOOLEAN | DEFAULT FALSE | 是否已处理 |
| created_at | DATETIME | | 接收时间 |

#### usage_counters 表（功能用量限制）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | TEXT (UUID) | PK | 记录 ID |
| user_id | TEXT | FK → users.id, NULLABLE | 登录用户关联（未登录时为 NULL） |
| ip_address | TEXT | NULLABLE | 未登录用户以 IP 追踪 |
| usage_type | TEXT | NOT NULL | 用量类型（如 `ai_analysis`） |
| usage_date | DATE | NOT NULL | 日期（按天重置） |
| count | INTEGER | DEFAULT 0 | 当日已使用次数 |

> 唯一约束：`UQ(user_id, usage_type, usage_date)` + `UQ(ip_address, usage_type, usage_date)`

#### download_history 表（下载历史记录）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | TEXT (UUID) | PK | 记录 ID |
| user_id | TEXT | FK → users.id, INDEX | 关联用户 |
| video_url | TEXT | NOT NULL | 视频原始 URL |
| video_title | TEXT | NOT NULL | 视频标题 |
| thumbnail | TEXT | NULLABLE | 缩略图 URL |
| platform | TEXT | NULLABLE | 来源平台（YouTube、Bilibili 等） |
| quality | TEXT | NULLABLE | 下载画质 |
| filesize | INTEGER | NULLABLE | 文件大小（字节） |
| created_at | DATETIME | | 下载时间 |

---

## 四、API 接口设计

### 4.1 认证接口 (/api/auth)

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | /api/auth/register | 无 | 邮箱注册，返回 JWT + 用户信息 |
| POST | /api/auth/login | 无 | 邮箱登录，返回 JWT + 用户信息 |
| POST | /api/auth/refresh | 无 | 刷新 Access Token |
| GET | /api/auth/me | Bearer | 获取当前用户信息 |
| GET | /api/auth/google | 无 | 重定向到 Google 授权页 |
| GET | /api/auth/google/callback | 无 | Google OAuth 回调，重定向前端并携带 JWT |
| GET | /api/auth/github | 无 | 重定向到 GitHub 授权页 |
| GET | /api/auth/github/callback | 无 | GitHub OAuth 回调，重定向前端并携带 JWT |
| POST | /api/auth/avatar | Bearer | 上传用户头像（multipart/form-data），返回更新后用户信息 |
| GET | /api/auth/avatar/{filename} | 无 | 获取头像文件（静态资源） |
| GET | /api/auth/download-history | Bearer | 获取下载历史（分页：page, page_size） |

### 4.2 支付接口 (/api/payment)

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | /api/payment/create-checkout-session | Bearer | 创建嵌入式 Checkout Session |
| GET | /api/payment/session-status | Bearer | 查询 Session 支付结果 |
| GET | /api/payment/subscription | Bearer | 获取当前订阅状态 |
| POST | /api/payment/create-portal-session | Bearer | 创建 Stripe 客户门户会话 |
| POST | /api/payment/webhook | 无（签名验证） | Stripe Webhook 回调 |

### 4.3 功能限制接口

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | /api/parse | 可选 Bearer | 解析视频（非 VIP 过滤 >720p 格式，返回 quality_limited 标志） |
| POST | /api/download-history | Bearer | 前端下载完成后记录下载历史 |
| GET | /api/ai/quota | 可选 Bearer | 查询当前用户/IP 的 AI 分析剩余配额 |
| POST | /api/ai/summarize | 可选 Bearer | AI 摘要（非 VIP 每日 3 次限制） |
| POST | /api/ai/chat | 可选 Bearer | AI 对话（非 VIP 每日 3 次限制，与摘要共享配额） |

### 4.4 配置接口

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | /api/config | 无 | 返回前端需要的非敏感配置（Stripe publishable key） |

---

## 五、Stripe 支付流程

### 5.1 订阅支付全流程

```
用户点击"升级 VIP"
    │
    ├── 未登录？ → 路由守卫跳转 /login?redirect=/checkout
    │
    ▼
/checkout 页面：选择月付/年付
    │
    ▼
前端 POST /api/payment/create-checkout-session { plan: "monthly" }
    │
    ▼
后端：
  1. get_or_create_customer(user) → stripe_customer_id
  2. 检查是否已有活跃订阅（防重复购买）
  3. stripe.checkout.Session.create(
       mode="subscription",
       ui_mode="embedded",
       customer=stripe_customer_id,
       client_reference_id=user.id,
       line_items=[{price: price_id, quantity: 1}],
       return_url=".../checkout/return?session_id={CHECKOUT_SESSION_ID}"
     )
  4. 返回 { client_secret }
    │
    ▼
前端：
  stripe.initEmbeddedCheckout({ clientSecret })
  → 渲染 Stripe 支付表单
    │
    ▼
用户在嵌入表单中填写卡号、完成支付
    │
    ▼
Stripe 重定向到 /checkout/return?session_id=xxx
    │
    ▼
前端 GET /api/payment/session-status?session_id=xxx
    │
    ├── status=complete → 显示成功页面，刷新用户信息
    └── status=其他 → 显示失败/重试
    │
    ▼
同时，Stripe 后台发送 Webhook:
  checkout.session.completed → 后端创建 Subscription 记录，标记 is_vip=true
  invoice.payment_succeeded → 后端记录 Payment
```

### 5.2 Webhook 处理的事件

| 事件 | 处理逻辑 |
|------|----------|
| `checkout.session.completed` | 首次支付成功：检索 Subscription 详情，创建本地记录，标记 VIP |
| `customer.subscription.updated` | 订阅变更（升级/降级/续费）：同步 status、period_end |
| `customer.subscription.deleted` | 订阅彻底删除：取消 VIP 状态 |
| `invoice.payment_succeeded` | 续费成功：记录 Payment，更新订阅周期 |
| `invoice.payment_failed` | 续费失败：记录失败 Payment，状态变为 past_due |

### 5.3 幂等性保证

每个 Stripe Webhook 事件携带唯一 `event.id`。处理流程：

1. 收到 Webhook → 验证签名（`stripe.Webhook.construct_event`）
2. 查询 `webhook_events` 表：`stripe_event_id` 是否已存在且 `processed=True`
3. 已处理 → 直接返回 200，不重复执行业务逻辑
4. 未处理 → 插入记录 → 执行业务逻辑 → 标记 `processed=True` → commit
5. `stripe_event_id` 列有 UNIQUE 约束，并发场景下数据库级别也能防重

### 5.4 安全措施

| 措施 | 实现 |
|------|------|
| Webhook 签名验证 | 每次用 `stripe.Webhook.construct_event` 验证 `Stripe-Signature` 头 |
| 防重复购买 | 创建 Checkout Session 前检查用户是否已有 active 订阅 |
| 防重复支付记录 | payments 表 `stripe_payment_intent_id` UNIQUE 约束 |
| 幂等事件处理 | webhook_events 表 `stripe_event_id` UNIQUE 约束 |
| Customer 绑定 | 每个 User 对应唯一 Stripe Customer（`stripe_customer_id` UNIQUE） |

---

## 六、认证系统设计

### 6.1 JWT 双令牌机制

| 令牌 | 有效期 | 用途 |
|------|--------|------|
| Access Token | 1 小时 | API 请求认证（Authorization: Bearer xxx） |
| Refresh Token | 7 天 | 过期后换取新的 Access Token |

**存储方式：** 前端 localStorage（键名 `sv_access_token`、`sv_refresh_token`、`sv_user`）

**安全考虑：** API 采用 Bearer Token 方式认证，不使用 Cookie，天然免疫 CSRF。

### 6.2 密码安全

- 使用 bcrypt 哈希（自动加盐，10 轮）
- 数据库只存哈希值，无法反推原文
- 密码最低 6 位限制

### 6.3 OAuth 流程

```
用户点击"Google 登录"
    │
    ▼
GET /api/auth/google → 302 重定向到 Google 授权页
    │
    ▼
用户在 Google 授权 → 302 回调到 /api/auth/google/callback?code=xxx
    │
    ▼
后端：
  1. exchange_code(code) → access_token
  2. get_userinfo(access_token) → { email, name, picture }
  3. 查找/创建用户（以 email 关联）
  4. 生成 JWT
  5. 302 重定向到前端 /oauth-callback?access_token=xxx&user=xxx
    │
    ▼
前端 OAuthCallbackView：
  1. 从 URL 参数解析 token 和用户信息
  2. 存入 localStorage
  3. 跳转首页
```

---

## 七、前端路由设计

| 路径 | 组件 | 守卫 | 说明 |
|------|------|------|------|
| / | HomeView | 无 | 首页（视频下载 + AI 分析 + 定价展示） |
| /login | LoginView | guestOnly | 登录页（已登录跳回首页） |
| /register | RegisterView | guestOnly | 注册页 |
| /oauth-callback | OAuthCallbackView | 无 | OAuth 回调中转页 |
| /checkout | CheckoutView | requiresAuth | 套餐选择 + 嵌入式 Stripe 支付 |
| /checkout/return | CheckoutReturnView | requiresAuth | 支付结果页 |
| /account | AccountView | requiresAuth | 账户设置 + 订阅管理 |

---

## 八、环境变量配置

```bash
# ---------- JWT 认证 ----------
JWT_SECRET_KEY=change-this-to-a-random-secret-string
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# ---------- Stripe 支付 ----------
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_MONTHLY_PRICE_ID=price_xxx
STRIPE_YEARLY_PRICE_ID=price_xxx

# ---------- OAuth（可选）----------
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# ---------- 应用 ----------
APP_URL=http://localhost:5173
```

---

## 九、Stripe 本地测试指南

### 9.1 前置准备

1. 注册 Stripe 账户，获取测试密钥（`sk_test_`、`pk_test_`）
2. 在 Dashboard → Products 创建产品和价格，获取 Price ID
3. 填入 `.env` 文件

### 9.2 Stripe CLI 本地测试（推荐）

```bash
# 安装
brew install stripe/stripe-cli/stripe

# 登录
stripe login

# 转发 Webhook 到本地
stripe listen --forward-to localhost:8000/api/payment/webhook
# 终端会输出 whsec_xxx，填入 .env 的 STRIPE_WEBHOOK_SECRET

# 触发测试事件
stripe trigger checkout.session.completed
stripe trigger invoice.payment_succeeded
```

### 9.3 测试信用卡号

| 卡号 | 场景 |
|------|------|
| 4242 4242 4242 4242 | 支付成功 |
| 4000 0025 0000 3155 | 需要 3D Secure 验证 |
| 4000 0000 0000 9995 | 支付被拒绝 |

> 有效期填任意未来日期，CVC 填任意 3 位数字。

### 9.4 完全离线测试

如无法连接外网，可使用 `localstripe` 模拟 Stripe 服务器：

```bash
pip install localstripe
localstripe  # 启动在 localhost:8420

# 修改 .env
STRIPE_API_BASE=http://localhost:8420
```

---

## 十、开发阶段记录

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase 1 | SQLite 数据库 + 邮箱注册登录 + JWT 认证 | ✅ 已完成 |
| Phase 2 | Google/GitHub OAuth 登录 | ✅ 已完成 |
| Phase 3 | Stripe 嵌入式 Checkout + Webhook + 订阅管理 | ✅ 已完成 |
| Phase 4 | VIP 权限控制 + NavBar 打通 + 账户管理页 | ✅ 已完成 |
| Phase 5 | VIP 状态持久化 + 功能权限差异（画质/字幕/AI 限制） | ✅ 已完成 |
| Phase 6 | 用户中心完善（头像上传 + 下载历史 + 信息面板重构） | ✅ 已完成 |

### Phase 5 详细记录

- **VIP 状态同步**：支付完成后前端轮询 `refreshUser()` 最多 5 次（间隔 2s），NavBar 挂载时自动刷新
- **画质限制**：后端 `/api/parse` 过滤 >720p 格式，前端显示 "升级 VIP 解锁 1080p / 4K 原画" 提示
- **字幕下载**：前端 `TranscriptTab` 对非 VIP 用户显示锁定按钮并引导升级
- **AI 分析配额**：后端 `UsageCounter` 按天计数，免费 3 次/天，VIP 无限；前端显示配额徽章，超限后按钮变为升级引导

### Phase 6 详细记录

- **头像上传**：`POST /api/auth/avatar` 接收 multipart 文件，限 JPG/PNG/WebP/GIF、2MB，存储在 `backend/data/avatars/`
- **下载历史**：`DownloadHistory` 模型 + 分页查询接口；前端下载完成后自动调用 `recordDownload()` 记录
- **账户页重构**：个人信息卡片（可点击上传头像 + VIP/免费标识 + 到期时间 + 注册时间）、会员订阅卡片、下载历史卡片（缩略图 + 元数据 + 分页加载）

### 后续可扩展方向

- 优惠券/促销码支持
- 邮件通知（续费成功/失败提醒）
- 下载次数配额限制（当前仅限制 AI 分析次数）
- 多语言 / 国际化支持
