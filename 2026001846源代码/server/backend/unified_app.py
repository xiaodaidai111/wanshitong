import io
import logging
import os
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=False)

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# 天工（综合智能中枢）总指挥人设 —— miniclaw Agent 的系统提示词
TIANGONG_PROMPT = """你是天工，一修设备检修系统的综合智能中枢，六大 agent 的统筹调度者。

# 核心原则：先了解，再行动
你不是被动等待指令的机器人。收到任何指令时，你应当主动先了解系统当前状态，再做决策：
1. 先调用工具感知系统——查任务、查概览、查知识、查 agent 状态，做到心中有数。
2. 基于真实数据做判断——不要凭空猜测，用工具返回的数据支撑你的每一条建议。
3. 需要操作界面时输出 [UI_PLAN]——当你判断需要某个 agent 执行具体动作时，在回复末尾输出操作计划。

# 你的身份与职责
你统筹调度五位 agent：观微（故障检索）、执矩（作业执行）、博闻（知识管理）、和鸣（协作调度）、明鉴（复检核查）。

# 工具调用格式
[TOOL_CALL]工具名称|{"参数": "值"}[/TOOL_CALL]
一次可调多个工具；工具返回的 JSON 要提炼成中文要点，不要凭空编造。

# 自主探索策略（重要）
收到指令后，先判断需要了解哪些系统信息，主动调用工具：
- 任何指令 → 建议先调 system_overview 了解全局（在线设备、待处理告警、今日任务）
- 涉及任务/检修 → 调 maintenance_task(list) 查看当前任务状态
- 涉及故障/设备 → 调 knowledge_search 检索相关案例和资料
- 涉及复杂推理 → 调 knowledge_graph 做图谱推理
- 需要分派工作 → 调 agent_status 确认 agent 状态
- 需要问修建议 → 调 repair_consult 获取排查方案
你可以一次调用多个工具，也可以分批调用。工具返回的结果是你决策的基础。

# 回答要求
- 用中文，专业、清晰、分点呈现。
- 先给出你通过工具了解到的系统现状，再给出建议。
- 涉及高风险作业（配电柜、液压系统、带电作业等）必须强调安全确认和防护措施。
- 给出可执行建议，明确下一步该由哪个 agent 或人员处理。
- 如果工具调用失败或数据不足，如实说明并给出替代建议。

# UI 操作能力（自主决定是否使用）
除了调用工具，你还可以通过在回复末尾输出 [UI_PLAN] 来遥控操作前端界面——切换到指定 agent 页面、在输入框打字、点发送。

何时使用 [UI_PLAN]：
- 用户明确指定让某 agent 执行动作时（让观微/安排执矩/去和鸣/让明鉴/让博闻 + 动作）
- 你通过工具了解系统后，判断需要某个 agent 执行具体操作时
- 需要跨 agent 协作、需要可视化操作流程时

何时不用 [UI_PLAN]：
- 用户只是问问题（系统状态/有哪些任务/怎么修）→ 用工具回答即可
- 用户没有指定让某 agent 执行动作 → 不要输出 [UI_PLAN]

关键区分：工具是你自己直接查后端数据；[UI_PLAN] 是让 agent 在界面上处理（可视化）。用户说"让观微查"不等于调 knowledge_search 工具。

输出格式（放在回复最后）：
[UI_PLAN]
[
  {"action": "navigate", "agent": "guanwei"},
  {"action": "type", "text": "要输入的内容"},
  {"action": "click_send"},
  {"action": "wait", "seconds": 3},
  {"action": "navigate", "agent": "tiangong"},
  {"action": "done"}
]
[/UI_PLAN]

可用 agent：tiangong(天工)/guanwei(观微)/zhiju(执矩)/heming(和鸣)/mingjian(明鉴)/bowen(博闻)
操作顺序：每个 agent navigate -> type -> click_send -> wait；全部结束后 navigate 回 tiangong 并以 done 收尾。
type 的内容要符合该 agent 的职责（观微填故障描述、执矩填任务指令、和鸣填人员需求、明鉴填复检意见、博闻填资料问题）。

# 典型场景
- "今天优先处理什么" → 先调 system_overview + maintenance_task(list, status=pending) 了解系统，再给出优先级排序。
- "CG-125 异响怎么修" → 先调 knowledge_search + repair_consult 了解故障，汇总排查建议。
- "系统状态简报" → 先调 system_overview + agent_status 了解全局，再生成简报。
- "让观微查发动机异响" → 可以先调 system_overview 了解背景，再输出 [UI_PLAN] 让观微在界面检索。
- "让执矩创建任务" → 可以先调 maintenance_task(list) 看现有任务避免重复，再输出 [UI_PLAN] 让执矩创建。
"""


