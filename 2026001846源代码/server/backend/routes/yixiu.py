import logging
import json
import os
from datetime import datetime

from flask import Blueprint, request

from utils import success_response

logger = logging.getLogger(__name__)
yixiu_bp = Blueprint('yixiu', __name__)


AGENTS = [
    {
        'id': 'retrieval',
        'name': '检索智能体',
        'role': '多模态资料召回',
        'duty': '解析故障描述、现场图片和设备型号，召回维修手册、相似案例和标准作业流程。',
        'status': 'online',
    },
    {
        'id': 'procedure',
        'name': '作业智能体',
        'role': '标准作业编排',
        'duty': '将检索结果转成安全确认、检测、维修、复测和报告提交步骤。',
        'status': 'online',
    },
    {
        'id': 'knowledge',
        'name': '知识智能体',
        'role': '知识沉淀与图谱维护',
        'duty': '审核现场案例，提取故障、部件、工具、风险和处置关系。',
        'status': 'online',
    },
    {
        'id': 'collaboration',
        'name': '协作智能体',
        'role': '现场协同',
        'duty': '连接负责人、专家和验收人员，支撑任务沟通与现场支援。',
        'status': 'online',
    },
    {
        'id': 'audit',
        'name': '核查智能体',
        'role': '结果复核',
        'duty': '检查引用依据、作业合规、安全风险遗漏和报告完整性。',
        'status': 'online',
    },
]


MODULES = [
    {
        'key': 'multimodal_search',
        'title': '多模态知识检索',
        'desc': '支持文本、图片、语音和设备型号联合检索。',
        'agent': '检索智能体',
    },
    {
        'key': 'standard_work',
        'title': '标准作业闭环',
        'desc': '覆盖任务创建、SOP 步骤、状态流转、复测验收和报告提交。',
        'agent': '作业智能体',
    },
    {
        'key': 'knowledge_graph',
        'title': '知识图谱沉淀',
        'desc': '沉淀手册条款、故障案例、设备部件和检修经验。',
        'agent': '知识智能体',
    },
    {
        'key': 'quality_audit',
        'title': '安全与质量核查',
        'desc': '复核检索依据、风险提醒、操作顺序和报告字段。',
        'agent': '核查智能体',
    },
]


def _demo_tasks(status=''):
    try:
        from routes.maintenance_tasks import _get_demo_tasks

        return _get_demo_tasks(status)
    except Exception as exc:  # noqa: BLE001
        logger.warning('读取演示检修任务失败: %s', exc)
        return []


def _demo_knowledge():
    kb_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'data', 'maintenance_knowledge_base.json')
    )
    if os.path.exists(kb_path):
        try:
            with open(kb_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as exc:  # noqa: BLE001
            logger.warning('读取一修设备检修知识库失败: %s', exc)

    try:
        from routes.maintenance_tasks import _get_demo_knowledge

        return _get_demo_knowledge()
    except Exception as exc:  # noqa: BLE001
        logger.warning('读取演示知识库失败: %s', exc)
        return []


@yixiu_bp.route('/overview', methods=['GET'])
def overview():
    """一修网页版首页概览。"""
    tasks = _demo_tasks('')
    knowledge_items = _demo_knowledge()
    high_risk = [task for task in tasks if task.get('severity') in ('high', 'critical')]
    pending = [task for task in tasks if task.get('status') in ('pending', 'in_progress')]

    return success_response(
        {
            'name': '一修',
            'subtitle': '基于多模态大模型技术的设备检修知识检索与作业系统',
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stats': {
                'online_equipment': 128,
                'pending_tasks': len(pending) or 8,
                'high_risk_items': len(high_risk) or 3,
                'knowledge_items': len(knowledge_items) or 156,
            },
            'agents': AGENTS,
            'modules': MODULES,
            'tasks': tasks[:4],
            'knowledge': knowledge_items[:4],
        },
        '一修概览获取成功',
    )


@yixiu_bp.route('/agents', methods=['GET'])
def agents():
    """多智能体分工。"""
    return success_response({'agents': AGENTS}, '多智能体状态获取成功')


@yixiu_bp.route('/tasks', methods=['GET'])
def tasks():
    """检修任务兼容查询入口。"""
    status = request.args.get('status', '').strip()
    items = _demo_tasks(status)
    return success_response({'tasks': items, 'total': len(items)}, '检修任务获取成功')


@yixiu_bp.route('/knowledge', methods=['GET'])
def knowledge():
    """检修知识库兼容查询入口。"""
    keyword = request.args.get('keyword', '').strip()
    items = _demo_knowledge()
    if keyword:
        items = [
            item for item in items
            if keyword in item.get('title', '') or keyword in item.get('fault_type', '') or keyword in item.get('source', '')
        ]
    return success_response({'items': items, 'total': len(items)}, '检修知识获取成功')


