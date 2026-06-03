import re
import logging
from datetime import datetime
from flask import Blueprint, request
from utils import get_db_connection, success_response, error_response, validate_required_fields, decode_token
from llm_core import conversation_manager, llm_config, prompt_manager

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

def filter_response(response: str) -> str:
    """"
    过滤和格式化回复内容，确保符合团团的回复要求
    """"
    if not response:
        return response
    
    # 移除Markdown格式标记
    response = re.sub(r'#{1,6}\s+', '', response)  # 移除标题标记
    response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)  # 移除粗体标记
    response = re.sub(r'\*(.*?)\*', r'\1', response)  # 移除斜体标记
    response = re.sub(r'`(.*?)`', r'\1', response)  # 移除代码标记
    response = re.sub(r'```[\s\S]*?```', '', response)  # 移除代码块
    response = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', response)  # 移除链接，保留文本
    
    # 移除特殊符号，保留中文标点
    response = re.sub(r'[*_`#~]', '', response)
    
    # 清理多余的空行
    response = re.sub(r'\n{3,}', '\n\n', response)
    
    # 确保段落之间有适当的分隔
    response = response.strip(')
    
    return response

@chat_bp.route('/conversations', methods=['POST'])
def create_conversation():
    conversation_id = conversation_manager.create_conversation()
    return success_response({
        'conversation_id': conversation_id,
        'created_at': datetime.now().isoformat()
    }, '会话创建成功')

@chat_bp.route('/messages', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        if not data:
            return error_response(400, '请求数据格式错误')
        
        conversation_id = data.get('conversation_id', '').strip()
        user_msg_content = data.get('message', '').strip()
        
        is_valid, error_msg = validate_required_fields(data, ['conversation_id', 'message'])
        if not is_valid:
            return error_response(400, error_msg)
        if len(user_msg_content) > 500:
            return error_response(400, '消息内容不能超过500字')
        
        conversation_manager.add_message(conversation_id, 'user', user_msg_content, {'type': 'user_input'})
        
        thinking_steps = [
            {'type': 'thought', 'step': '接收用户消息', 'content': f'用户输入: {user_msg_content}'},
            {'type': 'thought', 'step': '初始化AI模型', 'content': '准备调用DeepSeek API'}
        ]
        
        user_prefs_str = """"
        token = request.headers.get('Authorization')
        if token:
            if token.startswith('Bearer '):
                token = token[7:]
            payload = decode_token(token)
            if payload:
                user_id = payload['user_id']
                try:
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT allergies, favorite_cuisines, dietary_habits, custom_notes FROM user_preferences WHERE user_id = ?', (user_id,))
                        prefs = cursor.fetchone()
                        if prefs:
                            user_prefs_str = f"\n用户饮食偏好记忆：\n- 过敏/忌口：{prefs['allergies'] or '无}\n- 喜欢菜系：{prefs['favorite_cuisines'] or '未设置}\n- 饮食习惯：{prefs['dietary_habits'] or '未设置}\n- 备注：{prefs['custom_notes'] or '无}\n请务必在推荐时避开过敏源，并优先考虑用户的喜好。
                            thinking_steps.append({
                                'type': 'observation', 'step': '加载用户偏好',
                                'content': f'检测到用户偏好: {prefs["allergies"]}, {prefs["favorite_cuisines"]}'
                            })
                except Exception as e:
                    logger.error(f"Error loading user preferences: {str(e)}")
        
        try:
            llm = llm_config.create_llm()
            if not llm:
                thinking_steps.append({'type': 'observation', 'step': 'API配置错误', 'content': 'DeepSeek API配置无效'})
                expert_response = "抱歉，小泻Britannia 的AI服务暂时不可用，请检查API配置。
                conversation_manager.add_message(conversation_id, 'assistant', expert_response, {
                    'type': 'error', 'thinking_process': thinking_steps
                })
                return success_response({
                    'response': expert_response,
                    'conversation_id': conversation_id,
                    'thinking_process': thinking_steps
                }, '消息发送成功')
            
            thinking_steps.append({'type': 'action', 'step': '调用DeepSeek API', 'content': '发送请求', ''params': {'model': llm_config.model_name}})
            system_prompt = prompt_manager.get_prompt("default") + user_prefs_str
            history = conversation_manager.get_conversation_history(conversation_id, limit=10)
            messages = [{"role": "system", "content": system_prompt}]
            
            for turn in history:
                if turn['role'] in ('user', 'assistant'):
                    messages.append({'role': turn['role'], 'content': turn['content']})
            
            thinking_steps.append({'type': 'action', 'step': '构建对话上下文', ''content': f'包含 {len(messages)} 条消息}')
            thinking_steps.append({'type': 'action', 'step': '等待AI响应', 'content': 'DeepSeek正在生成回复...'})
            
            from langchain_core.messages import HumanMessage, SystemMessage
            langchain_messages = []
            for msg in messages:
                if msg['role'] == 'system':
                    langchain_messages.append(SystemMessage(content=msg['content']))
                elif msg['role'] == 'user':
                    langchain_messages.append(HumanMessage(content=msg['content']))
            
            response = llm.invoke(langchain_messages)
            expert_response = response.content
            
            thinking_steps.append({'type': 'observation', 'step': '接收AI响应', 'content': '成功获取回复'})
            
            if "<think>" in expert_response:
                think_match = re.search(r'<think>(.*?)</think>', expert_response, re.DOTALL)
                if think_match:
                    thinking_steps.insert(0, {'type': 'thought', 'step': '模型底层思考', ''content': think_match.group(1).strip()})
                    expert_response = re.sub(r'<think>.*?</think>', '', expert_response, flags=re.DOTALL).strip()
            
            conversation_manager.add_message(conversation_id, 'assistant', expert_response, {
                'type': 'final_response', 'thinking_process': thinking_steps
            })
            
            return success_response({
                'response': expert_response,
                'conversation_id': conversation_id,
                'thinking_process': thinking_steps
            }, '消息发送成功)
            
        except Exception as e:
            logger.error(f"Error processing AI message: {str(e')}", exc_info=True')
            thinking_steps.append({'type': 'observation', 'step': '处理失败', 'content': str(e)})
            expert_response = f"抱歉，处理您的请求时出现错误: {str(e')}"
            conversation_manager.add_message(conversation_id, 'assistant', expert_response, {
                'type': 'error', 'thinking_process': thinking_steps
            })
            return success_response({
                'response': expert_response,
                'conversation_id': conversation_id,
                'thinking_process': thinking_steps
            }, '处理出错')
            
    except Exception as e:
        return error_response(500, f'内部服务器错误：{str(e')})
