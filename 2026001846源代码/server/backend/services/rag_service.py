"""
LightRAG 知识图谱检索服务
- LLM: 统一 AI Agent 网关（默认阿里云百炼 / Qwen）
- Embedding: 统一 AI Agent 网关（默认 DashScope text-embedding-v4）
- 支持 5 种查询模式: naive / local / global / hybrid / mix
"""
import os
import urllib.request
# 绕过系统代理，避免 tiktoken 等库因代理不可用而失败
os.environ.setdefault('NO_PROXY', '*')
urllib.request.getproxies = lambda: {}

import json
import asyncio
import logging
import numpy as np
from functools import partial
from typing import Optional
from services.ai_gateway import ai_agent

logger = logging.getLogger(__name__)

# ─── 全局 RAG 实例 ───
_rag_instance = None
_rag_initialized = False

WORKING_DIR = os.path.join(os.path.dirname(__file__), '..', 'lightrag_storage')
EMBEDDING_DIM = 1024


# ─── 统一 LLM 函数 ───
async def unified_llm_func(prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs):
    """统一 LLM 调用函数，兼容 LightRAG 接口"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    try:
        return await ai_agent.async_chat(
            messages=messages,
            model=kwargs.get("model") or ai_agent.settings.chat_model,
            temperature=kwargs.get("temperature", 0),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
    except Exception as e:
        logger.error("统一 LLM 调用失败: %s", e)
        return ""


# ─── DashScope Embedding 函数 ───
async def dashscope_embedding_func(texts: list[str], embedding_dim: int = EMBEDDING_DIM, **kwargs) -> np.ndarray:
    """统一向量化函数"""
    try:
        vectors = await ai_agent.async_embeddings(texts, model=os.getenv("EMBEDDING_MODEL", ai_agent.settings.embedding_model))
        return np.array(vectors)
    except Exception as e:
        logger.error("统一 Embedding 调用失败: %s", e)
        return np.zeros((len(texts), embedding_dim))


def get_rag_instance():
    """获取或创建 LightRAG 单例"""
    global _rag_instance, _rag_initialized
    if _rag_instance is not None:
        return _rag_instance

    try:
        from lightrag import LightRAG
        from lightrag.utils import EmbeddingFunc

        os.makedirs(WORKING_DIR, exist_ok=True)

        _rag_instance = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=unified_llm_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=EMBEDDING_DIM,
                max_token_size=8192,
                func=dashscope_embedding_func,
            ),
        )
        logger.info("LightRAG 实例已创建，工作目录: %s", WORKING_DIR)
        return _rag_instance
    except ImportError as e:
        logger.error("LightRAG 未安装，请运行: pip install lightrag-hku  错误: %s", e)
        return None
    except Exception as e:
        logger.error("LightRAG 初始化失败: %s", e)
        return None


async def init_rag_storage():
    """初始化存储（异步）"""
    global _rag_initialized
    rag = get_rag_instance()
    if rag is None:
        return False
    try:
        await rag.initialize_storages()
        _rag_initialized = True
        logger.info("LightRAG 存储已初始化")
        return True
    except Exception as e:
        logger.error("LightRAG 存储初始化失败: %s", e)
        return False


async def close_rag_storage():
    """关闭存储（异步）"""
    global _rag_instance, _rag_initialized
    if _rag_instance and _rag_initialized:
        try:
            await _rag_instance.finalize_storages()
            _rag_initialized = False
            logger.info("LightRAG 存储已关闭")
        except Exception as e:
            logger.error("LightRAG 存储关闭失败: %s", e)


# ─── 持久化事件循环（解决 Flask 多线程 + LightRAG worker 事件循环冲突） ───
_rag_loop = None
_rag_loop_thread = None


def _get_rag_loop():
    """获取或创建 RAG 专用持久事件循环"""
    global _rag_loop, _rag_loop_thread
    if _rag_loop is None or _rag_loop.is_closed():
        import threading
        _rag_loop = asyncio.new_event_loop()
        _rag_loop_thread = threading.Thread(target=_rag_loop.run_forever, daemon=True)
        _rag_loop_thread.start()
    return _rag_loop


def _run_async(coro):
    """在持久事件循环中运行异步函数，避免 Flask 多线程事件循环冲突"""
    import concurrent.futures
    loop = _get_rag_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=300)


async def _ainsert_text(text: str) -> bool:
    """异步插入文本"""
    rag = get_rag_instance()
    if rag is None:
        return False
    try:
        await rag.ainsert(text)
        logger.info("知识已插入: %s...", text[:50])
        return True
    except Exception as e:
        logger.error("知识插入失败: %s", e)
        return False


async def _aquery(question: str, mode: str = "hybrid") -> str:
    """异步查询"""
    from lightrag import QueryParam
    rag = get_rag_instance()
    if rag is None:
        return "错误：LightRAG 未初始化"
    try:
        result = await rag.aquery(question, param=QueryParam(mode=mode))
        if hasattr(result, '__aiter__'):
            # 流式结果，收集全部
            chunks = []
            async for chunk in result:
                chunks.append(chunk)
            return ''.join(chunks)
        return str(result)
    except Exception as e:
        logger.error("LightRAG 查询失败: %s", e)
        return f"查询出错: {str(e)}"


# ─── 对外接口（同步，供 Flask 路由调用） ───

def insert_text(text: str) -> bool:
    """插入单条知识文本"""
    return _run_async(_ainsert_text(text))


def insert_knowledge_base(kb_path: str) -> dict:
    """批量导入 knowledge_base.json"""
    if not os.path.exists(kb_path):
        return {"success": False, "error": f"文件不存在: {kb_path}"}

    with open(kb_path, 'r', encoding='utf-8') as f:
        kb = json.load(f)

    success_count = 0
    errors = []
    for item in kb:
        title = item.get('title', '未知')
        content_parts = item.get('content', [])
        content = '\n'.join(content_parts) if isinstance(content_parts, list) else str(content_parts)
        keywords = item.get('keywords', [])
        tips = item.get('tips', '')

        text = f"【{title}】\n"
        if keywords:
            text += f"关键词：{', '.join(keywords)}\n"
        text += content
        if tips:
            text += f"\n提示：{tips}"

        if insert_text(text):
            success_count += 1
        else:
            errors.append(title)

    return {
        "success": True,
        "total": len(kb),
        "inserted": success_count,
        "failed": len(errors),
        "failed_items": errors
    }


def query(question: str, mode: str = "hybrid") -> str:
    """查询知识库"""
    return _run_async(_aquery(question, mode))


def get_stats() -> dict:
    """获取图谱统计信息"""
    rag = get_rag_instance()
    if rag is None:
        return {"initialized": False, "error": "LightRAG 未初始化"}

    stats = {
        "initialized": _rag_initialized,
        "working_dir": WORKING_DIR,
    }

    # 检查存储文件
    graph_file = os.path.join(WORKING_DIR, "graph_chunk_entity_relation.graphml")
    doc_file = os.path.join(WORKING_DIR, "kv_store_full_docs.json")
    chunk_file = os.path.join(WORKING_DIR, "kv_store_text_chunks.json")

    if os.path.exists(graph_file):
        try:
            import networkx as nx
            G = nx.read_graphml(graph_file)
            stats["graph_nodes"] = G.number_of_nodes()
            stats["graph_edges"] = G.number_of_edges()
        except Exception:
            stats["graph_nodes"] = -1
            stats["graph_edges"] = -1

    if os.path.exists(doc_file):
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                docs = json.load(f)
            stats["documents"] = len(docs)
        except Exception:
            stats["documents"] = -1

    if os.path.exists(chunk_file):
        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            stats["chunks"] = len(chunks)
        except Exception:
            stats["chunks"] = -1

    return stats


def is_available() -> bool:
    """检查 LightRAG 是否可用"""
    try:
        import lightrag
        return True
    except ImportError:
        return False
