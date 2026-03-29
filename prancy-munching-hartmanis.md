# CrimeJournal 全面完善与 BUG 修复计划

> 基于代码审查、后端测试(328项通过/95%覆盖)、前端构建验证(成功) 的系统性改进方案

---

## 一、项目现状总结

| 维度 | 状态 | 备注 |
|------|------|------|
| 后端测试 | ✅ 328项全通过 | 覆盖率 95.18% (要求 80%) |
| 前端构建 | ✅ TypeScript 编译通过 | 生产构建成功 (341KB JS) |
| 核心功能 | ⚠️ 部分实现 | 存在多个空壳/TODO 实现 |
| 安全 | 🔴 严重问题 | JWT密钥/内存数据库/无验证 |
| 代码质量 | ⚠️ 需改进 | 存在死代码/重复/UX问题 |

---

## 二、P0 - 必须立即修复（安全 + 核心功能）

### 2.1 安全问题

#### 🔴 CRITICAL: JWT 密钥空默认值
- **文件**: `backend/app/config.py:34`
- **问题**: `jwt_secret_key: str = ""` — 生产环境若未设置环境变量则使用空密钥
- **修复**: 启动时强制检查密钥是否存在，缺失则抛出错误
- **验证**: 确认无 `.env` 时启动失败

#### 🔴 CRITICAL: 内存数据库 (FAKE_USERS_DB)
- **文件**: `backend/app/api/auth.py:80`
- **问题**: `FAKE_USERS_DB = {}` — 服务器重启数据丢失，模块间直接修改对方数据
- **修复**: 集成真实 SQLite 数据库 (已有 SQLAlchemy 模型)
- **验证**: 注册用户后重启服务器，用户仍然存在

#### 🔴 CRITICAL: Token 黑名单任意添加
- **文件**: `backend/app/api/auth.py`
- **问题**: 登出 API 无任何验证，任何人都可向黑名单添加任意 token
- **修复**: 实现带 TTL 的 Redis 黑名单，或使用 refresh token 机制
- **验证**: 测试恶意 token 不会被黑名单阻止

#### 🟡 HIGH: 缺少输入验证
- **文件**: `backend/app/api/auth.py`
- **问题**: 无邮箱格式强校验、无密码强度要求、无搜索参数长度限制
- **修复**: Pydantic EmailStr 已部分验证；补充密码强度正则、搜索参数校验
- **验证**: 测试超长密码/邮箱/搜索词被正确拒绝

### 2.2 功能缺失（空实现）

#### 🔴 CRITICAL: Account.tsx 多个空函数
1. **修改密码** (`Account.tsx:101-118`)
   - 问题: `handleChangePassword` 中 `// TODO: Call backend API` 是空操作
   - 修复: 添加 `/auth/change-password` 后端 API，前端调用

2. **更新资料** (`Account.tsx:45-52`)
   - 问题: `updateMutation.mutate` 只调用 `authApi.me()` 不传参数
   - 修复: 添加 `/auth/profile` PUT API，前端传 full_name

3. **删除账户** (`Account.tsx:86-92`)
   - 问题: `deleteMutation` 是 `Promise.resolve({})` 占位符
   - 修复: 添加 `/auth/delete` DELETE API，前端调用

4. **CaseDetail 摘要生成无反馈** (`CaseDetail.tsx:235`)
   - 问题: `casesApi.summarize(caseId)` 调用后不更新 UI
   - 修复: 添加 loading 状态和结果更新

#### 🔴 CRITICAL: 后端密码修改 API 缺失
- **文件**: `backend/app/api/auth.py`
- **修复**: 添加 `PUT /auth/password` 端点，验证旧密码后更新

---

## 三、P1 - 重要改进（用户体验 + 代码质量）

### 3.1 前端 UX 问题

#### 🟡 HIGH: 搜索页无分页
- **文件**: `frontend/src/pages/Search.tsx`
- **问题**: 结果无分页控件，无法加载更多
- **修复**: 添加分页控件 (page/limit)，使用 TanStack Query 加载状态
- **修复2**: 显示 "找到 X 条结果"

