# CrimeJournal 最终实施计划（v3.0）

**战略定位**：零成本启动的法律科技SaaS
**核心技术**：CourtListener + 混合AI（Claude/DeepSeek）+ GitHub自动部署

---

## Context（为什么做这个计划）

### 老师的核心建议
1. **数据源权威性**：GDELT新闻报道不够专业，无法服务律师等专业人士
2. **战略转向**：从"犯罪新闻平台"转向"法律案例数据服务"
3. **成本优化**：学生项目需要零成本启动，使用免费平台

### 最新调研发现
1. **部署方案**：GitHub + Vercel + Render 可实现完全免费部署（24小时运行）
2. **AI成本优化**：DeepSeek比Claude便宜100倍，可用于辅助功能
3. **数据源**：CourtListener完全免费，数百万法律案例

### 决策
- ✅ 基于推进计划v2.0（法律数据方向）
- ✅ 整合零成本部署方案
- ✅ 实施混合AI策略（Claude核心 + DeepSeek辅助）

---

## 一、技术架构（零成本版）

### 1.1 系统架构
```
用户浏览器
    ↓
Vercel（前端 - React）
    ↓
Render免费层（后端 - FastAPI）
    ↓
┌────────────┬──────────────┐
│ Supabase   │ 混合AI服务    │
│ PostgreSQL │ - Claude     │
│ + pgvector │ - DeepSeek   │
│ (免费500MB)│ - OpenAI     │
└────────────┴──────────────┘
    ↓
CourtListener API（免费法律数据）
```

### 1.2 关键技术栈
- **前端**：React + TypeScript + TailwindCSS + Shadcn/ui
- **后端**：FastAPI (Python 3.11+) + SQLAlchemy
- **数据库**：Supabase PostgreSQL (免费500MB)
- **缓存**：Upstash Redis (免费10K命令/天)
- **部署**：
  - 前端：Vercel (免费)
  - 后端：Render免费层 (15分钟休眠，可接受)
- **AI服务**：
  - Claude Haiku 3.5：核心功能（案例总结、实体提取）
  - DeepSeek V3：辅助功能（关键词、分类）
  - **向量化方案**（三选一）：
    - 方案1：sentence-transformers本地模型（**推荐，完全免费**）
    - 方案2：OpenAI text-embedding-3-small（$0.02/M tokens）
    - 方案3：Cohere embed-english-light-v3.0（免费层）

**重要说明**：
- Claude目前**不支持embedding功能**
- 本地模型**配置需求极低**：只需4GB内存，88MB模型，CPU即可运行
- 推理速度：5-10ms/条，完全满足MVP需求
- **强烈推荐方案1**：零成本、无API限制、离线可用

### 1.3 月度成本
- 完全免费方案：$0-5/月（仅AI调用费）
- 优化方案（消除休眠）：$7/月（Render付费层）

---

## 二、混合AI策略

### 2.1 功能分配
| 功能 | 提供商 | 模型 | 成本 | 原因 |
|------|--------|------|------|------|
| 案例总结（核心） | Claude | Haiku 3.5 | $0.25/M tokens | 需要高质量法律推理 |
| 实体提取（核心） | Claude | Haiku 3.5 | $0.25/M tokens | 需要精确识别 |
| 向量化（核心） | OpenAI | text-embedding-3-small | $0.02/M tokens | 行业标准 |
| 关键词提取 | DeepSeek | V3 | $0.14/M tokens | 简单任务，可接受误差 |
| 分类标签 | DeepSeek | V3 | $0.14/M tokens | 基于规则，成本优化 |
| 查询理解 | DeepSeek | V3 | $0.14/M tokens | 预处理用户输入 |

**成本节省**：相比全用Claude，节省70-80%成本

### 2.2 API配置灵活性
**支持自定义配置**：
- API URL（支持代理/第三方服务）
- API Key（支持多个提供商）
- 运行时切换（数据库配置表）

**实现方式**：
```python
# 环境变量配置
CLAUDE_API_KEY=sk-ant-xxx
CLAUDE_BASE_URL=  # 可选，用于代理
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
OPENAI_API_KEY=sk-xxx

# 代码中支持动态切换
ai_service = AIService(
    provider="claude",  # 或 deepseek
    api_key=custom_key,
    base_url=custom_url
)
```