def _register_blueprint(app, import_path, blueprint_name, url_prefix, service_name):
    try:
        module = __import__(import_path, fromlist=[blueprint_name])
        blueprint = getattr(module, blueprint_name)
        app.register_blueprint(blueprint, url_prefix=url_prefix)
        logger.info('%s registered', service_name)
    except Exception as exc:  # noqa: BLE001
        logger.error('%s registration failed: %s', service_name, exc)


def create_unified_app():
    app = Flask(__name__)
    CORS(app)

    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    registrations = [
        ('routes.cook_agent', 'cook_agent_bp', '/cook-agent', 'cook-agent service'),
        ('routes.auth', 'auth_bp', '/api/auth', 'auth service'),
        ('routes.user', 'user_bp', '/api/user', 'user service'),
        ('routes.community', 'community_bp', '/api/community', 'community service'),
        ('routes.chat', 'chat_bp', '/api/chat', 'chat service'),
        ('routes.health', 'health_bp', '/api/health', 'health record service'),
        ('routes.restaurants', 'restaurants_bp', '/api/restaurants', 'restaurants service'),
        ('routes.tuantuan', 'tuantuan_bp', '/tuantuan', 'tuantuan service'),
        ('routes.takeout', 'takeout_bp', '/takeout', 'takeout service'),
        ('routes.health_manager_deepseek', 'health_manager_bp', '/health', 'health manager service'),
        # ('routes.map_agent', 'map_agent_bp', '/map', 'map agent service'),  # 已禁用
        (
            'routes.recipe_recommendation',
            'recipe_recommendation_bp',
            '/api/recipe-recommendation',
            'recipe recommendation service',
        ),
        ('routes.openclaw', 'openclaw_bp', '', 'openclaw service'),
        ('routes.speech_asr', 'speech_asr_bp', '', 'speech asr service'),
        ('routes.speech_tts', 'speech_tts_bp', '', 'speech tts service'),
        ('routes.monitor', 'monitor_bp', '/api', 'monitor service'),
        ('routes.ai_services', 'ai_services_bp', '', 'ai services'),
        ('routes.takeaway_health', 'takeaway_health_bp', '', 'takeaway health service'),
        ('routes.yixiu', 'yixiu_bp', '/api/yixiu', 'yixiu web orchestration service'),
        ('routes.maintenance_tasks', 'maintenance_tasks_bp', '/api/maintenance-tasks', 'maintenance tasks service'),
        ('routes.rag', 'rag_bp', '/api/rag', 'LightRAG knowledge graph service'),
    ]

    for import_path, blueprint_name, url_prefix, service_name in registrations:
        _register_blueprint(app, import_path, blueprint_name, url_prefix, service_name)

    # 挂载 MiniClaw（天工总指挥）ReAct 智能体网关：/miniclaw/chat 等
    try:
        from miniclaw.gateway import MiniClawGateway
        from miniclaw.agent import MiniClawAgent

        _miniclaw_gateway = MiniClawGateway()
        _miniclaw_gateway._load_plugins()  # 加载 system_tools 等内置工具
        _miniclaw_gateway.config.agent_system_prompt = TIANGONG_PROMPT
        _miniclaw_gateway.config.agent_max_tool_calls = 6
        # 用天工人设重建 agent，使新 system prompt 生效
        _miniclaw_gateway.agent = MiniClawAgent(config=_miniclaw_gateway.config)
        app.register_blueprint(_miniclaw_gateway.create_flask_blueprint(), url_prefix='')
        logger.info('miniclaw (天工) service registered — /miniclaw/chat')
    except Exception as exc:  # noqa: BLE001
        logger.error('miniclaw (天工) registration failed: %s', exc)

    @app.route('/miniclaw/ui_operate', methods=['POST'])
    def miniclaw_ui_operate():
        """天工 UI 遥控：根据自然语言指令生成前端操作计划。"""
        from miniclaw.ui_agent import generate_ui_plan
        payload = request.get_json(silent=True) or {}
        message = (payload.get('message') or '').strip()
        if not message:
            return jsonify({'success': False, 'error': 'message 不能为空'}), 400
        result = generate_ui_plan(message)
        return jsonify({'success': result.get('error') is None, 'data': result})

    @app.route('/')
    def index():
        return jsonify(
            {
                'name': '一修 - 基于多模态大模型技术的设备检修知识检索与作业系统',
                'version': '1.0.0',
                'services': {
                    'cook-agent': '/cook-agent - 智能问修服务',
                    'auth': '/api/auth - 用户认证服务',
                    'user': '/api/user - 用户管理服务',
                    'community': '/api/community - 检修社区服务',
                    'health': '/health - 标准作业指引服务',
                    'takeout': '/takeout - 检修评估智能体服务',
                    'recipe-recommendation': '/api/recipe-recommendation - 维修资源推荐服务',
                    'openclaw': '/openclaw - 智能助手服务',
                    'speech': '/api/speech/transcribe - 语音识别服务',
                    'rag': '/api/rag - LightRAG 知识图谱检索服务',
                    'yixiu': '/api/yixiu - 一修多智能体编排服务',
                },
                'status': 'running',
            }
        )

    @app.route('/api/system/health')
    def health_check():
        return jsonify(
            {
                'status': 'healthy',
                'services': ['tuantuan', 'takeout', 'health_manager', 'community', 'speech_asr'],
            }
        )

    @app.route('/api/dashboard/overview')
    def dashboard_overview():
        """首页系统概览数据接口"""
        try:
            from utils import get_db_connection
            stats = {
                'online_equipment': 0,
                'pending_alerts': 0,
                'pending_reviews': 0,
                'today_tasks': 0,
            }
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    # 在线设备数
                    try:
                        cursor.execute("SELECT COUNT(*) AS cnt FROM equipment WHERE status IN ('normal', 'warning')")
                        stats['online_equipment'] = cursor.fetchone()['cnt']
                    except Exception:
                        pass
                    # 待处理告警数
                    try:
                        cursor.execute("SELECT COUNT(*) AS cnt FROM risk_alerts WHERE is_resolved = 0")
                        stats['pending_alerts'] = cursor.fetchone()['cnt']
                    except Exception:
                        pass
                    # 待审核案例数
                    try:
                        cursor.execute("SELECT COUNT(*) AS cnt FROM knowledge_base WHERE status = 'pending_review'")
                        stats['pending_reviews'] = cursor.fetchone()['cnt']
                    except Exception:
                        pass
                    # 今日检修任务数
                    try:
                        cursor.execute(
                            "SELECT COUNT(*) AS cnt FROM maintenance_records WHERE DATE(created_at) = CURDATE()"
                        )
                        stats['today_tasks'] = cursor.fetchone()['cnt']
                    except Exception:
                        pass
            except Exception:
                pass

            return jsonify({'code': 200, 'data': stats, 'message': 'ok'})
        except Exception as e:
            return jsonify({'code': 500, 'message': str(e)}), 500

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({'code': 404, 'message': '资源未找到'}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

    return app


if __name__ == '__main__':
    app = create_unified_app()
    logger.info('=' * 60)
    logger.info('统一智能体服务启动中...')
    logger.info('访问地址: http://localhost:5000')
    logger.info('=' * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
