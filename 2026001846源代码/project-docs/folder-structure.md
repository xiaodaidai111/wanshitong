# 设备检修知识检索与标准作业系统 — 项目目录说明

## 系统概述

本系统是第十五届中国软件杯 A1 赛题作品，基于 uni-app + Flask 构建设备检修知识检索与标准作业系统。

核心功能：
1. 多模态知识检索（文本 / 故障图片 / 设备型号）
2. 标准化作业指引（步骤流程 / 合规校验 / 风险提醒）
3. 知识沉淀与更新（案例上传 / 审核入库 / 图谱更新）
4. 智能问修（故障问答 / 分步排查 / 图文解析）
5. 检修评估（质量评分 / 风险闭环 / 复盘报告）

---

## 顶层目录结构

```
2026001846源代码/
├── frontend/                # uni-app 前端（HBuilderX 运行）
├── backend/                 # Flask 后端服务
├── database/                # 数据库 schema 和迁移
├── uploads/                 # 用户上传文件存储
├── project-docs/            # 项目文档
├── start_all_services.py    # 一键启动所有服务
└── .env                     # 环境变量配置（不提交）
```

---

## 前端目录 (frontend/)

### 核心页面

| 目录 | 实际功能 | 说明 |
|------|---------|------|
| `pages/home/` | 首页工作台 | 系统概览、核心功能入口、今日任务、风险告警、知识更新 |
| `pages/takeaway-expert/` | 多模态知识检索 | 文本/图片/型号输入，检修等级选择，检索结果分区展示 |
| `pages/restaurant-recommendation/` | 知识沉淀与图谱 | 知识图谱 canvas、案例上传、审核状态、人工修正 |
| `pages/cooking-expert/` | 智能问修 | 故障问答、分步排查、图文解析 |
| `pages/health-manager/` | 标准作业指引 | 设备信息、检修等级、步骤流程、合规校验、状态指示器 |
| `pages/personal-center/` | 检修评估 / 用户中心 | 用户资料、检修计划、质量评估、成就系统 |

### 辅助页面

| 目录 | 功能 |
|------|------|
| `pages/user/` | 登录注册 |
| `pages/openclaw/` | 智能助手对话页 |
| `pages/image-viewer/` | 图片查看器 |
| `pages/webview/` | 内嵌网页 |
| `pages/community-detail/` | 社区详情 |
| `pages/nearby-communities/` | 现场空间 |
| `pages/recipe-recommendation/` | 检修资源推荐（历史遗留路径，内部已改造） |

### 组件 (src/components/)

| 组件 | 功能 |
|------|------|
| `HealthManagerFab/` | 标准作业页浮动按钮 |
| `cooking-assistant/` | 智能问修辅助组件 |
| `custom-navbar/` | 自定义导航栏 |
| `floating-ball/` | 浮动操作球 |
| `main-panel/` | 主面板组件 |
| `optimized-navbar/` | 优化导航栏 |
| `takeout-assessment/` | 检修质量评估组件 |

### 静态资源 (static/)

| 目录/文件 | 说明 |
|-----------|------|
| `manuals/` | 检修手册 PDF（含摩托车发动机维修手册.pdf） |
| `tabbar-icons/` | 底部导航图标 |
| `icons/` | 系统功能图标 |
| `avatar-*.png` | 用户头像 |
| `food.png` | 通用 fallback 图片（多页面引用） |
| `safeguard.png` | 检索页头像 |
| `healthymanager.png` | 标准作业页头像 |
| `niceexpert.png` | 知识沉淀页头像 |
| `openclaw.png` | 智能问修页头像 |
| `tweet-*.png` | 首页轮播图 |
| `icon-home.png` | 系统品牌图标 |

### 工具函数 (utils/)

| 文件 | 功能 |
|------|------|
| `request.js` | HTTP 请求封装 |
| `store.js` | 状态管理 |
| `cache.js` | 缓存工具 |
| `voice-input.js` | 语音输入控制器 |
| `guest.js` | 访客模式 |

### 知识库

| 文件 | 说明 |
|------|------|
| `map-agent/knowledge_base.json` | 前端知识库（摩托车发动机检修） |

---

## 后端目录 (backend/)

### 核心入口

| 文件 | 功能 |
|------|------|
| `unified_app.py` | 统一 Flask 应用，注册所有路由 |
| `unified_launcher.py` | 统一启动器，管理所有智能体进程 |
| `app_refactored.py` | 重构版应用入口 |
| `llm_core.py` | LLM 核心调用 |
| `mcp_tools.py` | MCP 工具集 |

### 路由 (routes/)