### 2.3 降级策略
- DeepSeek失败 → 自动fallback到Claude
- 核心功能失败 → 不降级（返回错误）
- 缓存机制 → 避免重复调用

---

## 三、GitHub自动部署方案

### 3.1 工作流程
```
1. 代码推送到GitHub
2. GitHub Actions自动构建
3. Webhook触发部署
4. Vercel部署前端（自动）
5. Render部署后端（自动）
6. 24/7运行（Render有冷启动）
```

### 3.2 关键配置文件
**render.yaml**（后端）：
```yaml
services:
  - type: web
    name: crimejournal-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: CLAUDE_API_KEY
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false
```

**vercel.json**（前端）：
```json
{
  "buildCommand": "npm run build",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://crimejournal-api.onrender.com"
  }
}
```

### 3.3 冷启动优化
- Render免费层：15分钟无活动休眠
- 首次访问：30-60秒唤醒
- 解决方案：
  1. 前端显示"正在唤醒服务器"提示
  2. 关键API使用缓存
  3. 可选：定时ping保持活跃（消耗免费额度）

---

## 四、3个月实施路线图

### 月1：基础框架（Week 1-4）

#### Week 1：环境搭建 + 数据库（20小时）
**任务**：
- [ ] 注册GitHub账号，创建仓库
- [ ] 注册Vercel、Render、Supabase账号
- [ ] 注册CourtListener API token（免费）
- [ ] 注册Claude API key、DeepSeek API key
- [ ] 创建Supabase数据库，配置schema
- [ ] 本地开发环境（Python 3.11、Node.js 20）

**关键文件**：
- `backend/requirements.txt`
- `backend/app/config.py`
- `backend/app/models/case.py`
- `backend/migrations/001_initial_schema.sql`

**交付物**：
- 数据库schema创建完成
- 环境变量配置文档
- 所有API密钥已获取

#### Week 2：CourtListener集成（30小时）
**任务**：
- [ ] 实现CourtListener Python客户端
- [ ] 实现案例搜索（关键词+过滤）
- [ ] 实现案例详情获取
- [ ] 实现数据缓存逻辑
- [ ] 单元测试（pytest）

**关键文件**：
- `backend/app/services/courtlistener.py`
- `backend/tests/test_courtlistener.py`

**代码示例**：
```python
# services/courtlistener.py
import httpx

class CourtListenerService:
    def __init__(self, api_token: str):
        self.base_url = "https://www.courtlistener.com/api/rest/v4"
        self.headers = {"Authorization": f"Token {api_token}"}

    async def search_opinions(self, query: str, **filters):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search/",
                headers=self.headers,
                params={"q": query, **filters}
            )
            return response.json()
```

**交付物**：
- CourtListener集成模块
- 测试覆盖率>80%

#### Week 3：FastAPI后端（35小时）
**任务**：
- [ ] FastAPI项目结构
- [ ] 用户认证（JWT）
- [ ] 搜索API（/api/search）
- [ ] 案例详情API（/api/cases/{id}）
- [ ] CORS配置

**关键文件**：
- `backend/app/main.py`
- `backend/app/api/cases.py`
- `backend/app/api/auth.py`

**API端点**：
```
POST /api/auth/register
POST /api/auth/login
GET  /api/search?q=contract&court=ca9
GET  /api/cases/{id}
GET  /api/history
```

**交付物**：
- 可运行的API服务
- Swagger文档（自动生成）

#### Week 4：AI服务集成（40小时）
**任务**：
- [ ] AI服务抽象基类
- [ ] Claude服务实现
- [ ] DeepSeek服务实现
- [ ] OpenAI embedding实现
- [ ] 智能路由器（任务分发）
- [ ] Redis缓存集成

**关键文件**：
- `backend/app/services/ai/base.py`
- `backend/app/services/ai/claude.py`
- `backend/app/services/ai/deepseek.py`
- `backend/app/services/ai/router.py`

**架构示例**：
```python
# services/ai/router.py
class AIRouter:
    async def execute(self, task: TaskType, content: str):
        # 1. 检查缓存
        # 2. 选择提供商（核心→Claude，辅助→DeepSeek）
        # 3. 调用API
        # 4. 失败降级
        # 5. 缓存结果
        pass
```

