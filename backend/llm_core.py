import os
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from utils import Config

logger = logging.getLogger(__name__)

class APIKeyManager:
    def __init__(self):
        self._api_keys: Dict[str, str] = {}
        self._load_keys_from_env()
    
    def _load_keys_from_env(self):
        if Config.AMAP_API_KEY:
            self._api_keys["amap"] = Config.AMAP_API_KEY
        if Config.DEEPSEEK_API_KEY:
            self._api_keys["deepseek"] = Config.DEEPSEEK_API_KEY
    
    def get_key(self, provider: str) -> Optional[str]:
        return self._api_keys.get(provider)
    
    def has_key(self, provider: str) -> bool:
        return provider in self._api_keys and bool(self._api_keys[provider])

api_key_manager = APIKeyManager()

class ModelInfo(BaseModel):
    name: str = Field(description="模型名称")
    provider: str = Field(description="提供商")
    version: str = Field(description="版本")
    max_tokens: int = Field(description="最大token数")
    supports_functions: bool = Field(default=True)

class ModelManager:
    MODELS = {
        "deepseek-chat": ModelInfo(
            name="deepseek-chat", provider="deepseek", version="1.0", max_tokens=4000, supports_functions=True
        )
    }
    
    def __init__(self):
        self._current_model: Optional[str] = "deepseek-chat"
    
    def get_current_model(self) -> Optional[str]:
        return self._current_model

model_manager = ModelManager()

class LLMConfig(BaseModel):
    model_name: str = Field(default_factory=lambda: model_manager.get_current_model() or "deepseek-chat", description="模型名称")
    temperature: float = Field(default=0.7, description="温度参数")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    base_url: str = Field(default="https://api.deepseek.com", description="API基础URL")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.api_key = api_key_manager.get_key("deepseek")
    
    def create_llm(self) -> Optional[ChatOpenAI]:
        try:
            if not self.api_key:
                return None
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=self.api_key,
                base_url=self.base_url
            )
        except Exception:
            return None

llm_config = LLMConfig()

class PromptTemplateManager:
    SYSTEM_PROMPTS = {
        "default": """你是美食推荐助手小泽。你的交互界面是一个集成高德地图的智能应用。

工作逻辑：
1. 分析用户的美食需求、预算和具体位置意向。
2. 搜索并推荐最合适的餐厅。
3. 你的推荐结果会实时显示在用户的地图打点上，因此请务必提供准确的【店名】和尽可能详细的【地址】。

输出要求：
- 使用自然、流畅的日常语言，避免使用过于专业或晦涩的术语
- 对于需要重点传达的内容，通过适当方式进行强调，以突出关键信息
- 回复内容需具备清晰的结构和段落划分，确保逻辑层次分明，便于用户理解
- 回复不得采用Markdown格式，应直接呈现文本内容
- 整个回复过程需始终将用户阅读体验放在首位，确保内容易读性强、信息传达准确高效
- 重点突出：店名、地址、推荐理由、人均价格
- 每次推荐 3-5 家餐厅
- 提醒用户可以在地图查看这些点位
- 300字左右
"""
    }
    
    def get_prompt(self, prompt_name: str = "default") -> str:
        return self.SYSTEM_PROMPTS.get(prompt_name, self.SYSTEM_PROMPTS["default"])

prompt_manager = PromptTemplateManager()

class Conversation:
    def __init__(self, conversation_id: Optional[str] = None):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.turns: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        self.last_activity_time = datetime.now()
        self.max_turns = 20
        self.timeout = 3600
    
    def add_turn(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        if self.is_timeout():
            raise ValueError("对话已超时")
        if len(self.turns) >= self.max_turns:
            self.turns.pop(0)
        
        turn = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.turns.append(turn)
        self.last_activity_time = datetime.now()
        return turn
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.turns[-limit:] if limit else self.turns
    
    def is_timeout(self) -> bool:
        return (datetime.now() - self.last_activity_time).total_seconds() > self.timeout

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.cleanup_interval = 300
        self.last_cleanup = time.time()
    
    def create_conversation(self) -> str:
        conversation = Conversation()
        self.conversations[conversation.conversation_id] = conversation
        self._cleanup_timeout_conversations()
        return conversation.conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        conversation = self.conversations.get(conversation_id)
        if conversation and conversation.is_timeout():
            del self.conversations[conversation_id]
            return None
        self._cleanup_timeout_conversations()
        return conversation
    
    def add_message(self, conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        try:
            return conversation.add_turn(role, content, metadata)
        except ValueError:
            del self.conversations[conversation_id]
            return None
    
    def get_conversation_history(self, conversation_id: str, limit: Optional[int] = None):
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        return conversation.get_history(limit)
    
    def _cleanup_timeout_conversations(self):
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        timeout_conversations = [cid for cid, conv in self.conversations.items() if conv.is_timeout()]
        for cid in timeout_conversations:
            del self.conversations[cid]
        self.last_cleanup = current_time

conversation_manager = ConversationManager()
