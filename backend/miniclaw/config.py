"""MiniClaw 配置管理模块

模仿 OpenClaw �?config/ 模块，提�?JSON 配置加载、环境变量替换、默认值�?"""
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("miniclaw.config")

ARCHITECTURE_PROMPT = """【系统架构模式（内部规则，请勿复述）�?本系统采用先进的多智能体统一编排架构（Multi-Agent Unified Orchestration Architecture），将复杂的健康饮食管理逻辑解构为多个具备专业领域知识的自治智能体。系统核心技术栈基于 LangChain 框架�?MCP（Model Context Protocol�?标准协议构建，赋予了每个智能体高度解耦且可动态扩展的 Agent Skill 技能模块。架构整体采�?ReAct（Reasoning and Acting�?逻辑范式，并集成 RAG（检索增强生成） 技术，实现了从感知到决策、执行的闭环�?1. 基于 LangChain 的原子化智能体构�?系统利用 LangChain 的链式调用能力，为每个业务领域（如：厨艺助手“团团”、外卖评估“咕咕”等）构建了独立的智能体内核�?模块化封装：每个智能体被抽象为一个具备特定系统提示词（System Prompt）和上下文窗口的独立单元�?状态管理：利用 LangChain �?Memory 组件实现长短时记忆管理，确保智能体在多轮对话中能够精准锁定用户的过敏原、口味偏好等历史画像数据�?2. 业务导向�?Agent Skill 技能定义层
在架构的最前端，系统为每个智能体定义了高度解耦的 Agent Skill（智能体技能）�?原子化能力抽象：将复杂的饮食管理拆解为“营养因子解析”、“热量缺口估算”、“食材OCR识别”等标准技能单元�?意图与技能映射：利用 LangChain 的路由机制，当用户输入指令时，系统首先匹配对应的 Agent Skill 接口。这种设计确保了智能体在执行任务前，已经明确了其职能边界与所需调用的能力范式�?3. RAG 增强的大模型核心推理层（大脑�?在明确技能路径后，系统进入基�?RAG（检索增强生成） 的深度推理阶段�?知识内化与去幻觉：智能体通过挂载�?RAG 模块，实时检索《中国居民膳食指南》及动态更新的食品营养数据库。通过将专业知识注�?Context Window，使大模型在决策时具备行业专家的底座知识，有效抑制了通用模型的“幻觉”现象�?4. ReAct 逻辑范式下的自主推理与技能调�?智能体底层遵�?ReAct 推理范式，面对复杂指令时，智能体通过 MCP 协议动态感知并调用可用�?Agent Skill�?意图拆解与精准匹配：在“思考（Thought）”阶段，智能体将用户需求因子化；在“行动（Action）”阶段，通过 MCP 标准接口精准触发对应�?Agent Skill，避免了传统硬编码模式下的扩展难题�?决策过程透明化：前端通过展示智能体利�?MCP 调取 Skill 的完整路径（Thinking Process），向用户呈现从“识别食物”到“计算热量”的严谨推导过程，提升了系统透明度�?5.基于 MCP 协议的标准工具执行层（四肢）
推理完成后，大模型通过 MCP（Model Context Protocol�?标准协议调用具体的工具集，完成最终的物理执行�?MCP 协议驱动的标准化调用：系统将底层的地�?POI 检索、健康指标计算模块、本地数据库读写等封装为符合 MCP 标准�?Tool。由�?MCP 定义了统一的数据交�?Schema，大模型可以像使用“万能插头”一样，精确、安全地驱动这些外部工具�?执行反馈闭环：MCP 运行环境将工具执行的结果（如“搜索到的低脂餐厅列表”或“识别出的食物营养成分”）实时返回给智能体，由大模型进行最后的逻辑聚合与结果输出�?"""

