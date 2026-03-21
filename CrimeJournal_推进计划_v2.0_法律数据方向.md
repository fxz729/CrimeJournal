# CrimeJournal 项目推进计划 v2.0

**重大战略转向：从新闻报道到法律文书数据服务**

制定日期：2026-03-20
版本：2.0（基于老师建议的重大调整）
目标：3个月MVP + 首个付费客户

---

## 🎯 执行摘要

### 老师的关键建议

**核心问题**：
- ❌ GDELT新闻报道数据源**权威性不足**
- ❌ 专业用户（律师、研究人员）为什么要为新闻报道付费？他们可以直接问ChatGPT
- ❌ 新闻报道无法满足专业人士的高要求

**两个战略选择**：

**选择1：服务普通大众**
- 数据源：新闻报道（GDELT）
- 优势：数据易获取、成本低
- 劣势：竞争激烈、付费意愿低、AI大模型竞争

**选择2：服务专业人士** ✅ **推荐**
- 数据源：法律文书、诉讼案例原文
- 优势：高付费意愿、高壁垒、差异化
- 劣势：数据获取难、合规要求高

### 最终决策：转向法律数据服务

**核心理由**：
1. **零成本启动**：CourtListener提供完全免费的法律API
2. **专业市场**：律师愿意为专业工具付费（$50-500/月）
3. **技术壁垒**：法律NLP、案例关联有门槛
4. **快速验证**：B2B市场，单客价值高，3个月可验证

---

## 📊 第一部分：市场分析与战略调整

### 1.1 为什么放弃新闻报道方向？

**致命缺陷**：
1. **权威性不足**：新闻报道是二手信息，非官方记录
2. **AI竞争**：用户可以直接问ChatGPT"北京朝阳区最近有什么犯罪？"
3. **覆盖不全**：媒体选择性报道，大量案件无新闻
4. **付费意愿低**：普通用户不愿为新闻聚合付费

**竞争对手已经很强**：
- Citizen：$100M+融资，实时推送
- Nextdoor：4100万月活，社区网络
- SpotCrime：免费地图展示

**我们的差异化在哪？**
- 仅仅"聚合展示"不够
- 无法与AI大模型竞争

### 1.2 为什么选择法律数据方向？

**市场机会**：
- Westlaw营收：$2B+/年
- LexisNexis营收：$1B+/年
- 律师愿意为专业工具付费：$300-3000/月

**关键发现：CourtListener免费API** 🎉
- **完全免费**：由非营利组织Free Law Project运营
- **数据规模**：数百万法律案例，470个司法管辖区
- **官方API**：REST API v4 + Python SDK
- **先进功能**：语义搜索、批量下载、Webhooks
- **即将支持**：Claude/ChatGPT的MCP服务器

**竞争优势**：
- 成本：$50-500/月 vs Westlaw $3000+/月
- 体验：现代Web界面 vs 90年代风格
- AI：内置智能分析 vs 需额外付费

### 1.3 目标客户重新定义

**一级目标（前3个月）**：
- **独立律师/小型律所（1-5人）**
  - 痛点：Westlaw太贵（$300-500/月/用户）
  - 预算：$50-200/月
  - 获客：LinkedIn、法律科技社区

**二级目标（3-6个月）**：
- **法学院学生/教授**
  - 痛点：学校数据库访问受限
  - 预算：$20-50/月（学生）、$100-300/月（教授）
  - 获客：法学院论坛、学术会议

**三级目标（6-12个月）**：
- **中型律所（10-50人）**
  - 痛点：需要团队协作功能
  - 预算：$1000-5000/月
  - 获客：直销、行业展会

---

## 🏗️ 第二部分：产品重新定位

### 2.1 新的核心价值主张

**一句话描述**：
"为独立律师和小型律所提供AI驱动的法律案例检索工具，价格只有Westlaw的1/10"

**三大支柱**：
1. **零数据成本**：基于CourtListener免费API
2. **AI增强**：Claude驱动的智能分析（案例总结、相似推荐）
3. **现代体验**：简洁UI + 语义搜索 vs 传统法律数据库

### 2.2 MVP功能（3个月）

**核心功能**：
1. **法律案例检索**
   - 关键词搜索（案件名称、法官、律师、法院）
   - 高级过滤（日期范围、法院层级、案件类型）
   - 语义搜索（CourtListener Semantic Search API）

2. **AI智能分析**
   - 案例自动总结（Claude API）
   - 关键法律实体提取（当事人、法官、律师、法条）
   - 相似案例推荐（基于向量相似度）

3. **用户管理**
   - 基础账户系统（注册/登录）
   - 搜索历史记录
   - 收藏夹功能

### 2.3 技术架构

