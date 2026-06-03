# -*- coding: utf-8 -*-
"""
应用配置：从环境变量读取，不写入任何真实 API Key。
会优先从项目根目录的 .env 文件加载（需安装 python-dotenv），再读系统环境变量。
"""
from __future__ import annotations

import os

# 优先从本项目目录加载 .env（不依赖 python-dotenv，未安装时也会手动读）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(BASE_DIR, ".env")
try:
    from dotenv import load_dotenv
    load_dotenv(_env_path)
except ImportError:
    # 未安装 python-dotenv 时手动解析 .env，避免配置不生效
    if os.path.isfile(_env_path):
        with open(_env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip()
                if not k:
                    continue
                if len(v) >= 2 and (v[0], v[-1]) in (('"', '"'), ("'", "'")):
                    v = v[1:-1]
                os.environ.setdefault(k, v)
DATA_DIR = os.path.join(BASE_DIR, "data")
# SQLite 数据库路径（留出数据库，便于后续扩展）
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "data", "agent.db"))

# DeepSeek 相关：仅从环境变量读取，占位请填写实际 API Key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
DEEPSEEK_CHAT_MODEL = os.getenv("DEEPSEEK_CHAT_MODEL", "deepseek-chat")
DEEPSEEK_EMBEDDING_MODEL = os.getenv("DEEPSEEK_EMBEDDING_MODEL", "deepseek-embedding")

# OpenAI 相关配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip()
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
# 对话历史条数上限（保证智能体具备足够上下文与用户连续交流）
CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "20"))
# 是否在回复中展示调试信息（生产环境建议关闭）
SHOW_DEBUG_INFO = os.getenv("SHOW_DEBUG_INFO", "0").strip() == "1"

# Flask
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
# CORS
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()
CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS", "GET,POST,OPTIONS").strip()
CORS_ALLOW_HEADERS = os.getenv(
    "CORS_ALLOW_HEADERS",
    "Content-Type, X-Api-Key, X-Base-Url, X-Chat-Model, X-Embedding-Model, X-Vision-Model",
).strip()