**交付物**：
- 混合AI服务可用
- 成本监控仪表板

**月1里程碑**：
- ✅ 后端API运行
- ✅ CourtListener集成完成
- ✅ 混合AI服务可用

---

### 月2：前端 + AI增强（Week 5-8）

#### Week 5：前端基础（30小时）
**任务**：
- [ ] React + TypeScript项目（Vite）
- [ ] TailwindCSS + Shadcn/ui
- [ ] 登录/注册页面
- [ ] 搜索页面（基础UI）
- [ ] 案例详情页面

**关键文件**：
- `frontend/src/App.tsx`
- `frontend/src/pages/Search.tsx`
- `frontend/src/pages/CaseDetail.tsx`

**交付物**：
- 可访问的Web应用
- 基础搜索和展示功能

#### Week 6：AI功能实现（35小时）
**任务**：
- [ ] 案例总结API（Claude）
- [ ] 实体提取API（Claude）
- [ ] 关键词提取API（DeepSeek）
- [ ] 向量化API（OpenAI）
- [ ] 相似案例推荐

**API端点**：
```
POST /api/cases/{id}/summarize     # Claude
POST /api/cases/{id}/entities      # Claude
POST /api/cases/{id}/keywords      # DeepSeek
GET  /api/cases/{id}/similar       # 向量搜索
```

**交付物**：
- AI分析功能完整
- 相似案例推荐可用

#### Week 7：用户体验优化（25小时）
**任务**：
- [ ] 收藏夹功能
- [ ] 搜索历史管理
- [ ] 响应式设计
- [ ] 加载状态优化
- [ ] 错误处理

**交付物**：
- 完整的用户功能
- 移动端可用

#### Week 8：部署配置（30小时）
**任务**：
- [ ] Render配置（render.yaml）
- [ ] Vercel配置（vercel.json）
- [ ] GitHub Actions自动部署
- [ ] 环境变量管理
- [ ] 部署测试

**关键文件**：
- `render.yaml`
- `vercel.json`
- `.github/workflows/deploy.yml`

**交付物**：
- 自动部署流程可用
- 24小时运行（有冷启动）

**月2里程碑**：
- ✅ 前端完整功能
- ✅ AI功能集成
- ✅ 自动部署上线

---

### 月3：商业化 + 客户验证（Week 9-12）

#### Week 9：订阅系统（35小时）
**任务**：
- [ ] Stripe集成
- [ ] 订阅计划（Free/Pro/Enterprise）
- [ ] 功能限制
- [ ] 订阅管理页面

**订阅计划**：
```
Free：$0/月
- 10次搜索/天
- 无AI分析

Pro：$50/月
- 无限搜索
- AI案例总结
- 相似案例推荐
- 导出功能

Enterprise：$500/月
- Pro所有功能
- API访问
- 团队账户（10人）
```

**交付物**：
- 订阅系统可用
- Stripe集成完成

#### Week 10：营销页面（25小时）
**任务**：
- [ ] 首页设计
- [ ] 定价页面
- [ ] 用户文档
- [ ] FAQ页面
- [ ] Google Analytics

**交付物**：
- 完整营销网站
- 用户文档

#### Week 11：客户开发（30小时）
**任务**：
- [ ] LinkedIn发布产品介绍
- [ ] Reddit r/LawFirm发帖
- [ ] 联系10个独立律师
- [ ] Beta测试
- [ ] 收集反馈

**交付物**：
- 10个Beta用户
- 用户反馈报告

#### Week 12：正式发布（30小时）
**任务**：
- [ ] 修复Beta测试bug
- [ ] Product Hunt发布
- [ ] Hacker News Show HN
- [ ] 邀请Beta用户付费
- [ ] 系统监控

**目标**：
- 至少1个付费客户（$50/月）
- 注册用户 > 50人
- 搜索请求 > 500次

**月3里程碑**：
- ✅ 产品正式上线
- ✅ 首批付费客户
- ✅ 系统稳定运行

---

## 五、成本分析