**系统架构**：
```
前端：React + TypeScript + TailwindCSS
后端：FastAPI (Python 3.11+)
数据库：PostgreSQL 16 + pgvector（向量搜索）
AI层：Claude API (Sonnet 4)
外部API：CourtListener REST API v4
```

**数据库设计**：
```sql
-- 用户表
users (id, email, password_hash, subscription_tier, created_at)

-- 案例缓存表（减少API调用）
cases_cache (id, courtlistener_id, case_name, court, date_filed,
             opinion_text, judges, attorneys, embedding, metadata)

-- 搜索历史
search_history (id, user_id, query, filters, results_count, created_at)

-- 收藏夹
favorites (id, user_id, case_id, notes, created_at)

-- AI分析缓存（避免重复调用Claude）
ai_analysis_cache (id, case_id, analysis_type, result, created_at)
```

---

## 📅 第三部分：3个月实施计划

### 月1：基础设施 + CourtListener集成（Week 1-4）

**目标**：完成数据层和基础API，能够搜索和展示案例

#### Week 1：环境搭建 + 数据库设计（20小时）
- [ ] 创建项目仓库（GitHub）
- [ ] 配置开发环境（Python 3.11, Node.js 20, PostgreSQL 16）
- [ ] 实现数据库schema
- [ ] 注册CourtListener API token（免费）
- [ ] 注册Anthropic API key
- [ ] 配置环境变量管理

**交付物**：数据库迁移脚本、环境配置文档

#### Week 2：CourtListener API集成（30小时）
- [ ] 实现CourtListener Python客户端封装
- [ ] 实现案例搜索功能（关键词 + 过滤）
- [ ] 实现案例详情获取
- [ ] 实现数据缓存逻辑（避免重复API调用）
- [ ] 编写单元测试（pytest）

**关键代码示例**：
```python
from courtlistener import CourtListener

cl = CourtListener(api_token=COURTLISTENER_TOKEN)

# 搜索案例
results = cl.search.opinions.get(
    q="contract breach damages",
    court="ca9",
    filed_after="2020-01-01",
    order_by="-date_filed"
)
```

**交付物**：CourtListener集成模块、测试覆盖率>80%

#### Week 3：FastAPI后端开发（35小时）
- [ ] 搭建FastAPI项目结构
- [ ] 实现用户认证（JWT）
- [ ] 实现搜索API端点（/api/search）
- [ ] 实现案例详情API（/api/cases/{id}）
- [ ] 实现搜索历史API
- [ ] 配置CORS

**API端点设计**：
```python
POST /api/auth/register  # 用户注册
POST /api/auth/login     # 用户登录
GET  /api/search         # 搜索案例
GET  /api/cases/{id}     # 案例详情
GET  /api/history        # 搜索历史
```

**交付物**：可运行的API服务、Swagger文档

#### Week 4：前端基础框架（40小时）
- [ ] 创建React + TypeScript项目（Vite）
- [ ] 配置TailwindCSS + Shadcn/ui
- [ ] 实现登录/注册页面
- [ ] 实现搜索页面（基础UI）
- [ ] 实现案例详情页面
- [ ] 集成API调用（axios）

**页面结构**：
```
/              # 首页（营销页面）
/login         # 登录
/register      # 注册
/dashboard     # 用户仪表板
/search        # 搜索页面
/cases/:id     # 案例详情
```

**交付物**：可访问的Web应用、基础搜索和展示功能

**月1里程碑**：
- ✅ 用户可以注册、登录
- ✅ 用户可以搜索案例、查看详情
- ✅ 数据从CourtListener实时获取

---

### 月2：AI功能 + 用户体验优化（Week 5-8）

**目标**：集成Claude API，实现智能分析功能

#### Week 5：Claude API集成（30小时）
- [ ] 实现案例总结功能
- [ ] 实现法律实体提取
- [ ] 实现AI分析缓存（避免重复调用）
- [ ] 添加API成本监控（记录token使用量）
- [ ] 实现错误处理和重试逻辑

**AI功能示例**：
```python
import anthropic

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def summarize_case(opinion_text: str) -> dict:
    """生成案例摘要（200-300字）"""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""请总结以下法律案例，包括：
1. 案件背景（2-3句）
2. 核心法律问题
3. 法院判决及理由
4. 重要先例价值

案例全文：{opinion_text[:10000]}"""
        }]
    )
    return {"summary": response.content[0].text}
```

**交付物**：AI分析模块、成本监控仪表板

#### Week 6：向量搜索 + 相似案例推荐（35小时）
- [ ] 安装pgvector扩展
- [ ] 实现案例向量化（使用sentence-transformers）
- [ ] 批量处理已缓存案例的向量
- [ ] 实现相似案例推荐API
- [ ] 前端展示相似案例

**向量化流程**：
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> list:
    """生成文本向量"""
    return model.encode(text).tolist()