| 文件 | 功能 | 状态 |
|------|------|------|
| `auth.py` | 认证 | 核心 |
| `user.py` | 用户管理 | 核心 |
| `community.py` | 社区功能 | 核心 |
| `chat.py` | 聊天接口 | 核心 |
| `takeaway_health.py` | 检修分析接口 | 核心（前端调用） |
| `health_manager_deepseek.py` | 标准作业智能体 | 核心 |
| `map_agent.py` | 地图智能体 | 核心 |
| `speech_asr.py` | 语音识别 | 核心 |
| `ai_services.py` | AI 服务 | 核心 |
| `monitor.py` | 监控 | 核心 |
| `openclaw.py` | 智能助手 | 核心 |
| `cook_agent.py` | 问修智能体 | 核心 |
| `takeout.py` | 检修任务智能体 | 核心 |
| `restaurants.py` | 设备数据接口 | 保留（后端注册） |
| `recipe_recommendation.py` | 资源推荐接口 | 保留（后端注册） |
| `restaurant_marker.py` | 设备标记接口 | 保留（后端注册） |
| `health.py` | 健康检查 | 保留 |

### 智能体

| 目录 | 功能 |
|------|------|
| `takeout-agent/` | 检修任务智能体（含 knowledge_base.json） |
| `map_agent/` | 地图智能体 |
| `miniclaw/` | 工具集 |
| `RAG/` | 检索增强生成 |

### 数据库

| 文件 | 说明 |
|------|------|
| `health_diet.db` | SQLite 数据库（历史遗留命名） |

---

## 数据库目录 (database/)

| 文件 | 说明 |
|------|------|
| `schema.sql` | 主 schema |
| `init.sql` | 初始化脚本 |
| `community_schema.sql` | 社区表结构 |
| `health_score_schema.sql` | 评分表结构 |
| `recipe_recommendation_schema.sql` | 推荐表结构 |
| `migrations/` | 迁移脚本 |

---

## 页面路径与实际功能映射

由于 HBuilderX 路由依赖现有路径，页面目录名暂不修改，但内部已全部改造为设备检修语义：

| pages.json 路径 | 实际功能 | 内部标题 |
|----------------|---------|---------|
| `pages/home/home` | 首页工作台 | 设备检修知识作业系统 |
| `pages/takeaway-expert/takeaway-expert` | 多模态检索 | 检修知识检索助手 |
| `pages/restaurant-recommendation/restaurant-recommendation` | 知识沉淀 | 知识沉淀与图谱 |
| `pages/cooking-expert/cooking-expert` | 智能问修 | 故障问修助手 |
| `pages/health-manager/health-manager` | 标准作业 | 标准作业指引 |
| `pages/personal-center/personal-center` | 检修评估 | 检修评估中心 |

---

## HBuilderX 运行说明

1. 用 HBuilderX 打开 `frontend/` 目录
2. 运行到浏览器或模拟器
3. 首页自动加载 `pages/home/home`
4. 底部 tabBar 可切换 6 个核心功能

---

## 已清理内容

### 已删除的目录/文件

- `万事通/` — 空目录
- `map-agentv1/` — 空目录
- `HealthManager/` — 独立智能体，后端已有替代
- `frontend/react-agent/` — 空目录
- `frontend/frontend/` — 空目录
- `frontend/pages/diet-recommendation/` — 空目录
- `frontend/pages/analytics/` — 空目录
- `frontend/pages/health-risk/` — 空目录
- `frontend/unpackage/` — 构建缓存
- `frontend/dist/` — 旧构建产物
- `frontend/static/food/*.png` — 无引用的菜品图片
- `frontend/static/restaurant.png` — 无引用
- `frontend/src/components/food-map/` — 无引用组件
- `user/` — 重复的登录注册页
- `logs/` — 旧日志
- `backend/test_*.py` — 旧测试文件
- `__pycache__/` — Python 缓存

### 已重命名的文件

- `frontend/static/icons/calorie-search.png` → `manual-search.png`
- `frontend/static/icons/diet-report.png` → `inspection-report.png`
- `frontend/static/icons/food.png` → `equipment.png`

---

## 仍保留的历史遗留

以下文件因后端路由仍注册或前端仍引用，暂时保留：

| 文件/目录 | 保留原因 |
|-----------|---------|
| `backend/routes/restaurants.py` | unified_app.py 注册路由 |
| `backend/routes/recipe_recommendation.py` | unified_app.py 注册路由 |
| `backend/routes/restaurant_marker.py` | unified_app.py 注册路由 |
| `backend/health_diet.db` | 数据库文件 |
| `frontend/static/food.png` | 6个页面用作 fallback 图片 |
| `frontend/static/food/recipes.json` | 2个页面 import |
| `database/recipe_recommendation_schema.sql` | 数据库 schema |

---

## 摩托车发动机维修手册

本系统以摩托车发动机维修手册作为第一个专业检修物品：

- PDF 路径：`frontend/static/manuals/摩托车发动机维修手册.pdf`
- 知识库引用：`map-agent/knowledge_base.json`、`backend/takeout-agent/data/knowledge_base.json`
- 关联节点：发动机结构、点火系统、燃油供给、异响排查、机油润滑