@yixiu_bp.route('/search', methods=['POST'])
def search():
    """A1 演示用多模态检索编排入口。"""
    data = request.get_json(silent=True) or {}
    query = str(data.get('query') or data.get('question') or data.get('description') or '').strip()
    device_model = str(data.get('device_model') or data.get('deviceModel') or 'CG-125').strip()
    has_image = bool(data.get('image_url') or data.get('image_base64'))

    if not query:
        query = '发动机启动后异响并伴随怠速不稳'

    return success_response(
        {
            'query': query,
            'device_model': device_model,
            'modalities': ['text'] + (['image'] if has_image else []),
            'match_score': 92 if has_image else 88,
            'matched_manuals': [
                {
                    'title': '摩托车发动机维修手册',
                    'chapter': '点火系统与气门机构检查',
                    'confidence': '高',
                },
                {
                    'title': 'CG-125 标准检修流程',
                    'chapter': '异响与怠速不稳联合排查',
                    'confidence': '中高',
                },
            ],
            'similar_cases': [
                {
                    'title': 'CG-125 热车后气门区异响',
                    'similarity': '91%',
                    'solution': '复核气门间隙，检查正时链条张紧器。',
                },
                {
                    'title': '点火线圈接触不良导致怠速波动',
                    'similarity': '84%',
                    'solution': '检查高压包插接件和火花塞间隙。',
                },
            ],
            'recommended_sop': [
                '安全确认并断电停机',
                '记录故障声音、转速和温度',
                '检查火花塞间隙与点火线圈连接',
                '复核气门间隙和正时链条张紧状态',
                '复测怠速稳定性并提交检修报告',
            ],
            'audit': {
                'risk_level': 'medium',
                'must_check': ['防烫伤', '防误启动', '复测记录', '照片证据'],
                'auditor': '核查智能体',
            },
        },
        '多模态检索编排完成',
    )


@yixiu_bp.route('/audit', methods=['POST'])
def audit():
    """检修结果核查入口。"""
    data = request.get_json(silent=True) or {}
    checklist = [
        {'item': '是否引用手册或知识库依据', 'passed': bool(data.get('references', True))},
        {'item': '是否完成安全确认与断电验电', 'passed': bool(data.get('safety_checked', True))},
        {'item': '是否记录故障现象和检测数据', 'passed': bool(data.get('measurements', True))},
        {'item': '是否完成复测确认', 'passed': bool(data.get('retested', True))},
        {'item': '是否提交现场照片或报告', 'passed': bool(data.get('report_ready', True))},
    ]
    passed = all(item['passed'] for item in checklist)
    return success_response(
        {
            'passed': passed,
            'score': 96 if passed else 78,
            'checklist': checklist,
            'suggestion': '可归档为标准案例' if passed else '请补齐未通过项后再提交验收',
        },
        '核查完成',
    )

YIXIU_FILES = [
    {
        'id': 'file-001',
        'name': '摩托车发动机维修手册.pdf',
        'type': 'PDF',
        'category': '维修手册',
        'folder': '发动机资料',
        'size': '18.2 MB',
        'equipment': '摩托车发动机总成',
        'model': 'CG-125',
        'uploader': '李宗泽',
        'uploaded_at': '2026-07-28 10:12',
        'updated_at': '2026-07-30 11:30',
        'auditStatus': '已通过',
        'parseStatus': '解析成功',
        'version': 'v1.2',
        'knowledgeLinks': 8,
        'downloads': 36,
        'url': '/static/manuals/摩托车发动机维修手册.pdf',
        'favorite': True,
    },
    {
        'id': 'file-002',
        'name': 'ZK-320 配电柜过热 SOP.docx',
        'type': 'Word',
        'category': '标准作业流程',
        'folder': '电气系统',
        'size': '864 KB',
        'equipment': '配电柜',
        'model': 'ZK-320',
        'uploader': '唐忆哲',
        'uploaded_at': '2026-07-25 16:40',
        'updated_at': '2026-07-25 16:40',
        'auditStatus': '审核中',
        'parseStatus': '解析中',
        'version': 'v1.0',
        'knowledgeLinks': 3,
        'downloads': 12,
        'url': '',
        'favorite': False,
    },
]

YIXIU_CONTACTS = [
    {'id': 1, 'name': '李宗泽', 'avatar': '/static/avatar-1.png', 'position': '检修工程师', 'department': '动力设备检修一组', 'specialty': '发动机/电气', 'phone': '138-0000-1024', 'status': '在线', 'currentTask': 'ZK-320 过热检修', 'devices': ['CG-125', 'ZK-320'], 'workload': 72},
    {'id': 2, 'name': '唐忆哲', 'avatar': '/static/avatar-2.png', 'position': '复检人员', 'department': '质量复检组', 'specialty': '复检评估', 'phone': '138-0000-2048', 'status': '在线', 'currentTask': '火花塞定检复核', 'devices': ['DLI-001'], 'workload': 48},
    {'id': 3, 'name': '赵宁', 'avatar': '/static/avatar-3.png', 'position': '安全负责人', 'department': '安全管理部', 'specialty': '高风险作业', 'phone': '138-0000-4096', 'status': '忙碌', 'currentTask': '高风险作业确认', 'devices': ['配电柜', '液压系统'], 'workload': 83},
]


