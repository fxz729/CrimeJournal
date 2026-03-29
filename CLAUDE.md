# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

CrimeJournal — AI驱动的法律案例研究平台，基于 FastAPI + React 构建。

## 开发命令

### Backend (Python/FastAPI)

```bash
cd backend

# 安装依赖（使用 venv）
pip install -r requirements.txt
# 或可编辑模式
pip install -e .

# 运行开发服务器
python -m app.main
# 或
uvicorn app.main:app --reload --port 8000

# 测试
pytest                          # 全部
pytest tests/test_auth.py        # 单文件
pytest -v --cov=app --cov-report=term-missing  # 带覆盖率
```

### Frontend (React/TypeScript/Vite)

```bash
cd frontend

# 安装依赖
npm install

# 开发（API代理到 localhost:8000）
npm run dev

# 构建（TypeScript 检查 + Vite 构建）
npm run build

# 预览构建结果
npm run preview

# ESLint
npm run lint
```

## 架构要点

### 服务依赖注入（重要）

所有服务（CourtListener、AI路由、缓存）通过 FastAPI `Depends()` 注入，不得在函数体内调用模块级函数获取服务实例：

```python
# ✅ 正确：使用 Depends() 注入
async def search_cases(
    request: Request,
    courtlistener: CourtListenerClient = Depends(get_courtlistener)
):
    result = await courtlistener.search_opinions(...)

# ❌ 错误：在函数体内调用模块级获取函数
async def search_cases(...):
    client = await get_courtlistener(request)  # 不允许
```

测试时使用 `app.dependency_overrides` 而非 `patch()` 覆盖：

```python
from app.api.cases import get_courtlistener, get_ai_router, get_cache
_app.dependency_overrides[get_courtlistener] = AsyncMock(return_value=mock_client)
```

### 前端 Provider 嵌套顺序

`frontend/src/main.tsx` 中的 Provider 从外到内：

```
QueryClientProvider
  -> BrowserRouter
    -> AuthProvider          # JWT token 验证
      -> I18nProvider        # 语言切换 (en/zh)
        -> ThemeProvider      # 主题切换 (light/dark/system)
          -> App
```

### i18n 实现

- 翻译存储在 `frontend/src/lib/i18n.tsx`，扁平化字符串 key（例：`'nav.home'`, `'search.title'`）
- 英文为默认语言，中文为第二语言
- 语言偏好存储在 `localStorage.language`
- 页面中通过 `const { t, language, setLanguage } = useI18n()` 使用
- 日期格式化应使用 `language` 变量选择 `zh-CN` 或 `en-US`
- **所有页面可见文本必须使用 `t()`，不得硬编码英文字符串**

### 主题/CSS 变量系统

`frontend/src/index.css` 定义 CSS 变量，`.dark` 类切换 dark 模式：