def find_similar_cases(case_embedding: list, top_k: int = 5):
    """使用pgvector查找相似案例"""
    query = """
    SELECT courtlistener_id, case_name, court, date_filed,
           1 - (embedding <=> %s::vector) AS similarity
    FROM cases_cache
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> %s::vector
    LIMIT %s
    """
    # 执行查询...
```

**交付物**：相似案例推荐功能、向量化脚本

#### Week 7：用户功能完善（25小时）
- [ ] 实现收藏夹功能
- [ ] 实现搜索历史管理
- [ ] 实现用户设置页面
- [ ] 添加搜索过滤器（法院、日期、案件类型）
- [ ] 优化搜索结果展示（分页、排序）

#### Week 8：UI/UX优化（30小时）
- [ ] 优化搜索页面布局
- [ ] 添加加载状态和骨架屏
- [ ] 实现响应式设计（移动端适配）
- [ ] 添加快捷键支持（Cmd+K搜索）
- [ ] 优化案例详情页排版
- [ ] 添加导出功能（PDF/Word）

**月2里程碑**：
- ✅ AI功能完整（总结、实体提取、相似推荐）
- ✅ 用户体验流畅
- ✅ 移动端可用

---

### 月3：商业化准备 + 客户验证（Week 9-12）

**目标**：完成订阅系统，获取首批付费客户

#### Week 9：订阅系统开发（35小时）
- [ ] 集成Stripe支付
- [ ] 实现订阅计划（Free/Pro/Enterprise）
- [ ] 实现功能限制（Free: 10次搜索/天，Pro: 无限）
- [ ] 实现订阅管理页面
- [ ] 添加发票生成功能

**订阅计划**：
```
Free：$0/月
- 10次搜索/天
- 基础案例查看
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
- 优先支持
```

**交付物**：可用的订阅系统、Stripe集成完成

#### Week 10：营销页面 + 文档（25小时）
- [ ] 设计首页（价值主张、功能展示）
- [ ] 创建定价页面
- [ ] 编写用户文档（如何搜索、如何使用AI功能）
- [ ] 创建API文档（Enterprise客户）
- [ ] 添加FAQ页面
- [ ] 配置Google Analytics

**交付物**：完整的营销网站、用户文档

#### Week 11：客户开发 + Beta测试（30小时）
- [ ] 在LinkedIn发布产品介绍
- [ ] 在Reddit r/LawFirm发帖
- [ ] 联系10个独立律师进行Beta测试
- [ ] 收集用户反馈
- [ ] 修复关键bug
- [ ] 优化搜索相关性

**获客策略**：
1. **LinkedIn**：发布文章"如何用$50/月替代$3000/月的Westlaw"
2. **Reddit**：r/LawFirm发帖"我做了一个便宜的法律案例搜索工具"
3. **直接外联**：找到独立律师的邮箱，发送个性化邮件

**交付物**：10个Beta用户、用户反馈报告

#### Week 12：正式发布 + 首批付费客户（30小时）
- [ ] 修复Beta测试发现的问题
- [ ] 在Product Hunt发布
- [ ] 在Hacker News发布Show HN
- [ ] 发送邮件给Beta用户，邀请付费
- [ ] 设置客户支持渠道（Intercom/Crisp）
- [ ] 监控系统稳定性

**目标**：
- 获取至少1个付费客户（$50/月）
- 注册用户 > 50人
- 搜索请求 > 500次

**月3里程碑**：
- ✅ 产品正式上线
- ✅ 获得首批付费客户
- ✅ 系统稳定运行

---

## 💰 第四部分：成本与预算

### 4.1 技术成本（3个月）

**完全免费的服务**：
- CourtListener API：$0（完全免费）
- PostgreSQL：$0（本地开发）
- React/FastAPI：$0（开源）

**付费服务**：
| 服务 | 用途 | 月费 | 3个月总计 |
|------|------|------|-----------|
| Railway/Render | 服务器部署 | $20 | $60 |
| Claude API | AI分析 | $50-100 | $150-300 |
| 域名 | crimejournal.com | $12/年 | $12 |
| Stripe | 支付处理 | $0（按交易收费） | $0 |
| **总计** | | | **$222-372** |

**最小可行预算**：$300

### 4.2 时间投入

**总时间**：365小时（约9周全职工作）
- 月1：125小时
- 月2：120小时
- 月3：120小时

**每周时间分配**：
- 开发：30小时/周
- 学习：5小时/周
- 客户开发：5小时/周

---

## 🎯 第五部分：成功指标

### 5.1 技术指标

**系统性能**：
- API响应时间：<500ms（P95）
- 系统可用性：>99%
- 搜索准确率：>90%（用户满意度）

**AI功能**：
- 案例总结质量：用户评分>4/5
- 相似案例相关性：>80%
- Claude API成本：<$100/月

### 5.2 商业指标

**用户获取**：
- 注册用户：>50人
- Beta测试用户：10人
- 付费客户：1-3人

**收入**：
- 月度经常性收入（MRR）：$50-150
- 客户获取成本（CAC）：<$100
- 客户生命周期价值（LTV）：>$600

### 5.3 里程碑检查点

**里程碑1（Week 4）**：
- [ ] CourtListener集成完成
- [ ] 用户可以搜索和查看案例
- [ ] 基础前端可用

**里程碑2（Week 8）**：
- [ ] AI功能完整
- [ ] 用户体验流畅
- [ ] 移动端可用

**里程碑3（Week 12）**：
- [ ] 产品正式上线
- [ ] 至少1个付费客户
- [ ] 系统稳定运行

---

## ⚠️ 第六部分：风险管理

### 6.1 技术风险

**风险1：CourtListener API限制**
- 概率：低
- 影响：中
- 缓解：实现缓存机制，减少API调用
- Plan B：使用其他免费法律数据源（Google Scholar）

**风险2：Claude API成本过高**
- 概率：中
- 影响：中
- 缓解：实现AI分析缓存，避免重复调用
- Plan B：使用开源模型（Llama 3）

**风险3：法律NLP难度高**
- 概率：中
- 影响：中
- 缓解：使用Claude API做文本理解，降低技术门槛
- Plan B：简化AI功能，专注基础检索

### 6.2 商业风险

**风险4：找不到付费客户**
- 概率：中
- 影响：高
- 缓解：
  - 开发前找3个意向客户（LOI）
  - 提供免费Pro账户换反馈
  - 降低定价至$20-30/月
- Plan B：转向法学院学生市场

**风险5：Westlaw降价竞争**
- 概率：低
- 影响：高
- 缓解：专注独立律师和小型律所（Westlaw忽视的市场）
- Plan B：转向白标解决方案

### 6.3 执行风险

**风险6：时间不足**
- 概率：中
- 影响：中
- 缓解：严格遵守MVP范围，砍掉非核心功能
- Plan B：延长时间线至4个月

---

## 🚀 第七部分：下一步行动

### 立即开始（本周）

**Day 1-2：环境搭建**
1. 注册CourtListener账号，获取API token
2. 注册Anthropic账号，获取Claude API key
3. 安装PostgreSQL 16
4. 创建GitHub仓库

**Day 3-4：技术验证**
1. 测试CourtListener API（搜索10个案例）
2. 测试Claude API（总结1个案例）
3. 验证技术可行性

**Day 5：客户验证**
1. 在LinkedIn联系5个独立律师
2. 询问他们的痛点和付费意愿
3. 验证市场需求

### 第一周目标

- [ ] 技术栈验证完成
- [ ] 找到3个意向客户（愿意试用）
- [ ] 数据库设计完成

---

## 📚 附录

### A. CourtListener API资源

**官方文档**：
- API文档：https://www.courtlistener.com/api/rest/v4/
- Python SDK：https://github.com/freelawproject/courtlistener
- 注册账号：https://www.courtlistener.com/sign-in/register/

**数据覆盖**：
- 联邦法院：最高法院、上诉法院、地区法院
- 州法院：50个州的最高法院和上诉法院
- 数据量：数百万案例

### B. 中国市场备选方案

**如果未来扩展到中国市场**：

**数据源选项**：
1. **中国裁判文书网**（免费但需爬取）
   - 数据量：1.2亿+判决书
   - 合规性：公开数据，可爬取
   - 技术难度：高（反爬虫）

2. **北大法宝**（付费授权）
   - 价格：2.5万元/年
   - 数据质量：高
   - API可用性：有

3. **威科先行**（付费授权）
   - 价格：11.4万元/年
   - 专注：财税法律
   - API可用性：需商业洽谈

**建议**：
- 短期：专注美国市场（CourtListener免费）
- 中期：评估中国市场需求
- 长期：如果有付费客户，再投入数据授权成本

### C. 竞品对比

| 维度 | CrimeJournal | Westlaw | LexisNexis | Google Scholar |
|------|--------------|---------|------------|----------------|
| 定价 | $50/月 | $3000+/月 | $3000+/月 | 免费 |
| 数据源 | CourtListener | 全面 | 全面 | 有限 |
| AI分析 | ✅ 内置 | ✅ 额外付费 | ✅ 额外付费 | ❌ 无 |
| 用户体验 | 现代 | 传统 | 传统 | 简陋 |
| 目标客户 | 独立律师 | 大型律所 | 大型律所 | 学生 |

---

**最后更新**：2026-03-20
**版本**：2.0（法律数据方向）
**下次审查**：Week 4（里程碑1）