#### 🟡 HIGH: 登录后重定向固定到 /search
- **文件**: `frontend/src/lib/auth.tsx` (推测)
- **问题**: 总是跳转到 `/search` 而非上一页
- **修复**: 使用 `useLocation` + `navigate(to, { replace: true })` 回到来源

#### 🟡 MEDIUM: 无 404 页面
- **文件**: `frontend/src/App.tsx`
- **修复**: 添加 `<NotFound />` 路由组件

#### 🟡 MEDIUM: 部分翻译缺失
- **文件**: `frontend/src/lib/i18n.tsx`
- **问题**: `footer` 部分中文缺失、部分页面翻译不完整
- **修复**: 补充所有翻译键

#### 🟡 MEDIUM: 删除确认使用 window.confirm
- **文件**: 多处 (`Account.tsx:121`, `Favorites.tsx`)
- **修复**: 使用自定义确认对话框组件替代

### 3.2 代码质量问题

#### 🟡 HIGH: 未使用的导入
- **文件**: 多个页面 (`Account.tsx`, `Search.tsx`, `Favorites.tsx`, `CaseDetail.tsx`, `Home.tsx`)
- **问题**: 都导入 `Navbar` 但未使用
- **修复**: 删除未使用的 `Navbar` 导入

#### 🟡 MEDIUM: LoadingSpinner CSS 类名错误
- **文件**: `frontend/src/components/LoadingSpinner.tsx`
- **问题**: 使用 `animate-spin` CSS 而非 Tailwind 的 `animate-spin` 类
- **修复**: 确认 CSS 类名正确

#### 🟡 MEDIUM: 导出不一致
- **文件**: `frontend/src/components/ui/button.tsx`
- **问题**: 同时使用命名导出和默认导出
- **修复**: 统一导出方式

#### 🟡 MEDIUM: i18n 类型不完整
- **文件**: `frontend/src/lib/i18n.tsx`
- **问题**: `Translations` 接口缺少 `footer.*`, `about.*` 等键
- **修复**: 补充完整类型定义

### 3.3 后端改进

#### 🟡 HIGH: 测试警告
- **问题**: `test_cache_service.py` 中协程未被 await
- **修复**: `tests/test_cache_service.py` 中补充 mock 的 async iterator

#### 🟡 MEDIUM: 覆盖率未覆盖的代码
- **文件**: `app/api/cases.py` — 37 行未覆盖 (84% vs 平均 95%)
- **问题**: `get_db()` 的 `NotImplementedError`、部分 AI 分析端点
- **修复**: 添加测试覆盖未覆盖路径

---

## 四、P2 - 架构与长期改进

### 4.1 架构升级

#### 🟢 MEDIUM: Redis 缓存服务未真实集成
- **文件**: `backend/app/services/cache.py`
- **问题**: 存在 CacheService 但可能未实际连接
- **修复**: 添加 Redis 连接健康检查，缺失时优雅降级

#### 🟢 MEDIUM: 订阅系统使用内存模拟
- **文件**: `backend/app/api/subscriptions.py`
- **问题**: 直接修改 `FAKE_USERS_DB["subscription_tier"]`
- **修复**: 集成真实数据库字段

#### 🟢 MEDIUM: 使用量限制中间件未强制执行
- **文件**: `backend/app/middleware/usage.py`
- **问题**: 当前只记录日志，实际限制在端点层面
- **修复**: 中间件中强制执行限制，超限返回 429

### 4.2 API 限流与防护

#### 🟢 LOW: 无全局请求限流
- **修复**: 添加 `slowapi` 或自定义中间件限制请求频率
- **修复**: 添加 `X-Request-ID` 追踪

#### 🟢 LOW: 缺少审计日志
- **修复**: 添加关键操作的日志记录 (注册、登录、搜索、订阅变更)

### 4.3 前端增强

#### 🟢 MEDIUM: 高级筛选器 (Search)
- 日期范围选择器、法院多选、案例类型筛选

#### 🟢 MEDIUM: 黑暗模式
- 适配系统偏好，支持手动切换

#### 🟢 LOW: PWA 支持
- 添加 manifest.json, service worker

#### 🟢 LOW: 移动端适配
- 检查 SearchBar、导航菜单在移动端的表现

