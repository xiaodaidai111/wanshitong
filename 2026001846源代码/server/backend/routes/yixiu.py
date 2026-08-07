"""一修网页版业务编排接口。

提供多模态检索、标准作业、知识沉淀和人工审核所需的稳定接口。
所有新增业务数据使用 SQLite 持久化，上传文件保存到本机 uploads/yixiu 目录。
"""

from __future__ import annotations

import base64
import json
import logging
import mimetypes
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from flask import Blueprint, current_app, request, send_file
from werkzeug.utils import secure_filename

from utils import error_response, success_response

logger = logging.getLogger(__name__)
yixiu_bp = Blueprint("yixiu", __name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
DB_PATH = DATA_DIR / "yixiu_web.db"
KNOWLEDGE_PATH = DATA_DIR / "maintenance_knowledge_base.json"

AGENTS = [
    {"id": "retrieval", "name": "观微", "role": "多模态检索智能体", "duty": "联合分析文字、现场图片、设备型号并召回手册、案例与作业流程。", "status": "online"},
    {"id": "procedure", "name": "执矩", "role": "标准作业智能体", "duty": "按设备类型和检修等级编排安全确认、检测、维修、复测与归档步骤。", "status": "online"},
    {"id": "knowledge", "name": "博闻", "role": "知识沉淀智能体", "duty": "整理一线案例，提取故障、部件、工具、风险和处置关系并进入审核。", "status": "online"},
    {"id": "collaboration", "name": "和鸣", "role": "现场协作智能体", "duty": "连接负责人、专家与复检人员，支撑任务沟通和现场协作。", "status": "online"},
    {"id": "audit", "name": "明鉴", "role": "质量核查智能体", "duty": "核验引用依据、作业合规、安全风险和报告完整性。", "status": "online"},
]

MODULES = [
    {"key": "multimodal_search", "title": "多模态知识检索", "desc": "支持文本、故障图片、维修文档和设备型号联合检索。", "agent": "观微"},
    {"key": "standard_work", "title": "标准作业闭环", "desc": "覆盖任务创建、逐步作业、合规确认、复检和报告归档。", "agent": "执矩"},
    {"key": "knowledge_graph", "title": "知识沉淀与更新", "desc": "支持案例上传、人工修正、审核入库与知识图谱更新。", "agent": "博闻"},
    {"key": "quality_audit", "title": "安全与质量核查", "desc": "复核引用、风险提醒、操作顺序、数据记录和报告字段。", "agent": "明鉴"},
]

CONTACTS = [
    {"id": 1, "name": "聪明的一修", "position": "检修工程师", "department": "动力设备检修一组", "specialty": "发动机 / 电气", "phone": "138-0000-1024", "status": "在线", "currentTask": "ZK-320 过热检修", "devices": ["CG-125", "ZK-320"], "workload": 72},
    {"id": 2, "name": "王铭", "position": "复检人员", "department": "质量复检组", "specialty": "复检评估", "phone": "138-0000-2048", "status": "在线", "currentTask": "点火系统复核", "devices": ["DLI-001"], "workload": 48},
    {"id": 3, "name": "赵宁", "position": "安全负责人", "department": "安全管理部", "specialty": "高风险作业", "phone": "138-0000-4096", "status": "忙碌", "currentTask": "高风险作业确认", "devices": ["配电柜", "液压系统"], "workload": 83},
]


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


_BUILTIN_TEMPLATES = [
    {
        "id": "tpl-blank",
        "name": "空白文档",
        "icon": "📝",
        "category": "通用",
        "description": "从零开始创建一份空白技术文档",
        "skeleton": {"content": "# 文档标题\n\n在此输入内容..."}
    },
    {
        "id": "tpl-sop",
        "name": "检修作业 SOP",
        "icon": "📋",
        "category": "检修流程",
        "description": "标准作业流程模板，适用于设备检修、维护作业",
        "skeleton": {"content": "# 检修作业 SOP\n\n## 一、基本信息\n- 设备名称：\n- 设备型号：\n- 作业类型：\n- 作业地点：\n- 负责人：\n\n## 二、安全确认\n- [ ] 停机断电\n- [ ] 验电挂牌\n- [ ] 穿戴劳保用品\n- [ ] 工具检查合格\n\n## 三、作业步骤\n1. 外观检查\n2. 参数测量\n3. 故障定位\n4. 维修处置\n5. 更换部件\n\n## 四、复测验收\n- [ ] 空载试运行\n- [ ] 负载试运行\n- [ ] 参数记录\n- [ ] 清理现场\n\n## 五、备注\n"}
    },
    {
        "id": "tpl-fault",
        "name": "故障排查报告",
        "icon": "🔍",
        "category": "故障分析",
        "description": "故障现象、排查过程、处置结论完整记录",
        "skeleton": {"content": "# 故障排查报告\n\n## 一、故障现象\n- 设备：\n- 故障描述：\n- 发生时间：\n- 影响范围：\n\n## 二、排查过程\n### 初步检查\n- 外观检查：\n- 参数检测：\n\n### 深入分析\n- 可能原因1：\n- 可能原因2：\n- 排查方法：\n\n## 三、处置措施\n- 最终原因：\n- 处置方案：\n- 更换部件：\n\n## 四、预防建议\n"}
    },
    {
        "id": "tpl-meeting",
        "name": "检修会议纪要",
        "icon": "📒",
        "category": "协作沟通",
        "description": "班组例会、技术交流、故障复盘纪要",
        "skeleton": {"content": "# 检修会议纪要\n\n## 会议信息\n- 会议主题：\n- 会议时间：\n- 参会人员：\n- 主持人：\n\n## 议题与讨论\n### 议题一：\n- 讨论内容：\n- 结论：\n\n### 议题二：\n- 讨论内容：\n- 结论：\n\n## 行动计划\n| 事项 | 责任人 | 截止时间 | 状态 |\n|------|--------|----------|------|\n|  |  |  |  |\n\n## 备注\n"}
    },
    {
        "id": "tpl-safety",
        "name": "安全操作规范",
        "icon": "🛡️",
        "category": "安全规范",
        "description": "高风险作业安全规程与防护要求",
        "skeleton": {"content": "# 安全操作规范\n\n## 一、适用范围\n本规范适用于 作业。\n\n## 二、人员要求\n- 作业人员必须持有 资格证\n- 熟悉设备结构与操作规程\n- 掌握应急处置方法\n\n## 三、防护用品\n- [ ] 安全帽\n- [ ] 绝缘手套\n- [ ] 护目镜\n- [ ] 防滑鞋\n- [ ] 安全带（高空作业）\n\n## 四、安全流程\n1. 开具工作票\n2. 现场交底\n3. 落实防护措施\n4. 实施作业\n5. 验收确认\n\n## 五、应急处置\n- 触电急救：\n- 火灾扑救：\n- 设备故障：\n\n## 六、注意事项\n"}
    }
]


def _seed_templates(conn):
    count = conn.execute("SELECT COUNT(*) as c FROM yixiu_doc_templates").fetchone()["c"]
    if count > 0:
        return
    now = _now()
    for t in _BUILTIN_TEMPLATES:
        conn.execute(
            "INSERT INTO yixiu_doc_templates VALUES (?, ?, ?, ?, ?, ?, 1, ?)",
            (t["id"], t["name"], t["icon"], t["category"], t["description"],
             json.dumps(t["skeleton"], ensure_ascii=False), now),
        )


def _db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS yixiu_files (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, stored_name TEXT, mime TEXT,
          type TEXT, category TEXT, folder TEXT, size INTEGER DEFAULT 0,
          equipment TEXT, model TEXT, uploader TEXT, uploaded_at TEXT,
          audit_status TEXT, parse_status TEXT, version TEXT DEFAULT 'v1.0',
          purpose TEXT DEFAULT 'knowledge', analysis_json TEXT DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS yixiu_tasks (
          id TEXT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL,
          completed_steps TEXT DEFAULT '[]', created_at TEXT, updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS yixiu_knowledge (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, type TEXT, category TEXT,
          equipment TEXT, model TEXT, summary TEXT, content TEXT, tags TEXT,
          source TEXT, status TEXT, reviewer TEXT, correction TEXT,
          created_at TEXT, updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS yixiu_contacts (
          id TEXT PRIMARY KEY, account TEXT UNIQUE, name TEXT NOT NULL,
          avatar TEXT, position TEXT, department TEXT, specialty TEXT,
          phone TEXT, status TEXT DEFAULT '在线', devices TEXT DEFAULT '[]',
          current_task TEXT, workload INTEGER DEFAULT 0,
          employee_id TEXT, updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS yixiu_messages (
          id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL,
          sender_id TEXT, sender_name TEXT, message_type TEXT DEFAULT 'text',
          text TEXT, attachment_json TEXT DEFAULT '{}', card_json TEXT DEFAULT '{}',
          created_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_yixiu_messages_conversation
          ON yixiu_messages(conversation_id, created_at);
        CREATE TABLE IF NOT EXISTS yixiu_knowledge_versions (
          id TEXT PRIMARY KEY,
          knowledge_id TEXT NOT NULL,
          version INTEGER NOT NULL,
          content_snapshot TEXT NOT NULL,
          title_snapshot TEXT,
          change_summary TEXT DEFAULT '',
          editor_id TEXT,
          editor_name TEXT,
          created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS yixiu_knowledge_collaborators (
          id TEXT PRIMARY KEY,
          knowledge_id TEXT NOT NULL,
          user_id TEXT NOT NULL,
          user_name TEXT NOT NULL,
          role TEXT DEFAULT 'editor',
          last_active_at TEXT,
          is_online INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS yixiu_knowledge_links (
          id TEXT PRIMARY KEY,
          knowledge_id TEXT NOT NULL,
          link_type TEXT NOT NULL,
          target_id TEXT NOT NULL,
          target_title TEXT,
          created_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_knowledge_versions
          ON yixiu_knowledge_versions(knowledge_id, version);
        CREATE INDEX IF NOT EXISTS idx_knowledge_collaborators
          ON yixiu_knowledge_collaborators(knowledge_id);
        CREATE INDEX IF NOT EXISTS idx_knowledge_links
          ON yixiu_knowledge_links(knowledge_id);
        CREATE TABLE IF NOT EXISTS yixiu_doc_templates (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          icon TEXT DEFAULT '📝',
          category TEXT DEFAULT '通用',
          description TEXT DEFAULT '',
          skeleton_json TEXT DEFAULT '{}',
          is_builtin INTEGER DEFAULT 0,
          created_at TEXT
        );
        """
    )
    # 预置模板数据
    _seed_templates(conn)
    return conn


def _json(value, default):
    try:
        return json.loads(value) if value else default
    except (TypeError, ValueError):
        return default


def _file_type(filename: str, mime: str = "") -> str:
    ext = Path(filename).suffix.lower()
    if mime.startswith("image/") or ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}:
        return "图片"
    if mime == "application/pdf" or ext == ".pdf":
        return "PDF"
    if ext in {".doc", ".docx", ".wps"}:
        return "Word"
    if ext in {".xls", ".xlsx", ".csv"}:
        return "Excel"
    if mime.startswith("video/") or ext in {".mp4", ".webm", ".mov"}:
        return "视频"
    if mime.startswith("text/") or ext in {".txt", ".md", ".log"}:
        return "文本"
    return "其他"


def _file_dict(row) -> dict:
    item = dict(row)
    item["auditStatus"] = item.pop("audit_status")
    item["parseStatus"] = item.pop("parse_status")
    item["uploaded_at"] = item.get("uploaded_at", "")
    item["sizeBytes"] = item.pop("size", 0)
    size = item["sizeBytes"]
    item["size"] = f"{size / 1024 / 1024:.1f} MB" if size >= 1024 * 1024 else f"{max(size / 1024, 0.1):.1f} KB"
    item["analysis"] = _json(item.pop("analysis_json", "{}"), {})
    item["url"] = f"/api/yixiu/files/{item['id']}/content"
    return item


def _demo_tasks(status: str = "") -> list[dict]:
    try:
        from routes.maintenance_tasks import _get_demo_tasks
        return _get_demo_tasks(status)
    except Exception as exc:  # noqa: BLE001
        logger.warning("读取演示任务失败: %s", exc)
        return []


def _base_knowledge() -> list[dict]:
    if KNOWLEDGE_PATH.exists():
        try:
            return json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("读取基础知识库失败: %s", exc)
    return []


def _stored_knowledge() -> list[dict]:
    with _db() as conn:
        rows = conn.execute("SELECT * FROM yixiu_knowledge ORDER BY created_at DESC").fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["tags"] = _json(item.get("tags"), [])
        item["reviewable"] = True
        result.append(item)
    return result


def _task_payload(row) -> dict:
    item = _json(row["payload"], {})
    item.update({"id": row["id"], "status": row["status"], "completedSteps": _json(row["completed_steps"], [])})
    return item


def _ensure_task_row(conn: sqlite3.Connection, task_id: str):
    row = conn.execute("SELECT * FROM yixiu_tasks WHERE id=?", (task_id,)).fetchone()
    if row:
        return row
    demo = next((item for item in _demo_tasks("") if str(item.get("id")) == str(task_id)), None)
    if not demo:
        return None
    sop = demo.get("sop") or ["安全确认", "故障记录", "部件检测", "维修处置", "复测提交"]
    demo = {**demo, "sop": sop}
    conn.execute("INSERT INTO yixiu_tasks VALUES (?, ?, ?, ?, ?, ?)", (str(task_id), json.dumps(demo, ensure_ascii=False), demo.get("status", "pending"), "[]", demo.get("created_at", _now()), _now()))
    return conn.execute("SELECT * FROM yixiu_tasks WHERE id=?", (str(task_id),)).fetchone()


def _sop_for(category: str, level: str, fault: str) -> tuple[list[dict], list[str]]:
    category = category or "通用设备"
    level = level or "二级检修"
    fault = fault or "故障"
    steps = [
        {"title": "作业许可与安全隔离", "detail": f"确认{category}{level}作业票，执行停机、断电、验电和挂牌。", "required": True, "evidence": "安全确认"},
        {"title": "故障现象记录", "detail": f"记录{fault}出现条件、报警、温度、声音及现场图片，禁止带故障盲目拆机。", "required": True, "evidence": "数据或图片"},
        {"title": "按依据逐项检测", "detail": "按照召回手册和相似案例测量关键参数，先确认原因再更换部件。", "required": True, "evidence": "检测值"},
        {"title": "维修处置与过程复核", "detail": "执行紧固、清洁、调整或更换，记录工具、部件及关键扭矩。", "required": True, "evidence": "过程记录"},
        {"title": "复测验收", "detail": "恢复防护后试运行，对照标准复测并确认故障消除。", "required": True, "evidence": "复测结果"},
        {"title": "报告与知识沉淀", "detail": "提交检修报告、引用依据和证据；有效经验进入知识审核队列。", "required": True, "evidence": "检修报告"},
    ]
    safety = ["必须执行停机断电和挂牌上锁", "拆卸前确认温度、压力和残余能量", "检测结果异常时禁止直接恢复运行"]
    return steps, safety


def _fallback_image_analysis(filename: str) -> dict:
    return {
        "equipment": "待结合设备型号确认",
        "fault_signs": ["已接收现场图片", "需结合故障描述确认异常部位"],
        "risk_points": ["仅凭图片不能直接判定部件失效", "维修前必须完成安全隔离"],
        "analysis": f"图片 {filename} 已纳入跨模态检索，将与设备型号、故障现象和手册条目联合匹配。",
        "suggestion": "补充拍摄设备铭牌、异常部位全景和细节图，可提高检索准确度。",
        "provider": "local-fallback",
    }


def _analyze_image(path: Path, mime: str) -> dict:
    fallback = _fallback_image_analysis(path.name)
    try:
        from services.ai_gateway import ai_agent
        status = ai_agent.status()
        if not status.get("configured"):
            return fallback
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        text = ai_agent.vision(
            prompt="识别设备、异常部位、故障迹象和安全风险，给出简洁 JSON。",
            image_base64=f"data:{mime};base64,{encoded}",
            system_prompt="你是设备检修视觉分析助手。只根据可见证据描述，不确定内容必须标注待确认。",
        )
        parsed = ai_agent.parse_json(text)
        return parsed or {**fallback, "analysis": text, "provider": status.get("provider", "ai")}
    except Exception as exc:  # noqa: BLE001
        logger.warning("视觉模型不可用，使用本地回退: %s", exc)
        return fallback


@yixiu_bp.get("/overview")
def overview():
    tasks = _demo_tasks("")
    with _db() as conn:
        stored_tasks = [_task_payload(row) for row in conn.execute("SELECT * FROM yixiu_tasks ORDER BY created_at DESC").fetchall()]
        file_count = conn.execute("SELECT COUNT(*) FROM yixiu_files").fetchone()[0]
    tasks = stored_tasks + tasks
    knowledge = _stored_knowledge() + _base_knowledge()
    pending = [item for item in tasks if item.get("status") in {"pending", "in_progress"}]
    high = [item for item in tasks if item.get("severity") in {"high", "critical"}]
    return success_response({
        "name": "一修", "subtitle": "设备检修知识检索与标准作业系统", "updated_at": _now(),
        "stats": {"online_equipment": 128, "pending_tasks": len(pending), "high_risk_items": len(high), "knowledge_items": len(knowledge), "files": file_count},
        "agents": AGENTS, "modules": MODULES, "tasks": tasks[:8], "knowledge": knowledge[:8],
    }, "一修概览获取成功")


@yixiu_bp.get("/agents")
def agents():
    return success_response({"agents": AGENTS}, "智能体状态获取成功")


@yixiu_bp.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        status = request.args.get("status", "").strip()
        with _db() as conn:
            stored = [_task_payload(row) for row in conn.execute("SELECT * FROM yixiu_tasks ORDER BY created_at DESC").fetchall()]
        items = stored + _demo_tasks(status)
        if status:
            items = [item for item in items if item.get("status") == status]
        return success_response({"tasks": items, "total": len(items)}, "检修任务获取成功")

    data = request.get_json(silent=True) or {}
    task_id = f"task-{uuid.uuid4().hex[:10]}"
    category = data.get("category") or data.get("equipment_category") or "通用设备"
    level = data.get("maintenanceLevel") or data.get("maintenance_level") or "二级检修"
    fault = data.get("faultType") or data.get("fault_type") or data.get("description") or "待确认故障"
    generated_sop, safety = _sop_for(category, level, fault)
    task = {
        "id": task_id, "workOrderNo": data.get("workOrderNo") or f"YX-{datetime.now():%Y%m%d-%H%M%S}",
        "title": data.get("title") or f"{data.get('deviceName') or data.get('equipment_name') or '设备'}检修任务",
        "equipment_name": data.get("equipment_name") or data.get("deviceName") or "待登记设备",
        "equipment_no": data.get("equipment_no", ""), "equipment_model": data.get("equipment_model") or data.get("deviceModel") or "",
        "category": category, "maintenanceLevel": level, "fault_type": fault, "description": data.get("description", ""),
        "severity": data.get("severity", "medium"), "assignee_name": data.get("assignee_name", "待分配"),
        "current_step": "作业许可与安全隔离", "progress": 0, "due_at": data.get("due_at", ""), "created_at": _now(),
        "sop": data.get("sopDetails") or generated_sop, "tools": data.get("tools", []), "parts": data.get("parts", []),
        "safety": data.get("safety") or safety, "references": data.get("references", []),
    }
    with _db() as conn:
        conn.execute("INSERT INTO yixiu_tasks VALUES (?, ?, ?, ?, ?, ?)", (task_id, json.dumps(task, ensure_ascii=False), "pending", "[]", _now(), _now()))
    task.update({"status": "pending", "completedSteps": []})
    return success_response(task, "检修任务创建成功")


@yixiu_bp.put("/tasks/<task_id>/status")
def change_task_status(task_id: str):
    data = request.get_json(silent=True) or {}
    status = data.get("status", "pending")
    allowed = {"pending", "in_progress", "review", "completed", "paused", "rejected", "overdue"}
    if status not in allowed:
        return error_response(400, "无效的任务状态")
    with _db() as conn:
        if not _ensure_task_row(conn, task_id):
            return error_response(404, "任务不存在")
        conn.execute("UPDATE yixiu_tasks SET status=?, updated_at=? WHERE id=?", (status, _now(), task_id))
    return success_response({"task_id": task_id, "status": status, "operator": data.get("operator", "当前用户"), "operated_at": _now(), "note": data.get("note", "")}, "任务状态已更新")


@yixiu_bp.put("/tasks/<task_id>/steps/<int:step_index>")
def complete_task_step(task_id: str, step_index: int):
    data = request.get_json(silent=True) or {}
    with _db() as conn:
        row = _ensure_task_row(conn, task_id)
        if not row:
            return error_response(404, "任务不存在或不是本页面创建的任务")
        task = _task_payload(row)
        steps = task.get("sop", [])
        if step_index < 0 or step_index >= len(steps):
            return error_response(400, "作业步骤不存在")
        completed = _json(row["completed_steps"], [])
        if data.get("completed", True) and step_index not in completed:
            completed.append(step_index)
        elif not data.get("completed", True) and step_index in completed:
            completed.remove(step_index)
        completed.sort()
        progress = round(len(completed) / max(len(steps), 1) * 100)
        status = "review" if progress == 100 else "in_progress"
        conn.execute("UPDATE yixiu_tasks SET completed_steps=?, status=?, updated_at=? WHERE id=?", (json.dumps(completed), status, _now(), task_id))
    return success_response({"task_id": task_id, "completedSteps": completed, "progress": progress, "status": status, "evidence": data.get("evidence", "")}, "作业步骤已记录")


@yixiu_bp.post("/recheck")
def save_recheck():
    data = request.get_json(silent=True) or {}
    passed = data.get("result", "通过") == "通过"
    status = "completed" if passed else "in_progress"
    with _db() as conn:
        conn.execute("UPDATE yixiu_tasks SET status=?, updated_at=? WHERE id=?", (status, _now(), str(data.get("task_id", ""))))
    return success_response({"task_id": data.get("task_id"), "result": data.get("result", "通过"), "next_status": status, "comment": data.get("comment", ""), "reviewer": data.get("reviewer", "复检人员"), "reviewed_at": _now()}, "复检结果已保存")


@yixiu_bp.route("/files", methods=["GET", "POST"])
def files():
    if request.method == "GET":
        keyword = request.args.get("keyword", "").strip()
        with _db() as conn:
            rows = conn.execute("SELECT * FROM yixiu_files ORDER BY uploaded_at DESC").fetchall()
        items = [_file_dict(row) for row in rows]
        if keyword:
            items = [item for item in items if keyword in item["name"] or keyword in (item.get("equipment") or "")]
        return success_response({"files": items, "total": len(items)}, "文件列表获取成功")

    if "file" not in request.files:
        return error_response(400, "请选择需要上传的文件")
    upload = request.files["file"]
    if not upload.filename:
        return error_response(400, "文件名为空")
    original_name = Path(upload.filename).name
    ext = Path(original_name).suffix.lower()
    allowed = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt", ".md", ".mp4", ".webm"}
    if ext not in allowed:
        return error_response(400, "不支持的文件类型")
    file_id = f"file-{uuid.uuid4().hex[:12]}"
    stored_name = f"{file_id}{ext}"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "yixiu"
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / secure_filename(stored_name)
    upload.save(path)
    mime = upload.mimetype or mimetypes.guess_type(original_name)[0] or "application/octet-stream"
    kind = _file_type(original_name, mime)
    analysis = _analyze_image(path, mime) if kind == "图片" else {"summary": "文件已保存，等待知识解析与人工审核。"}
    form = request.form
    with _db() as conn:
        conn.execute(
            "INSERT INTO yixiu_files VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (file_id, original_name, stored_name, mime, kind, form.get("category", "现场资料"), form.get("folder", "现场资料"), path.stat().st_size, form.get("equipment", ""), form.get("model", ""), form.get("uploader", "当前用户"), _now(), "待审核", "解析成功" if kind == "图片" else "等待解析", form.get("version", "v1.0"), form.get("purpose", "knowledge"), json.dumps(analysis, ensure_ascii=False)),
        )
        row = conn.execute("SELECT * FROM yixiu_files WHERE id=?", (file_id,)).fetchone()
    return success_response(_file_dict(row), "文件上传成功")


@yixiu_bp.get("/files/<file_id>/content")
def file_content(file_id: str):
    with _db() as conn:
        row = conn.execute("SELECT * FROM yixiu_files WHERE id=?", (file_id,)).fetchone()
    if not row:
        return error_response(404, "文件不存在")
    path = Path(current_app.config["UPLOAD_FOLDER"]) / "yixiu" / row["stored_name"]
    if not path.exists():
        return error_response(404, "文件内容不存在")
    return send_file(path, mimetype=row["mime"], download_name=row["name"])


@yixiu_bp.post("/search")
def search():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query") or data.get("description") or "").strip()
    device = str(data.get("deviceName") or data.get("device_name") or "设备").strip()
    model = str(data.get("deviceModel") or data.get("device_model") or "待确认型号").strip()
    category = str(data.get("category") or "通用设备").strip()
    fault = str(data.get("faultType") or data.get("fault_type") or "待确认故障").strip()
    level = str(data.get("maintenanceLevel") or "二级检修").strip()
    file_ids = data.get("fileIds") or []
    attachments = []
    if file_ids:
        marks = ",".join("?" for _ in file_ids)
        with _db() as conn:
            rows = conn.execute(f"SELECT * FROM yixiu_files WHERE id IN ({marks})", tuple(file_ids)).fetchall()
        attachments = [_file_dict(row) for row in rows]
    images = [item for item in attachments if item["type"] == "图片"]
    docs = [item for item in attachments if item["type"] != "图片"]
    steps, safety = _sop_for(category, level, fault)
    knowledge = _stored_knowledge() + _base_knowledge()
    terms = [term for term in [query, device, model, fault] if term]
    ranked = []
    for index, item in enumerate(knowledge):
        haystack = json.dumps(item, ensure_ascii=False)
        score = sum(1 for term in terms if term.lower() in haystack.lower())
        if score or index < 4:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    matched = [item for _, item in ranked[:6]]
    visual_findings = []
    for image in images:
        visual_findings.extend(image.get("analysis", {}).get("fault_signs", []))
    confidence = min(96, 82 + (6 if images else 0) + (3 if docs else 0) + (3 if model != "待确认型号" else 0))
    causes = [f"{fault}相关部件存在调整、磨损或连接异常", "运行参数或装配状态偏离手册要求", "需结合检测值排除供电、润滑或压力因素"]
    return success_response({
        "query": query, "device_name": device, "device_model": model, "category": category, "maintenance_level": level,
        "modalities": ["text", "equipment_model"] + (["image"] if images else []) + (["document"] if docs else []),
        "match_score": confidence, "phenomenon_summary": f"{device}（{model}）{fault}联合检索结果",
        "risk": "high" if any(word in query for word in ["冒烟", "漏电", "起火", "严重", "高温"]) else "medium",
        "stop_advice": "先完成安全隔离和数据记录，再按引用依据检修",
        "causes": causes, "positions": ["故障关联部件", "连接与紧固位置", "供电/润滑/压力回路"],
        "tools": ["万用表", "测温仪", "扭矩工具"], "visual_findings": visual_findings,
        "attachments": attachments, "matched_manuals": matched,
        "recommended_sop": steps, "safety": safety,
        "audit": {"risk_level": "medium", "must_check": ["安全隔离", "引用依据", "检测数据", "复测记录", "现场证据"], "auditor": "明鉴"},
    }, "多模态检索完成")


@yixiu_bp.route("/knowledge", methods=["GET"])
def knowledge():
    keyword = request.args.get("keyword", "").strip()
    items = _stored_knowledge() + _base_knowledge()
    if keyword:
        items = [item for item in items if keyword.lower() in json.dumps(item, ensure_ascii=False).lower()]
    return success_response({"items": items, "total": len(items)}, "知识资料获取成功")


@yixiu_bp.post("/knowledge/update")
def update_knowledge():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    summary = str(data.get("summary", "")).strip()
    if not title or not summary:
        return error_response(400, "知识标题和沉淀摘要不能为空")
    item_id = f"kb-{uuid.uuid4().hex[:12]}"
    tags = data.get("tags") or ["设备检修", "经验总结"]
    content = data.get("content") or f"# {title}\n\n## 适用范围\n- 设备：{data.get('equipment') or '待补充'}\n- 型号：{data.get('model') or '通用'}\n\n## 故障现象与经验\n{summary}\n\n## 安全与复核\n提交内容须经人工审核，确认引用依据、适用范围和安全风险后方可入库。"
    with _db() as conn:
        conn.execute("INSERT INTO yixiu_knowledge VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (item_id, title, data.get("type", "历史故障案例"), data.get("category", "案例"), data.get("equipment", ""), data.get("model", ""), summary, content, json.dumps(tags, ensure_ascii=False), data.get("source", "一线经验提交"), "pending", "", "", _now(), _now()))
        row = conn.execute("SELECT * FROM yixiu_knowledge WHERE id=?", (item_id,)).fetchone()
    item = dict(row)
    item["tags"] = _json(item["tags"], [])
    item["reviewable"] = True
    return success_response(item, "知识条目已进入人工审核队列")


@yixiu_bp.put("/knowledge/<item_id>/review")
def review_knowledge(item_id: str):
    data = request.get_json(silent=True) or {}
    status = data.get("status", "approved")
    if status not in {"approved", "rejected", "pending"}:
        return error_response(400, "无效的审核状态")
    correction = str(data.get("correction", "")).strip()
    tags = data.get("tags")
    with _db() as conn:
        row = conn.execute("SELECT * FROM yixiu_knowledge WHERE id=?", (item_id,)).fetchone()
        if not row:
            return error_response(404, "知识条目不存在")
        summary = correction or row["summary"]
        tag_value = json.dumps(tags, ensure_ascii=False) if isinstance(tags, list) else row["tags"]
        conn.execute("UPDATE yixiu_knowledge SET status=?, reviewer=?, correction=?, summary=?, tags=?, updated_at=? WHERE id=?", (status, data.get("reviewer", "当前审核人"), correction, summary, tag_value, _now(), item_id))
    return success_response({"id": item_id, "status": status, "summary": summary, "tags": _json(tag_value, []), "reviewer": data.get("reviewer", "当前审核人"), "updated_at": _now(), "graph_synced": status == "approved"}, "审核结果已保存并同步知识状态")


@yixiu_bp.post("/assistant/chat")
def assistant_chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    file_ids = data.get("fileIds") or []
    if not message and not file_ids:
        return error_response(400, "请输入问题或上传现场资料")
    attachments = []
    if file_ids:
        marks = ",".join("?" for _ in file_ids)
        with _db() as conn:
            attachments = [_file_dict(row) for row in conn.execute(f"SELECT * FROM yixiu_files WHERE id IN ({marks})", tuple(file_ids)).fetchall()]
    findings = []
    risks = []
    for item in attachments:
        analysis = item.get("analysis") or {}
        findings.extend(analysis.get("fault_signs") or analysis.get("findings") or [])
        risks.extend(analysis.get("risk_points") or [])
    context = f"已结合 {len(attachments)} 个附件进行分析。" if attachments else ""
    evidence = f"图像线索：{'、'.join(dict.fromkeys(findings))}。" if findings else ""
    risk_text = f"风险提示：{'、'.join(dict.fromkeys(risks))}。" if risks else ""
    answer = f"{context}{evidence}{risk_text}建议先确认设备型号和安全状态，再依据故障现象检索手册与相似案例；检测结果异常时再进入拆检或更换步骤。"
    return success_response({
        "response": answer,
        "modalities": ["text"] + (["image" if any(item.get("type") == "图片" for item in attachments) else "file"] if attachments else []),
        "findings": findings, "risk_points": risks, "attachments": attachments,
        "references": ["设备维修手册", "标准作业流程", "历史故障案例"], "agent": data.get("agent", "观微"),
    }, "智能检修助手已完成多模态分析")


@yixiu_bp.post("/audit")
def audit():
    data = request.get_json(silent=True) or {}
    checks = [
        ("引用手册或知识库依据", bool(data.get("references"))),
        ("完成安全确认与断电验电", bool(data.get("safety_checked"))),
        ("记录故障现象和检测数据", bool(data.get("measurements"))),
        ("完成复测确认", bool(data.get("retested"))),
        ("提交现场证据或报告", bool(data.get("report_ready"))),
    ]
    checklist = [{"item": item, "passed": passed} for item, passed in checks]
    score = round(sum(1 for _, passed in checks if passed) / len(checks) * 100)
    return success_response({"passed": score == 100, "score": score, "checklist": checklist, "suggestion": "可归档并提交知识沉淀" if score == 100 else "请补齐未通过项目后再提交验收"}, "核查完成")


@yixiu_bp.get("/contacts")
def contacts():
    with _db() as conn:
        rows = conn.execute("SELECT * FROM yixiu_contacts ORDER BY updated_at DESC").fetchall()
    stored = []
    for row in rows:
        item = dict(row)
        item["devices"] = _json(item.pop("devices", "[]"), [])
        item["currentTask"] = item.pop("current_task", "")
        item["employeeId"] = item.pop("employee_id", "")
        stored.append(item)
    merged = list(CONTACTS)
    known = {str(item.get("id")) for item in merged}
    merged.extend(item for item in stored if str(item.get("id")) not in known)
    return success_response({"contacts": merged, "total": len(merged)}, "contacts loaded")


@yixiu_bp.put("/contacts/<contact_id>")
def upsert_contact(contact_id: str):
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    if not name:
        return error_response("contact name is required", 400)
    now = _now()
    with _db() as conn:
        conn.execute(
            """INSERT INTO yixiu_contacts
               (id, account, name, avatar, position, department, specialty, phone,
                status, devices, current_task, workload, employee_id, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET account=excluded.account, name=excluded.name,
               avatar=excluded.avatar, position=excluded.position, department=excluded.department,
               specialty=excluded.specialty, phone=excluded.phone, status=excluded.status,
               devices=excluded.devices, current_task=excluded.current_task,
               workload=excluded.workload, employee_id=excluded.employee_id, updated_at=excluded.updated_at""",
            (contact_id, data.get("account"), name, data.get("avatar", ""),
             data.get("position", "maintenance worker"), data.get("department", "unassigned"),
             data.get("specialty", "maintenance"), data.get("phone", ""), data.get("status", "online"),
             json.dumps(data.get("devices", []), ensure_ascii=False), data.get("currentTask", ""),
             int(data.get("workload", 0) or 0), data.get("employeeId", ""), now),
        )
    return success_response({**data, "id": contact_id, "updated_at": now}, "contact synchronized")


@yixiu_bp.get("/conversations/<conversation_id>/messages")
def conversation_messages(conversation_id: str):
    with _db() as conn:
        rows = conn.execute("SELECT * FROM yixiu_messages WHERE conversation_id=? ORDER BY created_at ASC LIMIT 500", (conversation_id,)).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["attachment"] = _json(item.pop("attachment_json", "{}"), {})
        item["card"] = _json(item.pop("card_json", "{}"), {})
        items.append(item)
    return success_response({"messages": items}, "messages loaded")


@yixiu_bp.post("/conversations/<conversation_id>/messages")
def create_conversation_message(conversation_id: str):
    data = request.get_json(silent=True) or {}
    if not str(data.get("text", "")).strip() and not data.get("attachment") and not data.get("card"):
        return error_response("message content is required", 400)
    message_id = str(data.get("id") or uuid.uuid4())
    created_at = str(data.get("created_at") or _now())
    with _db() as conn:
        conn.execute(
            """INSERT INTO yixiu_messages
               (id, conversation_id, sender_id, sender_name, message_type, text,
                attachment_json, card_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (message_id, conversation_id, data.get("sender_id"), data.get("sender_name"),
             data.get("message_type", "text"), data.get("text", ""),
             json.dumps(data.get("attachment") or {}, ensure_ascii=False),
             json.dumps(data.get("card") or {}, ensure_ascii=False), created_at),
        )
    return success_response({**data, "id": message_id, "conversation_id": conversation_id, "created_at": created_at}, "message created")


def _ensure_knowledge_in_db(conn: sqlite3.Connection, item_id: str):
    """确保知识条目存在于数据库中。如果来自基础JSON，则复制到数据库。"""
    row = conn.execute("SELECT * FROM yixiu_knowledge WHERE id=?", (item_id,)).fetchone()
    if row:
        return row
    for item in _base_knowledge():
        if str(item.get("id")) == str(item_id):
            raw_content = item.get("content", "")
            content_str = "\n".join(raw_content) if isinstance(raw_content, list) else str(raw_content)
            summary = item.get("summary") or content_str[:200]
            conn.execute(
                "INSERT INTO yixiu_knowledge VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (str(item_id), item.get("title", "未命名"), item.get("type", "手册"),
                 item.get("category", "知识条目"), item.get("equipment_category") or item.get("equipment", ""),
                 item.get("equipment_model") or item.get("model", ""), summary,
                 content_str, json.dumps(item.get("tags", item.get("keywords", [])), ensure_ascii=False),
                 item.get("source", "基础知识库"), "approved", "", "", _now(), _now()),
            )
            return conn.execute("SELECT * FROM yixiu_knowledge WHERE id=?", (item_id,)).fetchone()
    return None


@yixiu_bp.put("/knowledge/<item_id>/content")
def edit_knowledge_content(item_id: str):
    """编辑保存知识条目内容，自动生成版本快照。"""
    data = request.get_json(silent=True) or {}
    content = str(data.get("content", "")).strip()
    if not content:
        return error_response(400, "内容不能为空")
    with _db() as conn:
        row = _ensure_knowledge_in_db(conn, item_id)
        if not row:
            return error_response(404, "知识条目不存在")
        current_version = conn.execute(
            "SELECT MAX(version) as v FROM yixiu_knowledge_versions WHERE knowledge_id=?", (item_id,)
        ).fetchone()["v"] or 1
        new_version = current_version + 1
        title = data.get("title") or row["title"]
        tags = data.get("tags")
        tag_value = json.dumps(tags, ensure_ascii=False) if isinstance(tags, list) else row["tags"]
        equipment = data.get("equipment") or row["equipment"]
        model = data.get("model") or row["model"]
        summary = data.get("summary") or (content[:200] if content else row["summary"])
        conn.execute(
            "UPDATE yixiu_knowledge SET title=?, content=?, tags=?, equipment=?, model=?, summary=?, status=?, updated_at=? WHERE id=?",
            (title, content, tag_value, equipment, model, summary, "pending", _now(), item_id),
        )
        version_id = f"ver-{uuid.uuid4().hex[:12]}"
        conn.execute(
            "INSERT INTO yixiu_knowledge_versions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (version_id, item_id, new_version, content, title,
             data.get("change_summary", ""), data.get("editor_id", ""),
             data.get("editor_name", "当前用户"), _now()),
        )
        updated = conn.execute("SELECT * FROM yixiu_knowledge WHERE id=?", (item_id,)).fetchone()
    item = dict(updated)
    item["tags"] = _json(item["tags"], [])
    item["version"] = new_version
    item["reviewable"] = True
    return success_response(item, "知识内容已保存，版本 v%d" % new_version)


@yixiu_bp.get("/knowledge/<item_id>/versions")
def knowledge_versions(item_id: str):
    """获取知识条目的版本历史。"""
    with _db() as conn:
        rows = conn.execute(
            "SELECT * FROM yixiu_knowledge_versions WHERE knowledge_id=? ORDER BY version DESC",
            (item_id,),
        ).fetchall()
    items = [dict(row) for row in rows]
    return success_response({"versions": items, "total": len(items)}, "版本历史获取成功")


@yixiu_bp.get("/knowledge/<item_id>/versions/<version_id>")
def knowledge_version_detail(item_id: str, version_id: str):
    """获取某个版本的详细内容。"""
    with _db() as conn:
        row = conn.execute(
            "SELECT * FROM yixiu_knowledge_versions WHERE id=? AND knowledge_id=?",
            (version_id, item_id),
        ).fetchone()
    if not row:
        return error_response(404, "版本不存在")
    return success_response(dict(row), "版本内容获取成功")


@yixiu_bp.post("/knowledge/<item_id>/versions/<version_id>/restore")
def restore_knowledge_version(item_id: str, version_id: str):
    """恢复到指定版本。"""
    with _db() as conn:
        row = _ensure_knowledge_in_db(conn, item_id)
        if not row:
            return error_response(404, "知识条目不存在")
        ver = conn.execute(
            "SELECT * FROM yixiu_knowledge_versions WHERE id=? AND knowledge_id=?",
            (version_id, item_id),
        ).fetchone()
        if not ver:
            return error_response(404, "版本不存在")
        current_version = conn.execute(
            "SELECT MAX(version) as v FROM yixiu_knowledge_versions WHERE knowledge_id=?", (item_id,)
        ).fetchone()["v"] or 1
        new_version = current_version + 1
        conn.execute(
            "UPDATE yixiu_knowledge SET content=?, title=?, status=?, updated_at=? WHERE id=?",
            (ver["content_snapshot"], ver["title_snapshot"], "pending", _now(), item_id),
        )
        restore_id = f"ver-{uuid.uuid4().hex[:12]}"
        conn.execute(
            "INSERT INTO yixiu_knowledge_versions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (restore_id, item_id, new_version, ver["content_snapshot"], ver["title_snapshot"],
             "恢复到 v%d" % ver["version"], "", "当前用户", _now()),
        )
    return success_response({"id": item_id, "restored_version": ver["version"], "new_version": new_version}, "已恢复到 v%d" % ver["version"])


@yixiu_bp.get("/knowledge/<item_id>/collaborators")
def knowledge_collaborators(item_id: str):
    """获取知识条目的协作成员列表。"""
    with _db() as conn:
        rows = conn.execute(
            "SELECT * FROM yixiu_knowledge_collaborators WHERE knowledge_id=? ORDER BY last_active_at DESC",
            (item_id,),
        ).fetchall()
    items = [dict(row) for row in rows]
    return success_response({"collaborators": items, "total": len(items)}, "协作成员获取成功")


@yixiu_bp.post("/knowledge/<item_id>/collaborators")
def add_knowledge_collaborator(item_id: str):
    """添加协作成员。"""
    data = request.get_json(silent=True) or {}
    user_id = str(data.get("user_id") or data.get("userId") or data.get("name") or "guest")
    user_name = str(data.get("user_name") or data.get("userName") or data.get("name") or "新成员")
    role = str(data.get("role", "editor"))
    now = _now()
    collab_id = f"col-{uuid.uuid4().hex[:10]}"
    with _db() as conn:
        conn.execute(
            "INSERT INTO yixiu_knowledge_collaborators VALUES (?, ?, ?, ?, ?, ?, ?)",
            (collab_id, item_id, user_id, user_name, role, now, 1),
        )
    return success_response({
        "id": collab_id, "knowledge_id": item_id,
        "user_id": user_id, "user_name": user_name, "role": role,
    }, "协作成员添加成功")


@yixiu_bp.post("/knowledge/<item_id>/presence")
def knowledge_presence(item_id: str):
    """上报在线状态（心跳）。"""
    data = request.get_json(silent=True) or {}
    user_id = str(data.get("user_id") or data.get("userId") or "guest")
    user_name = str(data.get("user_name") or data.get("userName") or "当前用户")
    now = _now()
    with _db() as conn:
        existing = conn.execute(
            "SELECT * FROM yixiu_knowledge_collaborators WHERE knowledge_id=? AND user_id=?",
            (item_id, user_id),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE yixiu_knowledge_collaborators SET is_online=1, last_active_at=? WHERE id=?",
                (now, existing["id"]),
            )
        else:
            collab_id = f"col-{uuid.uuid4().hex[:10]}"
            conn.execute(
                "INSERT INTO yixiu_knowledge_collaborators VALUES (?, ?, ?, ?, ?, ?, ?)",
                (collab_id, item_id, user_id, user_name, "editor", now, 1),
            )
        rows = conn.execute(
            "SELECT * FROM yixiu_knowledge_collaborators WHERE knowledge_id=? AND is_online=1",
            (item_id,),
        ).fetchall()
    online = [dict(row) for row in rows]
    return success_response({"online_members": online, "count": len(online)}, "在线状态已更新")


@yixiu_bp.route("/knowledge/<item_id>/links", methods=["GET", "POST"])
def knowledge_links(item_id: str):
    """获取或添加知识条目的板块联动关联。"""
    if request.method == "GET":
        with _db() as conn:
            rows = conn.execute(
                "SELECT * FROM yixiu_knowledge_links WHERE knowledge_id=? ORDER BY created_at DESC",
                (item_id,),
            ).fetchall()
        items = [dict(row) for row in rows]
        return success_response({"links": items, "total": len(items)}, "联动关联获取成功")

    data = request.get_json(silent=True) or {}
    link_type = str(data.get("link_type", "")).strip()
    target_id = str(data.get("target_id", "")).strip()
    target_title = str(data.get("target_title", "")).strip()
    if link_type not in {"task", "knowledge", "file"} or not target_id:
        return error_response(400, "关联类型和目标ID不能为空")
    link_id = f"link-{uuid.uuid4().hex[:10]}"
    with _db() as conn:
        conn.execute(
            "INSERT INTO yixiu_knowledge_links VALUES (?, ?, ?, ?, ?, ?)",
            (link_id, item_id, link_type, target_id, target_title, _now()),
        )
    return success_response({"id": link_id, "knowledge_id": item_id, "link_type": link_type,
                             "target_id": target_id, "target_title": target_title, "created_at": _now()}, "关联添加成功")


@yixiu_bp.route("/knowledge/<item_id>/links/<link_id>", methods=["DELETE"])
def remove_knowledge_link(item_id: str, link_id: str):
    """移除板块联动关联。"""
    with _db() as conn:
        row = conn.execute("SELECT * FROM yixiu_knowledge_links WHERE id=? AND knowledge_id=?", (link_id, item_id)).fetchone()
        if not row:
            return error_response(404, "关联不存在")
        conn.execute("DELETE FROM yixiu_knowledge_links WHERE id=?", (link_id,))
    return success_response({"id": link_id}, "关联已移除")


@yixiu_bp.get("/knowledge/linked/<link_type>/<target_id>")
def linked_knowledge(link_type: str, target_id: str):
    """反向查询：根据关联类型和目标ID查找关联的知识条目。"""
    with _db() as conn:
        rows = conn.execute(
            """SELECT k.*, l.target_id, l.target_title, l.id as link_id
               FROM yixiu_knowledge k
               JOIN yixiu_knowledge_links l ON k.id = l.knowledge_id
               WHERE l.link_type=? AND l.target_id=?""",
            (link_type, target_id),
        ).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["tags"] = _json(item.get("tags"), [])
        items.append(item)
    return success_response({"items": items, "total": len(items)}, "关联知识获取成功")


@yixiu_bp.route("/templates")
def list_templates():
    keyword = request.args.get("keyword", "").strip()
    with _db() as conn:
        rows = conn.execute(
            "SELECT * FROM yixiu_doc_templates WHERE name LIKE ? OR category LIKE ? ORDER BY is_builtin DESC, created_at DESC",
            (f"%{keyword}%", f"%{keyword}%"),
        ).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["skeleton"] = _json(item.get("skeleton_json"), {})
        items.append(item)
    return success_response({"templates": items, "total": len(items)})


@yixiu_bp.route("/templates/<template_id>")
def get_template(template_id):
    with _db() as conn:
        row = conn.execute("SELECT * FROM yixiu_doc_templates WHERE id=?", (template_id,)).fetchone()
    if not row:
        return error_response(404, "模板不存在")
    item = dict(row)
    item["skeleton"] = _json(item.get("skeleton_json"), {})
    return success_response(item)


@yixiu_bp.route("/templates", methods=["POST"])
def create_template():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    if not name:
        return error_response(400, "模板名称不能为空")
    template_id = f"tpl-{uuid.uuid4().hex[:10]}"
    skeleton = data.get("skeleton", {})
    with _db() as conn:
        conn.execute(
            "INSERT INTO yixiu_doc_templates VALUES (?, ?, ?, ?, ?, ?, 0, ?)",
            (template_id, name, str(data.get("icon", "📝")),
             str(data.get("category", "通用")), str(data.get("description", "")),
             json.dumps(skeleton, ensure_ascii=False), _now()),
        )
    return success_response({"id": template_id, "name": name}, "模板创建成功")


@yixiu_bp.route("/templates/<template_id>", methods=["DELETE"])
def delete_template(template_id):
    with _db() as conn:
        row = conn.execute("SELECT * FROM yixiu_doc_templates WHERE id=?", (template_id,)).fetchone()
        if not row:
            return error_response(404, "模板不存在")
        if row["is_builtin"]:
            return error_response(403, "内置模板不可删除")
        conn.execute("DELETE FROM yixiu_doc_templates WHERE id=?", (template_id,))
    return success_response({"id": template_id}, "模板已删除")