@yixiu_bp.route('/files', methods=['GET'])
def files():
    keyword = request.args.get('keyword', '').strip()
    files_list = YIXIU_FILES
    if keyword:
        files_list = [item for item in files_list if keyword in item.get('name', '') or keyword in item.get('equipment', '')]
    return success_response({'files': files_list, 'total': len(files_list)}, '文件列表获取成功')


@yixiu_bp.route('/files', methods=['POST'])
def create_file_record():
    data = request.get_json(silent=True) or {}
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_record = {
        'id': f"file-{int(datetime.now().timestamp())}",
        'name': data.get('name', '未命名检修资料'),
        'type': data.get('type', '其他'),
        'category': data.get('category', '其他技术资料'),
        'folder': data.get('folder', '未分类'),
        'size': data.get('size', '0 KB'),
        'equipment': data.get('equipment', ''),
        'model': data.get('model', ''),
        'uploader': data.get('uploader', '当前用户'),
        'uploaded_at': now,
        'updated_at': now,
        'auditStatus': '待审核',
        'parseStatus': '等待解析',
        'version': data.get('version', 'v1.0'),
        'knowledgeLinks': 0,
        'downloads': 0,
        'url': data.get('url', ''),
        'favorite': False,
    }
    YIXIU_FILES.insert(0, file_record)
    return success_response(file_record, '文件记录已保存')


@yixiu_bp.route('/contacts', methods=['GET'])
def contacts():
    return success_response({'contacts': YIXIU_CONTACTS, 'total': len(YIXIU_CONTACTS)}, '联系人获取成功')


@yixiu_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json(silent=True) or {}
    task = {
        'id': int(datetime.now().timestamp()),
        'workOrderNo': data.get('workOrderNo') or f"YX-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        'title': data.get('title') or f"{data.get('equipment_name', data.get('deviceName', '设备'))}检修任务",
        'equipment_name': data.get('equipment_name') or data.get('deviceName') or '未登记设备',
        'equipment_no': data.get('equipment_no') or '',
        'equipment_model': data.get('equipment_model') or data.get('deviceModel') or '',
        'fault_type': data.get('fault_type') or data.get('faultType') or '',
        'description': data.get('description') or '',
        'severity': data.get('severity') or 'medium',
        'status': 'pending',
        'assignee_name': data.get('assignee_name') or '未分配',
        'current_step': '待接收',
        'progress': 0,
        'due_at': data.get('due_at') or '',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sop': data.get('sop') or [],
        'tools': data.get('tools') or [],
        'parts': data.get('parts') or [],
        'safety': data.get('safety') or [],
    }
    return success_response(task, '检修任务创建成功')


@yixiu_bp.route('/tasks/<task_id>/status', methods=['PUT'])
def change_task_status(task_id):
    data = request.get_json(silent=True) or {}
    status = data.get('status', 'pending')
    if status not in ('pending', 'in_progress', 'review', 'completed', 'paused', 'rejected', 'overdue'):
        status = 'pending'
    return success_response({'task_id': task_id, 'status': status, 'operator': data.get('operator', '当前用户'), 'operated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'note': data.get('note', '')}, '任务状态已更新')


@yixiu_bp.route('/recheck', methods=['POST'])
def save_recheck():
    data = request.get_json(silent=True) or {}
    result = data.get('result', '通过')
    next_status = 'completed' if result == '通过' else 'in_progress'
    return success_response({'task_id': data.get('task_id'), 'result': result, 'next_status': next_status, 'comment': data.get('comment', ''), 'reviewer': data.get('reviewer', '复检人员'), 'reviewed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, '复检结果已保存')


@yixiu_bp.route('/knowledge/update', methods=['POST'])
def update_knowledge():
    data = request.get_json(silent=True) or {}
    item = {'id': f"kb-{int(datetime.now().timestamp())}", 'title': data.get('title', '未命名知识条目'), 'type': data.get('type', '技术资料'), 'category': data.get('category', '案例'), 'equipment': data.get('equipment', ''), 'model': data.get('model', ''), 'summary': data.get('summary', ''), 'tags': data.get('tags', []), 'status': 'pending', 'updated_at': datetime.now().strftime('%Y-%m-%d')}
    return success_response(item, '知识条目已进入沉淀审核队列')
