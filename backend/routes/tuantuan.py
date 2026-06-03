from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

tuantuan_bp = Blueprint('tuantuan', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@tuantuan_bp.route('/')
def index():
    return jsonify({
        'service': '厨艺团团',
        'description': '健康饮食智能体系统后端服务',
        'endpoints': {
            'auth': '/api/auth - 用户认证',
            'user': '/api/user - 用户管理',
            'chat': '/api/chat - 聊天对话',
            'restaurants': '/api/restaurants - 餐厅信息',
            'cook_agent': '/cook-agent - 厨艺智能体'
        }
    })

@tuantuan_bp.route('/api/auth', methods=['GET', 'POST'])
def auth():
    return jsonify({'message': '厨艺团团 - 用户认证服务'})

@tuantuan_bp.route('/api/user', methods=['GET', 'POST'])
def user():
    return jsonify({'message': '厨艺团团 - 用户管理服务'})

@tuantuan_bp.route('/api/chat', methods=['POST'])
def chat():
    return jsonify({'message': '厨艺团团 - 聊天对话服务'})

@tuantuan_bp.route('/api/restaurants', methods=['GET'])
def restaurants():
    return jsonify({'message': '厨艺团团 - 餐厅信息服务'})

@tuantuan_bp.route('/cook-agent/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'success': True, 'file_url': f"/uploads/{filename}", 'filename': filename})
    return jsonify({'error': '不支持的文件类型'}), 400

@tuantuan_bp.route('/cook-agent', methods=['GET'])
def cook_agent():
    return jsonify({'message': '厨艺团团 - 厨艺智能体服务'})