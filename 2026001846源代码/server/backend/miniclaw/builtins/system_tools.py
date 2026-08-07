"""内置插件：系统操作工具（检修业务版）

提供天工（综合智能中枢）调度一修系统各业务模块的工具，所有工具均对接
真实后端接口或数据库，使天工能够真正“操作”系统、完成多步任务链。

覆盖能力：
- 系统概览（在线设备 / 待处理告警 / 待审核 / 今日任务）
- 检修任务查询与创建
- 知识库检索
- 智能问修（cook-agent）
- 知识图谱检索（LightRAG）
- agent（智能体）状态
"""
import logging
import os
import json
from typing import Any, Dict, List, Optional

from miniclaw.tools import BaseTool, ToolResult, ToolParameter

logger = logging.getLogger("miniclaw.system_tools")

# 本机后端基址，工具通过 HTTP 回调本系统各业务接口
BACKEND_BASE_URL = os.getenv("MINICLAW_BACKEND_URL", "http://127.0.0.1:5000").rstrip("/")

# 六大 agent 定义（与前端 yixiuMock / routes.yixiu.AGENTS 对齐）
AGENTS_STATE = [
    {"id": "tiangong", "name": "天工", "role": "统筹调度", "duty": "统筹检索、作业、知识、协作和核查智能体，汇总系统状态与风险。", "status": "online"},
    {"id": "guanwei", "name": "观微", "role": "故障检索", "duty": "发现设备故障线索，解析故障现象、型号、图片和维修文档。", "status": "online"},
    {"id": "zhiju", "name": "执矩", "role": "作业执行", "duty": "编排标准作业步骤，推进工单流转并提醒高风险安全确认。", "status": "online"},
    {"id": "bowen", "name": "博闻", "role": "知识管理", "duty": "整理技术资料、维护知识网络、沉淀历史检修案例。", "status": "busy"},
    {"id": "heming", "name": "和鸣", "role": "协作调度", "duty": "管理联系人、协调现场人员、发起专家支援与任务沟通。", "status": "online"},
    {"id": "mingjian", "name": "明鉴", "role": "复检核查", "duty": "执行复检评估、安全检查、质量核验和任务验收。", "status": "online"},
]


def _http_get(path: str, params: Optional[Dict[str, Any]] = None, timeout: int = 10) -> Dict[str, Any]:
    import requests
    url = path if path.startswith("http") else f"{BACKEND_BASE_URL}{path}"
    resp = requests.get(url, params=params, timeout=timeout)
    return {"status": resp.status_code, "data": resp.json() if resp.content else {}}


def _http_post(path: str, payload: Optional[Dict[str, Any]] = None, timeout: int = 20) -> Dict[str, Any]:
    import requests
    url = path if path.startswith("http") else f"{BACKEND_BASE_URL}{path}"
    resp = requests.post(url, json=payload or {}, timeout=timeout)
    return {"status": resp.status_code, "data": resp.json() if resp.content else {}}


def _safe_http(callable_fn, *args, **kwargs) -> ToolResult:
    """统一封装 HTTP 调用异常，返回 ToolResult。"""
    try:
        result = callable_fn(*args, **kwargs)
        status = result.get("status", 0)
        data = result.get("data", {})
        if status == 401:
            return ToolResult(success=False, output="", error="接口需要登录鉴权，暂无法在内部直接调用")
        if status >= 400:
            return ToolResult(success=False, output="", error=f"接口返回 {status}: {data}")
        return ToolResult(success=True, output=json.dumps(data, ensure_ascii=False), metadata={"raw": data})
    except Exception as exc:  # noqa: BLE001
        logger.error("HTTP 工具调用失败: %s", exc)
        return ToolResult(success=False, output="", error=f"调用失败: {exc}")


class SystemOverviewTool(BaseTool):
    name = "system_overview"
    description = "获取一修系统整体概览，包括在线设备数、待处理告警、待审核案例、今日检修任务数。用于天工生成系统状态简报。"
    parameters = []

    def execute(self, **kwargs) -> ToolResult:
        return _safe_http(_http_get, "/api/dashboard/overview")