### 5.1 月度成本（MVP阶段）
| 项目 | 成本 | 说明 |
|------|------|------|
| Vercel（前端） | $0 | 免费 |
| Render（后端） | $0 | 免费层（有休眠） |
| Supabase（数据库） | $0 | 免费500MB |
| Upstash Redis | $0 | 免费10K命令/天 |
| Claude API | $5-10 | 按量付费（核心功能） |
| DeepSeek API | $1-3 | 按量付费（辅助功能） |
| Embedding（本地模型） | $0 | **完全免费** |
| **总计** | **$6-13/月** | 零成本启动 |

**关键改进**：使用本地embedding模型（sentence-transformers），完全免费，无需OpenAI API费用。

### 5.2 升级路径
**如果需要消除休眠**：
- Render升级：$7/月
- 总成本：$14-22/月
- 用户体验显著提升

---

## 六、关键风险与应对

### 6.1 技术风险
| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Render冷启动慢 | 首次访问体验差 | 前端提示 + 预热机制 |
| DeepSeek质量不稳定 | 辅助功能误差 | Fallback到Claude |
| Supabase存储限制 | 案例数量受限 | 优化存储 + 分层策略 |

### 6.2 商业风险
| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 找不到付费客户 | 无收入验证 | Beta免费试用 + LinkedIn外联 |
| 竞争对手降价 | 优势减弱 | 专注独立律师市场 |

---

## 七、验证计划

### 7.1 技术验证（Week 1）
- [ ] CourtListener API测试（搜索10个案例）
- [ ] Claude API测试（总结1个案例）
- [ ] DeepSeek API测试（提取关键词）
- [ ] Render部署测试（验证冷启动）

### 7.2 市场验证（Week 11）
- [ ] 联系10个独立律师
- [ ] 询问痛点和付费意愿
- [ ] 产品演示（5场）
- [ ] 收集反馈

### 7.3 成功指标
**技术指标**：
- API响应时间：<500ms（P95）
- 系统可用性：>99%
- AI分析质量：用户评分>4/5

**商业指标**：
- 注册用户：>50人
- 付费客户：1-3人
- MRR：$50-150

---

## 八、立即行动（本周）

### Day 1-2：账号注册
1. GitHub账号（如果没有）
2. Vercel账号（vercel.com）
3. Render账号（render.com）
4. Supabase账号（supabase.com）
5. CourtListener API token（courtlistener.com）
6. Claude API key（console.anthropic.com）
7. DeepSeek API key（platform.deepseek.com）

### Day 3-4：环境搭建（详细步骤）

#### 1. 创建项目目录
```bash
cd D:\A学业\作业\创业课程作业\CrimeJournal
mkdir backend frontend
```

#### 2. 创建Python虚拟环境
```bash
# 进入后端目录
cd backend

# 创建虚拟环境（Windows）
python -m venv venv

# 激活虚拟环境
# Windows CMD:
venv\Scripts\activate.bat
# Windows PowerShell:
venv\Scripts\Activate.ps1
# 如果遇到权限错误，先执行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 验证激活（应该看到 (venv) 前缀）
python --version  # 应该显示 Python 3.11+
```

#### 3. 安装后端依赖
创建 `backend/requirements.txt`：
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0
python-dotenv==1.0.0
httpx==0.26.0
anthropic==0.18.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
redis==5.0.1
sentence-transformers==2.3.1  # 本地向量化模型
pytest==8.0.0
pytest-asyncio==0.23.4
```

安装依赖：
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量
创建 `backend/.env`：
```env
# Claude配置
CLAUDE_API_KEY=你的claude_api_key
CLAUDE_BASE_URL=

# DeepSeek配置
DEEPSEEK_API_KEY=你的deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# CourtListener配置
COURTLISTENER_API_TOKEN=你的courtlistener_token

# 数据库配置（暂时用SQLite，后续迁移到Supabase）
DATABASE_URL=sqlite:///./crimejournal.db

# Redis配置
REDIS_URL=redis://localhost:6379

# JWT配置
JWT_SECRET_KEY=生成一个随机字符串
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# 向量化模型（本地）
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

