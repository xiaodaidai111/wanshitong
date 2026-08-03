# 一修项目现状分析与本轮优化记录

## 1. 当前前端工程

- 工程目录：`frontend`
- 当前 Web 入口：`frontend/index.html`、`frontend/main.js`、`frontend/App.vue`
- 技术栈：Vue 3 + Vite 5 + `@vitejs/plugin-vue`
- 保留依赖：原 uni-app 依赖仍在 `package.json` 中，旧页面仍保留在 `frontend/pages`
- 构建命令：`npm run build`
- 当前策略：不删除旧 uni-app 页面，不更换技术栈，在标准 Vue3 Web 入口上建设 B/S 工作台。

## 2. 当前页面结构

原项目保留了移动端页面：

- `pages/home/home.vue`：原首页/迁移说明入口。
- `pages/repair-search/repair-search.vue`：一修检索页，已有设备型号、故障描述、模式选择、结果卡片。
- `pages/repair-tasks/repair-tasks.vue`：一修任务页，已有统计、筛选和工单列表。
- `pages/knowledge-base/knowledge-base.vue`：一修知识库页，已有搜索和知识卡片。
- `pages/yixiu-profile/yixiu-profile.vue`：项目核查中心，已有智能体和核查清单。
- `pages/takeaway-expert`、`health-manager`、`restaurant-recommendation`、`recipe-recommendation`、`cooking-expert` 等旧页面仍存在，业务语义需要继续清理。

本轮 Web 入口重构为五个一级页面：

- 首页
- 智能检索
- 检修任务
- 知识库
- 个人中心

## 3. 请求封装与状态管理

- 旧请求封装：`frontend/utils/request.js`，基于 `uni.request`，适合原 uni-app 页面。
- 新增 Web 请求封装：`frontend/src/api/yixiuWeb.js`，基于浏览器 `fetch`，面向标准 Vue3 Web 入口。
- 新增集中兜底数据：`frontend/src/data/yixiuMock.js`，所有暂缺接口数据集中管理，避免散落在组件内。
- 当前没有 Pinia/Vuex，状态采用 Vue `ref/reactive/computed` 在 `App.vue` 内管理，符合当前轻量工程结构。

## 4. 后端工程

- 后端目录：`server/backend`
- 主入口：`unified_app.py`
- 框架：Flask + Flask-CORS
- 统一路由：`/api/yixiu`、`/api/ai`、`/api/rag`、`/api/maintenance-tasks`
- AI 网关：`services/ai_gateway.py`
- 默认 AI Provider：Qwen/DashScope，兼容 OpenAI 协议。
- RAG：`routes/rag.py` + `services/rag_service.py`，已有 LightRAG 相关接口。

## 5. 数据库与知识库

- 设备检修数据库脚本：`server/database/equipment_maintenance_schema.sql`
- 核心表：`equipment`、`maintenance_records`、`knowledge_base`、`standard_procedures`、`inspection_reports`、`risk_alerts`、`user_maintenance_profiles`
- 知识库 JSON：`server/backend/data/maintenance_knowledge_base.json`
- LightRAG 存储：`server/backend/lightrag_storage`

## 6. 本轮后端新增接口

在 `server/backend/routes/yixiu.py` 中补充：

- `GET /api/yixiu/files`：文件列表。
- `POST /api/yixiu/files`：保存上传文件元数据。
- `GET /api/yixiu/contacts`：现场联系人。
- `POST /api/yixiu/tasks`：创建检修任务。
- `PUT /api/yixiu/tasks/<task_id>/status`：Web 工作台任务状态流转。
- `POST /api/yixiu/recheck`：保存复检评估结果。
- `POST /api/yixiu/knowledge/update`：知识沉淀更新。

这些接口优先作为 Web 工作台可用能力，后续可进一步接入真实数据库表。

## 7. 本轮前端已落地能力

- 左侧统一导航，支持展开/收起。
- 顶部栏展示当前页面、面包屑、全局搜索、后端/AI/RAG 状态、用户入口。
- 首页展示系统状态、统计卡片、今日任务、快捷入口、风险提醒、图表、最近记录和智能体状态。
- 智能检索支持故障描述、设备信息、故障代码、文件上传记录、语音输入模拟、Qwen/RAG 检索结果展示。
- 检索结果支持分类筛选、详情、预览、复制引用、加入检修任务。
- 检修任务支持今日概览、任务管理、筛选、新建任务、详情查看、任务流转、复检评估、联系人查询。
- 知识库支持知识网络、文件管理、技术资料库、沉淀更新。
- 文件管理支持列表/卡片视图、搜索筛选、上传记录、预览错误状态。
- 个人中心支持检修记录和核查智能体调用。
- 所有暂缺真实数据均集中从 `yixiuMock.js` 兜底。

## 8. 仍需继续深化

- 将 `POST /api/yixiu/files` 接入真实 multipart 上传和文件存储。
- 文件预览需按文件唯一编号从后端换取真实访问地址。
- 文件权限、版本、回收站、操作日志需要落库。
- 旧 uni-app 页面里的食品、外卖、菜谱、餐厅、健康文案需要继续逐页清理。
- 任务步骤执行记录、图片上传、检测数据、报告导出需进一步落库。
- LoongArch/银河麒麟部署需要针对 OpenCV、Ultralytics、LightRAG、tiktoken 等依赖做安装验证和替代方案。