class MaintenanceTaskTool(BaseTool):
    name = "maintenance_task"
    description = "查询或创建检修任务。action='list' 按状态筛选任务（status 可选 pending/in_progress/completed/all）；action='get' 按 id 获取任务详情；action='create' 创建新任务。"
    parameters = [
        ToolParameter(name="action", type="string", description="操作类型: list / get / create", required=True),
        ToolParameter(name="status", type="string", description="任务状态筛选，list 时可用：pending/in_progress/completed/all", required=False, default="all"),
        ToolParameter(name="task_id", type="string", description="任务ID，get 时必填", required=False),
        ToolParameter(name="data", type="object", description="创建任务的字段，create 时必填", required=False),
    ]

    def execute(self, **kwargs) -> ToolResult:
        action = (kwargs.get("action") or "").strip().lower()
        if action == "list":
            status = (kwargs.get("status") or "all").strip()
            params = {"status": status} if status and status != "all" else {}
            result = _safe_http(_http_get, "/api/maintenance-tasks/", params=params)
            if result.success:
                return result
            # HTTP 鉴权失败(401)时，天工作为系统内部智能体直接读数据库获取任务
            return self._list_from_db(status)
        if action == "get":
            task_id = kwargs.get("task_id")
            if not task_id:
                return ToolResult(success=False, output="", error="get 操作需要 task_id")
            return _safe_http(_http_get, f"/api/maintenance-tasks/{task_id}")
        if action == "create":
            data = kwargs.get("data") or {}
            return _safe_http(_http_post, "/api/maintenance-tasks/", payload=data)
        return ToolResult(success=False, output="", error=f"不支持的操作: {action}")

    @staticmethod
    def _cell(row: Any, key: str) -> str:
        try:
            value = row[key]
        except Exception:  # noqa: BLE001
            return ""
        return "" if value is None else str(value)

    def _list_from_db(self, status: str) -> ToolResult:
        """HTTP 接口需鉴权时的回退方案：直接读取检修任务表。"""
        try:
            from utils import get_db_connection
        except Exception as exc:  # noqa: BLE001
            return ToolResult(success=False, output="", error=f"任务接口需登录且无法读取数据库: {exc}")
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                where = "WHERE 1=1"
                params: List[Any] = []
                if status and status != "all":
                    where += " AND mr.status = %s"
                    params.append(status)
                cursor.execute(
                    f"""SELECT mr.id, mr.title, mr.severity, mr.status, mr.description,
                               mr.fault_code, mr.created_at, u.name AS assignee_name,
                               e.name AS equipment_name, e.model AS equipment_model
                        FROM maintenance_records mr
                        LEFT JOIN users u ON u.id = mr.user_id
                        LEFT JOIN equipment e ON e.id = mr.equipment_id
                        {where}
                        ORDER BY mr.created_at DESC
                        LIMIT 20""",
                    params,
                )
                rows = cursor.fetchall()
        except Exception as exc:  # noqa: BLE001
            return ToolResult(success=False, output="", error=f"读取任务数据库失败: {exc}")
        if not rows:
            return ToolResult(success=True, output=f"检修任务列表为空(status={status})", metadata={"tasks": []})
        lines = []
        for r in rows:
            lines.append(
                f"- [{self._cell(r, 'id')}] {self._cell(r, 'title')} | "
                f"{self._cell(r, 'equipment_name') or '未知设备'} ({self._cell(r, 'equipment_model')}) | "
                f"严重度:{self._cell(r, 'severity')} | 状态:{self._cell(r, 'status')} | "
                f"负责人:{self._cell(r, 'assignee_name') or '未分配'} | 创建:{self._cell(r, 'created_at')}"
            )
        return ToolResult(
            success=True,
            output=f"检修任务列表({len(rows)}条):\n" + "\n".join(lines),
            metadata={"tasks": [dict(r) for r in rows]},
        )


class KnowledgeSearchTool(BaseTool):
    name = "knowledge_search"
    description = "检索一修知识库（历史故障案例、维修手册、标准作业流程等）。通过关键词匹配知识条目。"
    parameters = [
        ToolParameter(name="keyword", type="string", description="检索关键词，如设备型号、故障现象、部件名称", required=True),
        ToolParameter(name="limit", type="integer", description="返回条目上限", required=False, default=10),
    ]

    def execute(self, **kwargs) -> ToolResult:
        keyword = (kwargs.get("keyword") or "").strip()
        if not keyword:
            return ToolResult(success=False, output="", error="检索关键词不能为空")
        limit = int(kwargs.get("limit", 10))
        result = _safe_http(_http_get, "/api/yixiu/knowledge", params={"keyword": keyword, "limit": limit})
        if result.success and result.metadata.get("raw"):
            raw = result.metadata["raw"]
            items = raw.get("data", raw) if isinstance(raw, dict) else raw
            if isinstance(items, dict):
                items = items.get("items") or items.get("list") or items
            summary = self._summarize(items, keyword)
            return ToolResult(success=True, output=summary, metadata=result.metadata)
        return result

    @staticmethod
    def _summarize(items: Any, keyword: str) -> str:
        if not items:
            return f"未检索到与「{keyword}」相关的知识条目"
        if isinstance(items, dict):
            items = items.get("items") or items.get("list") or []
        rows: List[str] = []
        for idx, item in enumerate(items[:10], 1):
            if not isinstance(item, dict):
                continue
            title = item.get("title") or item.get("name") or "未命名"
            equip = item.get("equipment") or item.get("model") or ""
            cat = item.get("category") or item.get("type") or ""
            rows.append(f"{idx}. {title}" + (f"（{equip}）" if equip else "") + (f" [{cat}]" if cat else ""))
        return f"检索「{keyword}」命中 {len(items)} 条知识：\n" + "\n".join(rows)


