# 一修网页版改造与 A1 赛题匹配说明

## 项目定位

一修是面向中国软件杯 A1 赛题“基于多模态大模型技术的设备检修知识检索与作业系统”的网页版项目。系统保留现有 uni-app 前端、Flask 统一后端、设备检修任务接口、知识库接口、语音能力和 RAG/知识图谱服务注册方式，在原有架构上完成品牌、入口和网页化表达改造。

## A1 赛题能力映射

| 赛题关注点 | 一修对应模块 | 已落地表现 |
| --- | --- | --- |
| 多模态知识检索 | `pages/repair-search/repair-search.vue`、`routes.yixiu`、`routes.rag` | 支持故障文本、图片、设备型号、维修资料匹配 |
| 标准作业流程 | `pages/repair-tasks/repair-tasks.vue`、`routes.maintenance_tasks`、`routes.yixiu` | 检修任务、风险等级、SOP 步骤、状态流转 |
| 知识沉淀与复用 | `pages/knowledge-base/knowledge-base.vue`、`maintenance_knowledge_base` | 手册、案例、问答、知识图谱、审核入库 |
| 一线协作 | `pages/repair-tasks/repair-tasks.vue`、`pages/yixiu-profile/yixiu-profile.vue` | 支持负责人协作、消息沟通、现场支援 |
| 质量核查 | `pages/yixiu-profile/yixiu-profile.vue`、`/api/yixiu/audit` | 合规性、质量分、复测确认、报告提交 |
| 统一编排接口 | `routes.yixiu` | 提供 `/api/yixiu/overview`、`/search`、`/audit` 等 A1 演示入口 |

## 多智能体分工

1. 检索智能体：理解故障输入，召回维修手册、相似案例、SOP 与工具备件清单。
2. 作业智能体：将检索结果转成现场可执行步骤，提示断电、验电、复测、报告提交等关键动作。
3. 知识智能体：审核一线案例，沉淀经验条目，维护知识图谱节点与关联关系。
4. 协作智能体：连接负责人、专家和验收人员，支撑任务沟通与现场支援。
5. 核查智能体：复核检索依据、作业合规、风险遗漏和最终报告完整性。

## 网页化改造结果

- `frontend/App.vue`：H5 桌面端从手机预览容器扩展为最大 1280px 的网页工作台。
- `frontend/pages/home/home.vue`：首页重建为“一修”工作台，突出 A1 赛题、核心能力、任务优先级、多智能体和知识沉淀，并接入 `/api/yixiu/overview`。
- `frontend/pages/repair-search/repair-search.vue`：新增干净命名的多模态检修知识检索页，接入 `/api/yixiu/search`。
- `frontend/pages/repair-tasks/repair-tasks.vue`：新增干净命名的检修任务工作台，接入 `/api/yixiu/tasks`。
- `frontend/pages/knowledge-base/knowledge-base.vue`：新增干净命名的检修知识库页面，接入 `/api/yixiu/knowledge`。
- `frontend/pages/yixiu-profile/yixiu-profile.vue`：新增项目核查中心，接入 `/api/yixiu/agents` 和 `/api/yixiu/audit`。
- `frontend/pages.json`：全局标题改为“一修”。
- `frontend/pages.json`：tabBar 主导航切换到 `repair-search`、`repair-tasks`、`knowledge-base`、`yixiu-profile`，旧业务页面不再作为网页路由入口注册。
- `frontend/manifest.json`、`frontend/src/manifest.json`：应用名称与权限说明改为设备检修场景。
- `server/backend/unified_app.py`：后端根服务名改为“一修 - 基于多模态大模型技术的设备检修知识检索与作业系统”。
- `server/backend/routes/yixiu.py`：新增一修统一编排蓝图，在保留旧接口的同时提供更符合赛题语义的 API。

## 一修 API 编排层

| 接口 | 用途 |
| --- | --- |
| `GET /api/yixiu/overview` | 网页首页概览，返回统计、多智能体、核心模块、任务和知识条目 |
| `GET /api/yixiu/agents` | 返回检索、作业、知识、协作、核查五类智能体分工 |
| `GET /api/yixiu/tasks` | 检修任务统一查询入口，兼容原任务数据 |
| `GET /api/yixiu/knowledge` | 检修知识统一查询入口，兼容原知识库数据 |
| `POST /api/yixiu/search` | A1 多模态检索编排演示入口 |
| `POST /api/yixiu/audit` | 检修结果核查入口 |

## 知识库数据源

- 默认设备检修知识库：`server/backend/data/maintenance_knowledge_base.json`。
- `routes.rag` 的初始化候选路径已优先指向该文件。
- `services.knowledge_retriever` 的默认检索路径已优先指向该文件。
- 旧 `takeout-agent/data/knowledge_base.json` 仍保留为兼容兜底，不作为一修主数据源。

## 核查清单

- H5 构建通过：`npm run build:h5`。
- 首页桌面端宽屏显示，不再被限制为窄手机壳。
- 首页可从 `/api/yixiu/overview` 读取一修概览数据，接口不可用时保留演示兜底。
- 首页移动端仍可一列/两列响应式展示。
- 项目名、标题、说明统一为“一修”。
- 原有前后端目录和后端蓝图注册方式保持不变，网页主路由已收敛到“一修”业务入口。