- `--bg-primary/secondary/tertiary` — 背景
- `--text-primary/secondary/tertiary` — 文本
- `--brand-primary` (#3b82f6 蓝), `--brand-accent` (#10b981 绿)
- `--border-default/subtle/focus`
- `--shadow-xs/md/lg/xl`
- `--transition-fast/base/slow` (150/200/300ms)

Tailwind 组件中通过 `var(--xxx)` 引用。

### API 代理配置

开发环境：`vite.config.ts` 配置 `/api` 代理到 `http://localhost:8000`。
生产环境：Vite proxy 不存在，需配置 Nginx/Caddy 等反向代理。

### Auth 流程

1. 登录成功后将 JWT token 存入 `localStorage.token`
2. Axios 请求拦截器自动注入 `Authorization: Bearer {token}`
3. 401 响应时，公开路径（`/cases/search`, `/cases/`, `/cases/shared/`, `/search/favorites/check/`）不触发重定向
4. `AuthProvider` 启动时检查 token 有效性

### 搜索数据流

```
Search.tsx -> casesApi.search()
  -> GET /api/cases/search?q=...&page=...&court=...
  -> cases.py: search_cases() -> CourtListenerClient.search_opinions()
  -> GET https://www.courtlistener.com/api/rest/v3/search/...
  -> SearchResponse { total, page, total_pages, results }
  -> React Query 缓存 -> 渲染
```

### AI 服务

统一使用 **MiniMax**（M2.7 模型），通过 `AIRouter`（`app/services/ai/router.py`）路由：
- `summarize_case()` — 案例摘要
- `extract_entities()` — 实体提取
- `extract_keywords()` — 关键词提取
- `translate_case()` — 翻译
- `format_text()` — 文本格式化

### 中间件

注册顺序（CORS -> UsageLimit -> Audit）：
- `UsageLimitMiddleware` — 每日搜索次数限制（Free 10次/天，Pro无限制）
- `AuditMiddleware` — API 操作审计日志

### 数据层

- **SQLite** — 用户数据（SQLAlchemy ORM，`DBUser` 模型），审计日志（独立 `AuditLog` 模型）
- **内存字典** — `FAKE_SEARCH_HISTORY`、`FAKE_FAVORITES`（`app/api/search.py`）
- **Redis/CacheService** — 缓存 AI 分析结果，失败时优雅降级到内存模式
- 用量数据（`daily_search_count`, `last_search_date`）存储在 SQLite `users` 表

### 测试要点

Mock 服务定义在 `tests/conftest.py`：
- `MockCourtListenerClient` — 模拟 CourtListener API
- `MockAIService` — 模拟 MiniMax AI
- `MockCacheService` — 模拟 Redis 缓存

关键 fixtures：
- `clear_fake_db`（autouse）自动清理内存状态
- `reset_global_services`（autouse）重置 `app.state` 中的服务实例

## 关键文件

### Backend
- `backend/app/main.py` — FastAPI 应用入口，lifespan 管理（初始化/关闭）、中间件注册
- `backend/app/config.py` — 配置（`settings` 单例，pydantic-settings）
- `backend/app/api/cases.py` — 案例搜索、详情、AI 分析端点
- `backend/app/api/auth.py` — 认证（JWT）+ SQLAlchemy `DBUser` 模型
- `backend/app/api/search.py` — 搜索历史、收藏（内存字典）
- `backend/app/api/subscriptions.py` — 订阅管理（Stripe 占位符）
- `backend/app/services/courtlistener.py` — CourtListener API v3/v4 客户端
- `backend/app/services/cache.py` — Redis 缓存（优雅降级）
- `backend/app/services/ai/router.py` — AI 服务路由
- `backend/app/services/ai/minimax.py` — MiniMax 实现
- `backend/app/middleware/usage.py` — 用量限制
- `backend/app/middleware/audit.py` — 审计日志
- `backend/tests/conftest.py` — 测试 fixtures 和 mock 服务

### Frontend
- `frontend/src/main.tsx` — 入口，Provider 嵌套
- `frontend/src/App.tsx` — 路由配置（React Router）
- `frontend/src/lib/api.ts` — Axios 客户端（请求/响应拦截器）
- `frontend/src/lib/auth.tsx` — AuthContext（JWT token 管理）
- `frontend/src/lib/i18n.tsx` — i18n Context + 翻译字典（525+ key）
- `frontend/src/lib/ThemeContext.tsx` — ThemeContext（light/dark/system）
- `frontend/src/pages/Search.tsx` — 搜索页（主要功能）
- `frontend/src/pages/LandingV2.tsx` — 首页/落地页
- `frontend/src/pages/CaseDetail.tsx` — 案例详情
- `frontend/vite.config.ts` — Vite 配置（含 PWA 和 API 代理）

## 敏感信息

`.env` 和 `*.db` 已被 `.gitignore` 忽略。配置通过 `pydantic_settings.BaseSettings` 从 `.env` 加载。
