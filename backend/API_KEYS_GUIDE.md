# CrimeJournal API密钥配置指南

本文档指引你获取CrimeJournal所需的全部API密钥。

---

## 1. CourtListener API Token（免费）

**用途**：获取美国法院判例数据

**获取步骤**：
1. 访问 https://www.courtlistener.com/accounts/login/
2. 注册账号（免费）
3. 登录后访问 https://www.courtlistener.com/api/token/
4. 复制Token，格式如：`a1b2c3d4e5f6...`

---

## 2. Claude API Key（按量付费）

**用途**：AI案例总结、实体提取

**获取步骤**：
1. 访问 https://console.anthropic.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 点击 "Create Key"
5. 复制生成的Key，格式如：`sk-ant-api03-xxxxx`

**费用**：Haiku模型 $0.25/百万tokens，预计每月 $5-10

---

## 3. DeepSeek API Key（便宜）

**用途**：关键词提取、查询理解

**获取步骤**：
1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 点击 "Create API Key"
5. 复制生成的Key，格式如：`sk-xxxxxx`

**费用**：V3模型 $0.14/百万tokens，预计每月 $1-3

---

## 4. Supabase（可选，免费）

**用途**：生产环境PostgreSQL数据库

**获取步骤**：
1. 访问 https://supabase.com/
2. 点击 "Start your project"
3. 用GitHub登录
4. 创建新项目
5. 在 Settings > Database 中找到连接信息

**本地开发**：可使用SQLite，无需额外配置

---

## 5. Redis（可选）

**用途**：生产环境缓存

**本地开发**：可跳过，安装Redis可选

**免费方案**：
- Upstash Redis：https://upstash.com/（免费10K命令/天）

---

## 快速配置

复制 `.env.example` 为 `.env`：

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填入你的密钥：

```env
# ===== 必需 =====
CLAUDE_API_KEY=sk-ant-api03-你的Claude密钥
DEEPSEEK_API_KEY=sk-你的DeepSeek密钥
COURTLISTENER_API_TOKEN=你的CourtListener密钥

# ===== JWT密钥（随机生成） =====
JWT_SECRET_KEY=在终端运行: python -c "import secrets; print(secrets.token_hex(32))"

# ===== 可选（本地开发使用SQLite） =====
DATABASE_URL=sqlite:///./crimejournal.db
REDIS_URL=redis://localhost:6379

# ===== 模型（使用免费本地模型） =====
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## 验证配置

安装依赖后，测试配置是否正确：

```bash
cd backend
.\venv\Scripts\activate  # Windows
# 或 source venv/bin/activate  # Linux/Mac

python -c "
from app.config import settings
print('Claude:', '✓' if settings.claude_api_key else '✗')
print('DeepSeek:', '✓' if settings.deepseek_api_key else '✗')
print('CourtListener:', '✓' if settings.courtlistener_api_token else '✗')
"
```

---

## 下一步

1. 获取以上API密钥
2. 填入 `.env` 文件
3. 运行后端：`uvicorn app.main:app --reload`
4. 运行前端：`cd ../frontend && npm run dev`
