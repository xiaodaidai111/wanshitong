from typing import Any, Dict, List


class HealthRagLookupTool:
    name = "health_rag_lookup"
    description = "糖豆：检索健康知识库并返回摘要"

    def __init__(self, agent):
        self.agent = agent

    def run(self, query: str) -> Dict[str, Any]:
        context = self.agent._build_rag_context(query, top_k=3)
        return {"query": query, "context": context}


def get_health_tools(agent) -> List[Any]:
    return [HealthRagLookupTool(agent)]
