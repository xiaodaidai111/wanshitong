"""
健康管理智能体 独立服务入口
仅启动 HealthManager 相关的 API，不依赖主项目的任何模块。
使用方式：python run.py
"""
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# 加载当前目录下的 .env
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, '.env'))

from routes import qwen_bp

app = Flask(__name__)
CORS(app)

# 挂载聊天路由，保持和主项目中一致的前缀
app.register_blueprint(qwen_bp, url_prefix='/api/qwen')

@app.route('/')
def index():
    return '✅ 健康管理智能体服务运行中'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
