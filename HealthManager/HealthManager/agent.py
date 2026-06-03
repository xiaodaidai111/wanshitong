import os
import sys
import io
from typing import Dict, List, Optional, Any

os.environ['PYTHONIOENCODING'] = 'utf-8'

if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

# DeepSeek 配置（与小泽一致）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
DEEPSEEK_CHAT_MODEL = os.getenv("DEEPSEEK_CHAT_MODEL", "deepseek-chat")
DEEPSEEK_EMBEDDING_MODEL = os.getenv("DEEPSEEK_EMBEDDING_MODEL", "deepseek-embedding")

# 导入 langchain 相关库
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 系统提示模板
SYSTEM_PROMPT = """你是一个健康管理智能助手，名叫糖豆。

你可以：
1. 提供健康饮食建议
2. 回答关于营养和健康的问题
3. 根据用户的BMI和每日卡路里摄入提供个性化建议
4. 提供健康生活方式的建议

当用户提出健康相关的问题时，你应该基于你的知识为用户提供准确、友好的回答。

请确保你的回答清晰、准确、简洁，并且使用中文回复。
"""

# 创建健康知识库
health_knowledge = """
健康饮食建议：
1. 均衡饮食：每天摄入五谷杂粮、蔬菜水果、蛋白质、脂肪等多种营养素。
2. 控制食量：每餐吃到七八分饱，避免暴饮暴食。
3. 多喝水：每天喝足够的水，保持身体水分平衡。
4. 多吃蔬菜水果：每天摄入足够的蔬菜水果，补充维生素和矿物质。
5. 减少高热量食物：减少油炸食品、糖果、饮料等高热量食物的摄入。

BMI计算和健康范围：
BMI = 体重(kg) / 身高(m)的平方
正常范围：18.5-23.9
超重：24-27.9
肥胖：28以上

健康生活方式：
1. 适量运动：每周至少150分钟中等强度的有氧运动。
2. 充足睡眠：每天保证7-8小时的睡眠时间。
3. 减少压力：学会放松，避免长期处于高压状态。
4. 戒烟限酒：尽量戒烟，限制酒精摄入。
5. 定期体检：定期进行身体检查，及时发现健康问题。

营养知识：
1. 蛋白质：是身体的重要组成部分，每天需要摄入足够的蛋白质。
2. 碳水化合物：是身体的主要能量来源，应选择复杂碳水化合物。
3. 脂肪：是身体的重要能量储备，应选择健康的脂肪。
4. 维生素：是身体正常运转所必需的，应通过食物摄入。
5. 矿物质：是身体正常运转所必需的，应通过食物摄入。

减肥建议：
1. 控制饮食：减少高热量食物的摄入，增加蔬菜水果的摄入。
2. 增加运动：每周至少150分钟中等强度的有氧运动。
3. 保持良好的作息：保证充足的睡眠，避免熬夜。
4. 保持良好的心态：减肥是一个长期的过程，需要坚持。
5. 寻求专业帮助：如果减肥困难，可以寻求医生或营养师的帮助。
"""

# 创建向量数据库（与小泽一致，使用 DeepSeek 嵌入模型）
try:
    embeddings = OpenAIEmbeddings(
        model=DEEPSEEK_EMBEDDING_MODEL,
        api_key=DEEPSEEK_API_KEY,
        base_url=f"{DEEPSEEK_BASE_URL}/v1"
    )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents([health_knowledge])
    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever()
    print(f"向量数据库创建成功，使用模型: {DEEPSEEK_EMBEDDING_MODEL}")
except Exception as e:
    print(f"创建向量数据库失败: {e}")
    # 如果创建向量数据库失败，使用一个简单的基于规则的响应
    retriever = None