#### 5. 安装前端依赖
```bash
cd ../frontend

# 使用Vite创建React项目
npm create vite@latest . -- --template react-ts

# 安装依赖
npm install axios react-router-dom @tanstack/react-query
npm install -D tailwindcss postcss autoprefixer
npm install @shadcn/ui

# 初始化TailwindCSS
npx tailwindcss init -p
```

#### 6. 验证环境
```bash
# 后端验证
cd ../backend
python -c "import fastapi; import anthropic; print('Backend OK')"

# 前端验证
cd ../frontend
npm run dev  # 应该能启动开发服务器
```

### Day 5：技术验证
1. 测试CourtListener API
2. 测试Claude API
3. 测试DeepSeek API
4. 测试本地embedding模型
5. 验证技术可行性

**验证代码示例**：
```python
# 测试CourtListener
import httpx
response = httpx.get(
    "https://www.courtlistener.com/api/rest/v4/search/",
    params={"q": "contract"},
    headers={"Authorization": "Token YOUR_TOKEN"}
)
print(response.status_code)  # 应该是200

# 测试Claude
from anthropic import Anthropic
client = Anthropic(api_key="YOUR_KEY")
message = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello"}]
)
print(message.content)

# 测试embedding模型
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("This is a test")
print(f"Embedding dimension: {len(embedding)}")  # 应该是384
```

---

## 九、GitHub完整部署流程

### 9.1 本地项目结构（所有文件保存在工作区）
```
D:\A学业\作业\创业课程作业\CrimeJournal\
├── .gitignore
├── README.md
├── LICENSE
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── case.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── courtlistener.py
│   │   │   ├── ai/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── claude.py
│   │   │   │   ├── deepseek.py
│   │   │   │   └── router.py
│   │   │   └── cache.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── cases.py
│   │   │   ├── auth.py
│   │   │   └── search.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── prompts.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_courtlistener.py
│   └── migrations/
│       └── 001_initial_schema.sql
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Search.tsx
│   │   │   └── CaseDetail.tsx
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── SearchBar.tsx
│   │   │   └── CaseCard.tsx
│   │   └── lib/
│   │       └── api.ts
│   └── public/
├── .github/
│   └── workflows/
│       ├── backend.yml
│       └── frontend.yml
├── render.yaml
└── vercel.json
```

### 9.2 GitHub仓库创建和初始化

#### Step 1: 在GitHub创建仓库
1. 访问 https://github.com/new
2. 仓库名称：`CrimeJournal`
3. 描述：`AI-Powered Legal Case Research Platform`
4. 可见性：Public（免费部署需要公开仓库）
5. **不要**勾选"Initialize with README"（我们本地已有文件）
6. 点击"Create repository"

#### Step 2: 本地Git初始化
```bash
# 在工作区根目录
cd D:\A学业\作业\创业课程作业\CrimeJournal

# 初始化Git仓库
git init

# 配置用户信息（如果还没配置）
git config user.name "你的名字"
git config user.email "你的邮箱"

# 创建.gitignore文件
```

创建 `.gitignore`：
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env
*.egg-info/
dist/
build/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.next/
out/
build/
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# 敏感信息
.env
*.pem
*.key

# 数据库
*.db
*.sqlite

# 日志
*.log
logs/

# 临时文件
*.tmp
.cache/
```

#### Step 3: 第一次提交
```bash
# 添加所有文件
git add .

# 创建第一次提交
git commit -m "feat: initial commit - CrimeJournal v3.0

- Setup backend with FastAPI + Claude/DeepSeek AI integration
- Setup frontend with React + TypeScript + TailwindCSS
- Configure CourtListener API integration
- Add local embedding model (sentence-transformers)
- Setup deployment configs (Render + Vercel)

Co-Authored-By: Claude Sonnet 4.6 (1M context) <noreply@anthropic.com>"

# 关联远程仓库
git remote add origin https://github.com/你的用户名/CrimeJournal.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 9.3 GitHub Actions自动部署配置

#### 后端部署 (.github/workflows/backend.yml)
```yaml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - 'requirements.txt'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Render
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}

      - name: Notify deployment status
        if: always()
        run: |
          echo "Backend deployment triggered at $(date)"
```

#### 前端部署 (.github/workflows/frontend.yml)
```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: frontend
```