DEFAULT_CONFIG = {
    "gateway": {
        "host": "0.0.0.0",
        "port": 8003,
        "debug": False,
    },
    "agent": {
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 2048,
        "max_tool_calls": 5,
        "system_prompt": ARCHITECTURE_PROMPT + "\n\n" + "你是 MiniClaw AI 助手，一个插件驱动的智能网关。你可以使用各种工具来帮助用户�?,
    },
    "llm": {
        "api_key": "",
        "base_url": "https://api.deepseek.com/v1",
        "provider": "deepseek",
    },
    "plugins": {
        "enabled": True,
        "builtin_path": "miniclaw.builtins",
    },
    "hooks": {
        "enabled": True,
    },
}


@dataclass
class MiniClawConfig:
    gateway_host: str = "0.0.0.0"
    gateway_port: int = 8003
    gateway_debug: bool = False
    agent_model: str = "deepseek-chat"
    agent_temperature: float = 0.7
    agent_max_tokens: int = 2048
    agent_max_tool_calls: int = 5
    agent_system_prompt: str = DEFAULT_CONFIG["agent"]["system_prompt"]
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_provider: str = "deepseek"
    plugins_enabled: bool = True
    hooks_enabled: bool = True
    _raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MiniClawConfig":
        gw = data.get("gateway", {})
        ag = data.get("agent", {})
        llm = data.get("llm", {})
        pl = data.get("plugins", {})
        hk = data.get("hooks", {})
        return cls(
            gateway_host=gw.get("host", "0.0.0.0"),
            gateway_port=int(gw.get("port", 8003)),
            gateway_debug=gw.get("debug", False),
            agent_model=ag.get("model", "deepseek-chat"),
            agent_temperature=float(ag.get("temperature", 0.7)),
            agent_max_tokens=int(ag.get("max_tokens", 2048)),
            agent_max_tool_calls=int(ag.get("max_tool_calls", 5)),
            agent_system_prompt=ag.get("system_prompt", DEFAULT_CONFIG["agent"]["system_prompt"]),
            llm_api_key=llm.get("api_key", ""),
            llm_base_url=llm.get("base_url", "https://api.deepseek.com/v1"),
            llm_provider=llm.get("provider", "deepseek"),
            plugins_enabled=pl.get("enabled", True),
            hooks_enabled=hk.get("enabled", True),
            _raw=data,
        )

    @classmethod
    def from_env(cls) -> "MiniClawConfig":
        data = {}
        for key in ("MINICLAW_API_KEY", "DEEPSEEK_API_KEY"):
            val = os.getenv(key, "")
            if val:
                data.setdefault("llm", {})["api_key"] = val
        for key in ("MINICLAW_BASE_URL", "DEEPSEEK_BASE_URL"):
            val = os.getenv(key, "")
            if val:
                data.setdefault("llm", {})["base_url"] = val
        if os.getenv("MINICLAW_PORT"):
            data.setdefault("gateway", {})["port"] = int(os.getenv("MINICLAW_PORT"))
        if os.getenv("MINICLAW_HOST"):
            data.setdefault("gateway", {})["host"] = os.getenv("MINICLAW_HOST")
        return cls.from_dict(data)

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "MiniClawConfig":
        config = dict(DEFAULT_CONFIG)
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                config = _deep_merge(config, user_config)
                logger.info(f"配置已从 {config_path} 加载")
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
        env_config = cls.from_env()
        merged = _deep_merge(config, env_config._raw)
        return cls.from_dict(merged)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gateway": {
                "host": self.gateway_host,
                "port": self.gateway_port,
                "debug": self.gateway_debug,
            },
            "agent": {
                "model": self.agent_model,
                "temperature": self.agent_temperature,
                "max_tokens": self.agent_max_tokens,
                "max_tool_calls": self.agent_max_tool_calls,
                "system_prompt": self.agent_system_prompt,
            },
            "llm": {
                "api_key": "***" if self.llm_api_key else "",
                "base_url": self.llm_base_url,
                "provider": self.llm_provider,
            },
            "plugins": {"enabled": self.plugins_enabled},
            "hooks": {"enabled": self.hooks_enabled},
        }


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result