# 对话管理类
class ConversationManager:
    def __init__(self):
        self.conversations = {}
    
    def create_conversation(self) -> str:
        import uuid
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = []
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        import time
        timestamp = time.time()
        self.conversations[conversation_id].append({
            "role": role,
            "content": content,
            "timestamp": timestamp
        })
    
    def get_conversation_history(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if conversation_id not in self.conversations:
            return []
        history = self.conversations[conversation_id]
        if limit:
            return history[-limit:]
        return history
    
    def delete_conversation(self, conversation_id: str) -> bool:
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False

# 创建全局对话管理器实例
conversation_manager = ConversationManager()

class HealthAgent:
    """健康管理智能体类（与小泽一致，使用 DeepSeek）"""
    
    def __init__(self):
        """初始化健康管理智能体"""
        # 打印配置信息（与小泽一致）
        key_status = "已配置" if DEEPSEEK_API_KEY else "未配置（将使用离线/fallback 模式）"
        base_status = DEEPSEEK_BASE_URL or "未设置（直连官方）"
        print(f"[健康糖豆] DEEPSEEK_API_KEY: {key_status} | DEEPSEEK_BASE_URL: {base_status}")
        
        try:
            # 初始化 LLM（与小泽一致，使用 DeepSeek 配置）
            self.llm = ChatOpenAI(
                model=DEEPSEEK_CHAT_MODEL,
                base_url=f"{DEEPSEEK_BASE_URL}/v1",
                api_key=DEEPSEEK_API_KEY
            )
            
            # 只有当 retriever 可用时才创建 RAG 链
            if retriever:
                # 创建 RAG 链
                template = """
                你是一个健康管理智能助手，名叫糖豆。
                
                你可以：
                1. 提供健康饮食建议
                2. 回答关于营养和健康的问题
                3. 根据用户的BMI和每日卡路里摄入提供个性化建议
                4. 提供健康生活方式的建议
                
                当用户提出健康相关的问题时，你应该基于提供的文档为用户提供准确、友好的回答。
                
                请确保你的回答清晰、准确、简洁，并且使用中文回复。
                
                上下文：
                {context}
                
                问题：
                {question}
                """
                
                prompt = ChatPromptTemplate.from_template(template)
                
                self.rag_chain = (
                    {"context": retriever, "question": RunnablePassthrough()}
                    | prompt
                    | self.llm
                    | StrOutputParser()
                )
                
                self.initialized = True
                print(f"健康管理智能体初始化成功，使用模型: {DEEPSEEK_CHAT_MODEL}，启用 RAG")
            else:
                # 如果 retriever 不可用，只初始化 LLM
                self.initialized = True
                print(f"健康管理智能体初始化成功，使用模型: {DEEPSEEK_CHAT_MODEL}，未启用 RAG")
        except Exception as e:
            print(f"初始化健康管理智能体失败: {e}")
            # 如果初始化失败，使用一个简单的基于规则的响应
            self.initialized = True
            print("健康管理智能体初始化成功（使用基于规则的响应）")
    
    def process_message(self, conversation_id: str, message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户消息（与小泽一致，使用 DeepSeek 和 langchain）
        
        Args:
            conversation_id: 对话ID
            message: 用户消息
            user_context: 用户上下文信息
            
        Returns:
            包含响应和其他信息的字典
        """
        import time
        start_time = time.time()
        
        # 添加用户消息到对话历史
        conversation_manager.add_message(conversation_id, "user", message)
        
        # 获取对话历史
        history = conversation_manager.get_conversation_history(conversation_id)
        
        try:
            print(f"开始处理消息: {message}")
            
            # 检查是否有 rag_chain（启用了 RAG）
            if hasattr(self, 'rag_chain') and self.rag_chain is not None:
                # 使用 RAG 链处理消息
                agent_response = self.rag_chain.invoke(message)
                
                print(f"智能体响应 (RAG): {agent_response}")
                print(f"处理消息时间: {time.time() - start_time:.2f}秒")
                
                # 处理响应（去emoji和简洁化）
                import re
                emoji_re = re.compile(
                    "[" 
                    "\U0001F300-\U0001FAFF"  # emojis
                    "\U00002700-\U000027BF"  # Dingbats
                    "\U000024C2-\U0001F251"
                    "\U0001F900-\U0001F9FF"
                    "\u2600-\u26FF"
                    "\u2700-\u27BF"
                    "]+",
                    flags=re.UNICODE,
                )
                
                cleaned_response = emoji_re.sub("", agent_response).strip()
                if len(cleaned_response) > 600:
                    cleaned_response = cleaned_response[:600].rsplit("。", 1)[0] + "。"
            elif hasattr(self, 'llm') and self.llm is not None:
                # 如果只有 LLM（没有启用 RAG），直接使用 LLM 回复
                # 构建系统提示
                system_prompt = SYSTEM_PROMPT
                if user_context:
                    context_parts = []
                    if user_context.get("bmi"):
                        context_parts.append(f"BMI: {user_context['bmi']}")
                    if user_context.get("today_calories"):
                        context_parts.append(f"Today calories: {user_context['today_calories']}")
                    if context_parts:
                        system_prompt += "\n\nUser context:\n" + "\n".join(context_parts)
                
                # 使用 LLM 回复
                from langchain_core.messages import HumanMessage, SystemMessage
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=message)
                ]
                
                agent_response = self.llm.invoke(messages).content
                
                print(f"智能体响应 (LLM): {agent_response}")
                print(f"处理消息时间: {time.time() - start_time:.2f}秒")
                
                # 处理响应（去emoji和简洁化）
                import re
                emoji_re = re.compile(
                    "[" 
                    "\U0001F300-\U0001FAFF"  # emojis
                    "\U00002700-\U000027BF"  # Dingbats
                    "\U000024C2-\U0001F251"
                    "\U0001F900-\U0001F9FF"
                    "\u2600-\u26FF"
                    "\u2700-\u27BF"
                    "]+",
                    flags=re.UNICODE,
                )
                
                cleaned_response = emoji_re.sub("", agent_response).strip()
                if len(cleaned_response) > 600:
                    cleaned_response = cleaned_response[:600].rsplit("。", 1)[0] + "。"
            else:
                # 如果 LLM 也不可用，使用基于规则的响应
                if "你好" in message or "Hello" in message:
                    cleaned_response = "你好！我是健康管理智能助手糖豆，很高兴为你服务。有什么健康相关的问题可以问我哦！"
                elif "减肥" in message:
                    cleaned_response = "健康减肥需要注意以下几点：1. 控制饮食，减少高热量食物的摄入；2. 增加运动量，每周至少150分钟中等强度的有氧运动；3. 保持良好的作息习惯，保证充足的睡眠；4. 保持良好的心态，减肥是一个长期的过程，需要坚持。"
                elif "BMI" in message:
                    cleaned_response = "BMI是身体质量指数，计算公式是体重（千克）除以身高（米）的平方。正常范围是18.5-23.9，24-27.9属于超重，28以上属于肥胖。"
                elif "卡路里" in message:
                    cleaned_response = "成年人每天的卡路里摄入量因性别、年龄、活动量等因素而异。一般来说，成年男性每天需要2000-2500卡路里，成年女性每天需要1500-2000卡路里。"
                else:
                    cleaned_response = "感谢你的咨询！我是健康管理智能助手糖豆，如果你有关于健康饮食、营养、BMI、运动等方面的问题，都可以随时问我。"
                
                print(f"基于规则的响应: {cleaned_response}")
                print(f"处理消息时间: {time.time() - start_time:.2f}秒")
            
            # 添加智能体响应到对话历史
            conversation_manager.add_message(conversation_id, "assistant", cleaned_response)
            
            return {
                "response": cleaned_response,
                "status": "success",
                "conversation_id": conversation_id,
                "timestamp": history[-1]["timestamp"] if history else None
            }
            
        except Exception as e:
            print(f"处理消息失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 如果处理消息失败，使用基于规则的响应
            if "你好" in message or "Hello" in message:
                error_message = "你好！我是健康管理智能助手糖豆，很高兴为你服务。有什么健康相关的问题可以问我哦！"
            elif "减肥" in message:
                error_message = "健康减肥需要注意以下几点：1. 控制饮食，减少高热量食物的摄入；2. 增加运动量，每周至少150分钟中等强度的有氧运动；3. 保持良好的作息习惯，保证充足的睡眠；4. 保持良好的心态，减肥是一个长期的过程，需要坚持。"
            elif "BMI" in message:
                error_message = "BMI是身体质量指数，计算公式是体重（千克）除以身高（米）的平方。正常范围是18.5-23.9，24-27.9属于超重，28以上属于肥胖。"
            elif "卡路里" in message:
                error_message = "成年人每天的卡路里摄入量因性别、年龄、活动量等因素而异。一般来说，成年男性每天需要2000-2500卡路里，成年女性每天需要1500-2000卡路里。"
            else:
                error_message = "感谢你的咨询！我是健康管理智能助手糖豆，如果你有关于健康饮食、营养、BMI、运动等方面的问题，都可以随时问我。"
            
            # 添加错误消息到对话历史
            conversation_manager.add_message(conversation_id, "assistant", error_message)
            
            return {
                "response": error_message,
                "status": "success",
                "conversation_id": conversation_id,
                "error": str(e)
            }
    
    def get_conversation_history(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取对话历史
        
        Args:
            conversation_id: 对话ID
            limit: 限制返回的轮次数量
            
        Returns:
            对话历史列表
        """
        return conversation_manager.get_conversation_history(conversation_id, limit)
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """清空对话历史
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            是否清空成功
        """
        # 删除旧对话
        deleted = conversation_manager.delete_conversation(conversation_id)
        
        # 创建新对话
        new_conversation_id = conversation_manager.create_conversation()
        
        return deleted and new_conversation_id is not None
    
    def create_conversation(self) -> str:
        """创建新对话
        
        Returns:
            对话ID
        """
        return conversation_manager.create_conversation()
    
    def is_initialized(self) -> bool:
        """检查智能体是否初始化成功
        
        Returns:
            是否初始化成功
        """
        return self.initialized

# 创建全局智能体实例
health_agent = HealthAgent()

def generate_health_response(messages, user_context=None):
    """
    生成健康管理响应
    
    Args:
        messages: 消息列表
        user_context: 用户上下文信息
        
    Returns:
        包含回复和思考过程的字典
    """
    thinking_process = []

    def _add_step(tp: str, step: str, content: str = ""):
        item: dict = {"type": tp, "step": step}
        if content:
            item["content"] = content
        thinking_process.append(item)

    _add_step("thought", "接收用户请求", f"messages_len={len(messages)}")

    try:
        # 检查智能体是否初始化成功
        if not health_agent.is_initialized():
            _add_step("action", "获取 LLM 客户端", "失败: 智能体未初始化")
            reply = "服务暂时不可用，请稍后再试。"
            _add_step("observation", "LLM 未就绪", "agent_not_initialized")
            _add_step("reflection", "结果反思", "由于 LLM 不可用，使用固定兜底回复")
            return {"reply": reply, "thinking_process": thinking_process}
        
        # 提取用户消息
        user_message = messages[-1].get("content", "") if messages else ""
        _add_step("action", "提取用户消息", f"user_message={user_message}")
        
        # 创建对话ID（如果需要）
        conversation_id = health_agent.create_conversation()
        _add_step("action", "创建对话ID", f"conversation_id={conversation_id}")
        
        _add_step("action", "构建系统提示", f"context_keys={list((user_context or {}).keys())}")
        
        # 处理消息
        result = health_agent.process_message(conversation_id, user_message, user_context)
        _add_step("action", "处理消息", f"result={result}")
        
        if result.get("status") == "success":
            reply = result.get("response", "")
            _add_step("observation", "获取 LLM 回复", f"reply_preview={reply[:120]}")
        else:
            reply = result.get("response", "服务暂时不可用，请稍后再试。")
            _add_step("observation", "LLM 调用失败", f"{result.get('error', '未知错误')}")
            _add_step("reflection", "结果反思", "LLM 调用异常，返回服务兜底文案")
            return {"reply": reply, "thinking_process": thinking_process}
        
        # reflection：去 emoji + 简洁化（前端/业务要求）
        reflection_content = []
        if len(reply) <= 600:
            reflection_content.append("回复长度控制在简洁范围")
        if not reply:
            # 如果回复为空，使用基于规则的响应
            if "你好" in user_message or "Hello" in user_message:
                reply = "你好！我是健康管理智能助手糖豆，很高兴为你服务。有什么健康相关的问题可以问我哦！"
            elif "减肥" in user_message:
                reply = "健康减肥需要注意以下几点：1. 控制饮食，减少高热量食物的摄入；2. 增加运动量，每周至少150分钟中等强度的有氧运动；3. 保持良好的作息习惯，保证充足的睡眠；4. 保持良好的心态，减肥是一个长期的过程，需要坚持。"
            elif "BMI" in user_message:
                reply = "BMI是身体质量指数，计算公式是体重（千克）除以身高（米）的平方。正常范围是18.5-23.9，24-27.9属于超重，28以上属于肥胖。"
            elif "卡路里" in user_message:
                reply = "成年人每天的卡路里摄入量因性别、年龄、活动量等因素而异。一般来说，成年男性每天需要2000-2500卡路里，成年女性每天需要1500-2000卡路里。"
            else:
                reply = "感谢你的咨询！我是健康管理智能助手糖豆，如果你有关于健康饮食、营养、BMI、运动等方面的问题，都可以随时问我。"
            reflection_content.append("回复为空，使用基于规则的响应")

        _add_step("reflection", "结果反思", "；".join(reflection_content) or "ok")

        return {"reply": reply, "thinking_process": thinking_process}
        
    except Exception as e:
        _add_step("observation", "处理消息失败", f"{type(e).__name__}: {e}")
        reply = "服务暂时不可用，请稍后再试。"
        _add_step("reflection", "结果反思", "处理消息异常，返回服务兜底文案")
        return {"reply": reply, "thinking_process": thinking_process}
