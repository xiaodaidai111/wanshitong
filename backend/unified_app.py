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

    app.config['UPLOAD_FOLDER'] = 'uploads'
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
        ('routes.map_agent', 'map_agent_bp', '/map', 'map agent service'),
        (
            'routes.recipe_recommendation',
            'recipe_recommendation_bp',
            '/api/recipe-recommendation',
            'recipe recommendation service',
        ),
        ('routes.openclaw', 'openclaw_bp', '', 'openclaw service'),
        ('routes.speech_asr', 'speech_asr_bp', '', 'speech asr service'),
        ('routes.monitor', 'monitor_bp', '/api', 'monitor service'),
        ('routes.ai_services', 'ai_services_bp', '', 'ai services'),
        ('routes.takeaway_health', 'takeaway_health_bp', '', 'takeaway health service'),
    ]

    for import_path, blueprint_name, url_prefix, service_name in registrations:
        _register_blueprint(app, import_path, blueprint_name, url_prefix, service_name)

    @app.route('/')
    def index():
        return jsonify(
            {
                'name': '统一智能体服务',
                'version': '1.0.0',
                'services': {
                    'tuantuan': '/tuantuan - 厨艺团团服务',
                    'takeout': '/takeout - 外卖咕咕服务',
                    'health': '/health - 健康糖豆服务',
                    'map': '/map - 推荐小泽服务',
                    'community': '/api/community - 社区服务',
                    'recipe-recommendation': '/api/recipe-recommendation - 家常菜推荐榜服务',
                    'speech': '/api/speech/transcribe - 语音识别服务',
                },
                'status': 'running',
            }
        )

    @app.route('/api/health')
    def health_check():
        return jsonify(
            {
                'status': 'healthy',
                'services': ['tuantuan', 'takeout', 'health_manager', 'map_agent', 'community', 'speech_asr'],
            }
        )

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