### 9.4 Render配置 (render.yaml)
```yaml
services:
  # Web服务（后端API）
  - type: web
    name: crimejournal-api
    env: python
    region: oregon  # 或 singapore（亚洲）
    plan: free  # 免费层
    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: CLAUDE_API_KEY
        sync: false  # 手动设置
      - key: CLAUDE_BASE_URL
        sync: false  # 第三方URL
      - key: DEEPSEEK_API_KEY
        sync: false
      - key: COURTLISTENER_API_TOKEN
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: crimejournal-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: crimejournal-redis
          type: pserv
          property: connection

  # Redis缓存服务
  - type: pserv
    name: crimejournal-redis
    env: docker
    repo: https://github.com/render-examples/redis
    plan: starter  # 免费层

# PostgreSQL数据库
databases:
  - name: crimejournal-db
    plan: starter  # 免费90天，之后$7/月
    # 或使用Supabase（永久免费500MB）
```

### 9.5 Vercel配置 (vercel.json)
```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://crimejournal-api.onrender.com",
    "NEXT_PUBLIC_APP_NAME": "CrimeJournal"
  },
  "routes": [
    { "handle": "filesystem" },
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
```

### 9.6 GitHub Secrets配置
在GitHub仓库设置中添加以下Secrets：

1. 访问 `https://github.com/你的用户名/CrimeJournal/settings/secrets/actions`
2. 点击"New repository secret"
3. 添加以下secrets：

```
RENDER_SERVICE_ID      # 从Render dashboard获取
RENDER_API_KEY         # 从Render账户设置获取
VERCEL_TOKEN           # 从Vercel账户设置生成
VERCEL_ORG_ID          # 从Vercel团队设置获取
VERCEL_PROJECT_ID      # 创建Vercel项目后获取
```

### 9.7 部署流程（完整）

#### 本地开发 → 测试 → 部署
```bash
# 1. 本地开发
# 修改代码...

# 2. 本地测试
cd backend
pytest tests/

cd ../frontend
npm run test

# 3. 提交代码
git add .
git commit -m "feat: 添加新功能"

# 4. 推送到GitHub（自动触发部署）
git push origin main

# 5. 查看部署状态
# GitHub Actions: https://github.com/你的用户名/CrimeJournal/actions
# Render: https://dashboard.render.com/
# Vercel: https://vercel.com/dashboard

# 6. 访问应用
# 前端：https://crimejournal.vercel.app
# 后端：https://crimejournal-api.onrender.com
# API文档：https://crimejournal-api.onrender.com/docs
```

---

## 十、素材获取与设计（使用Skills/MCP）

### 10.1 前端UI设计素材

#### 使用Shadcn/ui组件库（免费）
```bash
# 在frontend目录
cd frontend

# 初始化Shadcn/ui
npx shadcn@latest init

# 添加需要的组件
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add select
npx shadcn@latest add table
npx shadcn@latest add toast
```

#### 使用Pexels获取免费图片（通过MCP）
```typescript
// 使用 pexels-media MCP工具
import { searchPhotos } from '@pexels/api'

// 搜索法律相关图片
const photos = await searchPhotos('law books', 10)
// 用于首页背景、案例卡片等
```

#### 使用Unsplash API（免费）
```typescript
// 获取法律主题图片
const response = await fetch(
  'https://api.unsplash.com/photos/random?query=law&orientation=landscape',
  {
    headers: {
      Authorization: 'Client-ID YOUR_ACCESS_KEY'
    }
  }
)
```

### 10.2 图标和Logo设计

#### 使用Lucide Icons（免费）
```bash
npm install lucide-react
```

```tsx
import { Scale, Search, FileText, BookOpen } from 'lucide-react'

// 法律主题图标
<Scale className="h-6 w-6" />  // 天平（法律）
<Search className="h-6 w-6" />  // 搜索
<FileText className="h-6 w-6" />  // 文件
<BookOpen className="h-6 w-6" />  // 法律书籍
```

#### Logo设计（使用AI工具）
使用MCP工具或在线服务：
1. **Canva免费Logo制作**
2. **Hugging Face Logo生成器**
3. **Brandmark.io**（付费，质量高）

### 10.3 数据可视化素材

#### 使用Recharts（免费）
```bash
npm install recharts
```