---

## 五、执行计划（按优先级排序）

### Phase 1: 安全 + 核心功能 (预计 3-5 小时)

| 序号 | 任务 | 文件 | 验证方式 |
|------|------|------|----------|
| 1 | JWT 密钥强制检查 | `config.py` | 无密钥时启动报错 |
| 2 | SQLite 真实数据库集成 | `auth.py`, `models/` | 重启后用户数据持久 |
| 3 | Token 黑名单修复 | `auth.py` | 恶意 token 无法使用 |
| 4 | 密码修改 API + 前端 | `auth.py`, `Account.tsx` | 实际修改密码 |
| 5 | 资料更新 API + 前端 | `auth.py`, `Account.tsx` | 实际更新姓名 |
| 6 | 删除账户 API + 前端 | `auth.py`, `Account.tsx` | 实际删除账户 |
| 7 | 摘要生成反馈 | `CaseDetail.tsx` | 加载状态+结果更新 |

### Phase 2: UX 改进 (预计 2-3 小时)

| 序号 | 任务 | 文件 |
|------|------|------|
| 8 | 搜索分页 + 结果计数 | `Search.tsx` |
| 9 | 登录后重定向来源页 | `Login.tsx`, `Register.tsx` |
| 10 | 404 页面 | `App.tsx` |
| 11 | 翻译补全 | `i18n.tsx` |
| 12 | 删除未使用导入 | 多个页面 |
| 13 | 自定义确认对话框 | 替换 window.confirm |

### Phase 3: 代码质量 + 架构 (预计 2-3 小时)

| 序号 | 任务 | 文件 |
|------|------|------|
| 14 | 修复测试警告 | `test_cache_service.py` |
| 15 | 提升 cases.py 覆盖率 | 新增测试 |
| 16 | Redis 健康检查 + 降级 | `cache.py` |
| 17 | 订阅系统数据库集成 | `subscriptions.py` |
| 18 | 使用量限制中间件强制执行 | `usage.py` |
| 19 | API 限流中间件 | 新增中间件 |

### Phase 4: 高级功能 (预计 3-5 小时)

| 序号 | 任务 |
|------|------|
| 20 | 高级搜索筛选器 |
| 21 | 黑暗模式 |
| 22 | PWA 支持 |
| 23 | 审计日志 |
| 24 | 移动端适配检查 |

---

## 六、关键文件索引

### 后端
| 文件 | 用途 |
|------|------|
| `backend/app/config.py` | 配置管理 (JWT密钥问题) |
| `backend/app/api/auth.py` | 认证 API (内存DB/空函数) |
| `backend/app/api/cases.py` | 案例 API (84%覆盖率) |
| `backend/app/api/subscriptions.py` | 订阅 API (内存模拟) |
| `backend/app/middleware/usage.py` | 用量限制 (未强制) |
| `backend/app/services/cache.py` | 缓存服务 (测试警告) |
| `backend/app/models/user.py` | 用户模型 |
| `backend/tests/` | 测试套件 (328项) |

### 前端
| 文件 | 用途 |
|------|------|
| `frontend/src/pages/Account.tsx` | 账户页 (3个空函数) |
| `frontend/src/pages/CaseDetail.tsx` | 案例详情 (无反馈) |
| `frontend/src/pages/Search.tsx` | 搜索页 (无分页) |
| `frontend/src/lib/i18n.tsx` | 国际化 (翻译缺失) |
| `frontend/src/App.tsx` | 路由 (无404) |
| `frontend/src/lib/api.ts` | API 客户端 |

---

## 七、验证清单

### 必测场景
- [ ] 无 `.env` 文件时后端启动失败 (JWT 密钥检查)
- [ ] 注册用户 → 重启服务器 → 用户仍存在 (DB 持久化)
- [ ] 修改密码功能实际生效
- [ ] 更新姓名功能实际生效
- [ ] 删除账户功能实际生效
- [ ] 搜索结果分页正常
- [ ] 登录后返回来源页
- [ ] 所有翻译键在两种语言下都有值
- [ ] 328 项后端测试全部通过
- [ ] 前端生产构建成功
- [ ] TypeScript 类型检查无错误