class RepairConsultTool(BaseTool):
    name = "repair_consult"
    description = "调用智能问修（观微/团团能力），根据故障描述给出排查建议。适用于设备故障诊断、检修方法咨询。"
    parameters = [
        ToolParameter(name="message", type="string", description="故障描述或问修问题", required=True),
        ToolParameter(name="action", type="string", description="问修动作类型，可选，如 diagnose/plan", required=False),
    ]

    def execute(self, **kwargs) -> ToolResult:
        message = (kwargs.get("message") or "").strip()
        if not message:
            return ToolResult(success=False, output="", error="问修内容不能为空")
        payload = {"message": message}
        if kwargs.get("action"):
            payload["action"] = kwargs["action"]
        result = _safe_http(_http_post, "/cook-agent/chat", payload=payload, timeout=45)
        if result.success and result.metadata.get("raw"):
            raw = result.metadata["raw"]
            text = raw.get("response") or raw.get("data", {}).get("response") or raw.get("answer") or ""
            if text:
                return ToolResult(success=True, output=text, metadata=result.metadata)
        return result


class KnowledgeGraphTool(BaseTool):
    name = "knowledge_graph"
    description = "查询知识图谱（LightRAG），支持多种检索模式：naive/local/global/hybrid/mix。用于结构化故障原因、部件关系、检修方案推理。"
    parameters = [
        ToolParameter(name="query", type="string", description="自然语言查询，如'CG-125发动机异响的原因和检修方案'", required=True),
        ToolParameter(name="mode", type="string", description="检索模式: naive/local/global/hybrid/mix", required=False, default="hybrid"),
    ]

    def execute(self, **kwargs) -> ToolResult:
        query = (kwargs.get("query") or "").strip()
        if not query:
            return ToolResult(success=False, output="", error="图谱查询不能为空")
        mode = (kwargs.get("mode") or "hybrid").strip()
        result = _safe_http(_http_post, "/api/rag/query", payload={"query": query, "mode": mode}, timeout=45)
        if result.success and result.metadata.get("raw"):
            raw = result.metadata["raw"]
            text = raw.get("response") or raw.get("data", {}).get("response") or raw.get("answer") or ""
            if not text and isinstance(raw, dict):
                text = json.dumps(raw, ensure_ascii=False)[:1500]
            if text:
                return ToolResult(success=True, output=text, metadata=result.metadata)
        return result


class AgentStatusTool(BaseTool):
    name = "agent_status"
    description = "获取六大 agent（智能体）的当前状态与职责，用于天工统筹调度、判断该把任务分派给哪个 agent。"
    parameters = [
        ToolParameter(name="agent_id", type="string", description="可选，指定 agent ID（tiangong/guanwei/zhiju/bowen/heming/mingjian），不填则返回全部", required=False),
    ]

    def execute(self, **kwargs) -> ToolResult:
        agent_id = (kwargs.get("agent_id") or "").strip()
        if agent_id:
            for a in AGENTS_STATE:
                if a["id"] == agent_id:
                    return ToolResult(success=True, output=json.dumps(a, ensure_ascii=False), metadata={"agent": a})
            return ToolResult(success=False, output="", error=f"未找到 agent: {agent_id}")
        lines = []
        for a in AGENTS_STATE:
            lines.append(f"- {a['name']}（{a['role']}）[{a['status']}]: {a['duty']}")
        return ToolResult(success=True, output="六大 agent 状态：\n" + "\n".join(lines), metadata={"agents": AGENTS_STATE})


def register(api):
    api.register_tool(SystemOverviewTool())
    api.register_tool(MaintenanceTaskTool())
    api.register_tool(KnowledgeSearchTool())
    api.register_tool(RepairConsultTool())
    api.register_tool(KnowledgeGraphTool())
    api.register_tool(AgentStatusTool())
