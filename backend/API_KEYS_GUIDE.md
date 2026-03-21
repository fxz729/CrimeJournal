# CrimeJournal API密钥配置指南

本文档指引你获取CrimeJournal所需的全部API密钥。

---

## 1. CourtListener API Token（免费）

**用途**：获取美国法院判例数据

**获取步骤**：
1. 访问 https://www.courtlistener.com/accounts/login/
2. 注册账号（免费）
3. 登录后访问 https://www.courtlistener.com/api/token/
4. 复制Token

---

## 2. MiniMax API Key（推荐）

**用途**：AI案例总结、实体提取

**获取步骤**：
1. 访问 https://platform.minimaxi.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 点击 "Create API Key"
5. 复制生成的Key

**费用**：价格实惠，国内直连

**模型**：`MiniMax-Text-01`

---

## 3. DeepSeek API Key（可选）

**用途**：关键词提取、查询理解（可选用MiniMax代替）

**获取步骤**：
1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 点击 "Create API Key"
5. 复制生成的Key

**费用**：V3模型 $0.14/百万tokens

---

## 快速配置

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填入你的密钥：

```env
# ===== MiniMax（主要AI服务）=====
MINIMAX_API_KEY=你的MiniMax密钥
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=MiniMax-Text-01

# ===== DeepSeek（可选）=====
DEEPSEEK_API_KEY=你的DeepSeek密钥

# ===== CourtListener ======
COURTLISTENER_API_TOKEN=你的CourtListener密钥

# ===== JWT密钥 ======
JWT_SECRET_KEY=在终端运行: python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 验证配置

```bash
cd backend
.\venv\Scripts\activate  # Windows

python -c "
from app.config import settings
print('MiniMax:', '✓' if settings.minimax_api_key else '✗')
print('DeepSeek:', '✓' if settings.deepseek_api_key else '✗')
print('CourtListener:', '✓' if settings.courtlistener_api_token else '✗')
"
```

---

## 下一步

1. 获取以上API密钥
2. 填入 `.env` 文件
3. 运行后端：`.\start.bat`
4. 运行前端：`cd ../frontend && npm run dev`
