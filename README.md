# CrimeJournal

AI 驱动的法律案例研究平台，基于 FastAPI + React 构建。

## 环境准备

### 前置依赖

- Python 3.10+
- Node.js 18+
- npm 或 pnpm

### 安装依赖

**后端**
```bash
cd backend
pip install -r requirements.txt
```

**前端**
```bash
cd frontend
npm install
```

## 启动开发服务器

### 后端

```bash
cd backend
python -m app.main
```

服务地址：http://localhost:8000
API 文档：http://localhost:8000/docs

### 前端

```bash
cd frontend
npm run dev
```

服务地址：http://localhost:5173（或终端显示的端口）

> 前端已配置 `/api` 代理到 `http://localhost:8000`，无需额外配置。

## 关闭服务器

- 在运行终端按 `Ctrl+C`
- 或通过任务管理器结束进程

## 环境变量配置

后端根目录下的 `.env` 文件：

```bash
# MiniMax AI（总结、实体提取、关键词）
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=MiniMax-M2.7

# DeepSeek AI（翻译、格式整理）
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# CourtListener 法律数据库
COURTLISTENER_API_TOKEN=your_courtlistener_token

# 数据库
DATABASE_URL=sqlite:///./crimejournal.db

# Redis（可选，开发环境自动降级到内存）
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your_secret_key_at_least_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

## 运行测试

```bash
cd backend
pytest                          # 全部测试
pytest tests/test_auth.py       # 单文件
pytest -v --cov=app --cov-report=term-missing  # 带覆盖率
```

## 项目结构

```
CrimeJournal/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由（认证、案例、搜索、订阅）
│   │   ├── services/     # 服务层
│   │   │   └── ai/       # AI 服务（MiniMax、DeepSeek、路由器）
│   │   ├── middleware/    # 中间件（用量限制、审计）
│   │   └── main.py       # FastAPI 入口
│   └── tests/            # 测试文件
└── frontend/
    ├── src/
    │   ├── pages/         # 页面组件
    │   ├── lib/          # 工具（API、认证、i18n、主题）
    │   └── App.tsx       # 路由配置
    └── vite.config.ts     # Vite 配置（含 API 代理）
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React, TypeScript, Vite, Tailwind CSS |
| 后端 | FastAPI, SQLAlchemy, Pydantic |
| AI | MiniMax M2.7（总结/实体）、DeepSeek V3.2（翻译/格式） |
| 数据源 | CourtListener API v3/v4 |
| 数据库 | SQLite（开发） |