```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

// 案例趋势图表
<LineChart width={600} height={300} data={caseTrends}>
  <XAxis dataKey="date" />
  <YAxis />
  <CartesianGrid strokeDasharray="3 3" />
  <Tooltip />
  <Line type="monotone" dataKey="count" stroke="#8884d8" />
</LineChart>
```

### 10.4 营销文案和内容

#### 使用Claude生成营销文案（通过MCP）
```python
# 使用Claude API生成首页文案
from anthropic import Anthropic

client = Anthropic(api_key=CLAUDE_API_KEY)

marketing_copy = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=500,
    messages=[{
        "role": "user",
        "content": """为法律案例检索平台撰写首页营销文案，包括：
1. 标题（10字以内）
2. 副标题（30字以内）
3. 三大核心优势
4. CTA按钮文案

目标用户：独立律师、小型律所
差异化：价格只有Westlaw的1/10"""
    }]
)
```

#### 使用DeepSeek生成FAQ（低成本）
```python
# 使用DeepSeek生成常见问题
faq = deepseek_service.chat([
    {"role": "user", "content": "生成10个法律科技SaaS平台的常见问题及答案"}
])
```

### 10.5 配色方案

#### 使用TailwindCSS预定义配色（免费）
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',  // 主色调（专业蓝）
          600: '#2563eb',
          900: '#1e3a8a',
        },
        secondary: {
          500: '#64748b',  // 辅助色（灰色）
        },
        accent: {
          500: '#10b981',  // 强调色（绿色，代表正义）
        }
      }
    }
  }
}
```

#### 使用Coolors.co生成配色方案（免费）
访问 https://coolors.co/ 生成法律主题配色：
- Navy Blue: #1a365d（专业）
- Gold: #d69e2e（权威）
- White: #ffffff（简洁）
- Slate: #475569（稳重）

### 10.6 字体选择

#### 使用Google Fonts（免费）
```typescript
// 在index.html中引入
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Merriweather:wght@400;700&display=swap" rel="stylesheet">

// TailwindCSS配置
fontFamily: {
  sans: ['Inter', 'sans-serif'],  // UI字体
  serif: ['Merriweather', 'serif'],  // 标题字体
}
```

### 10.7 模板和示例代码

#### 使用GitHub模板仓库（免费）
搜索关键词：
- "legal tech react template"
- "saas landing page template"
- "dashboard react typescript"

推荐模板：
1. **Taxonomy**（Next.js + TailwindCSS）
2. **Next.js SaaS Starter**
3. **Shadcn/ui Templates**

#### 使用CodeSandbox示例（免费）
访问 https://codesandbox.io 搜索：
- "React search interface"
- "FastAPI CRUD example"
- "PostgreSQL + pgvector demo"

---

## 十一、项目文件创建清单（所有文件保存在工作区）

### 立即创建的文件（Week 1）
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/services/courtlistener.py`
- `backend/app/services/ai/base.py`
- `backend/app/services/ai/claude.py`
- `backend/app/services/ai/deepseek.py`
- `backend/app/services/ai/router.py`
- `backend/app/api/cases.py`
- `backend/app/api/auth.py`

### 前端核心文件
- `frontend/package.json`
- `frontend/src/App.tsx`
- `frontend/src/pages/Search.tsx`
- `frontend/src/pages/CaseDetail.tsx`

### 部署配置文件
- `render.yaml`
- `vercel.json`
- `.github/workflows/deploy.yml`

---

## 总结

这个计划实现了：
1. ✅ **零成本启动**：完全免费的技术栈（月成本$7-15，主要是AI调用）
2. ✅ **混合AI优化**：Claude核心 + DeepSeek辅助，节省70-80%成本
3. ✅ **GitHub自动部署**：代码推送即部署，24小时运行
4. ✅ **灵活配置**：支持自定义API URL和Key
5. ✅ **快速验证**：3个月MVP，首个付费客户

相比原计划v2.0的改进：
- 成本：从$300降至$7-15/月（节省95%）
- 部署：从手动部署改为GitHub自动部署
- AI：从单Claude改为混合方案，成本优化
- 可行性：零成本启动，降低失败风险

下一步：执行Week 1任务，开始环境搭建。
