import io
import logging
import os
import sys

from flask import Flask, jsonify
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
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
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
        ('routes.maintenance_tasks', 'maintenance_tasks_bp', '/api/maintenance-tasks', 'maintenance tasks service'),
        ('routes.rag', 'rag_bp', '/api/rag', 'LightRAG knowledge graph service'),
    ]

    for import_path, blueprint_name, url_prefix, service_name in registrations:
        _register_blueprint(app, import_path, blueprint_name, url_prefix, service_name)

    @app.route('/')
    def index():
        return jsonify(
            {
                'name': '智学多智能体 - 设备检修知识检索与标准作业系统',
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
