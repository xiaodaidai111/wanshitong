"""内置插件：系统操作工具

提供操作整个系统各个功能模块的工具，包括健康管理、烹饪专家、外卖评估等。
"""
import requests
import json
from miniclaw.tools import BaseTool, ToolResult, ToolParameter


class HealthManagerTool(BaseTool):
    name = "health_manager"
    description = "健康管理模块操作工具，用于获取健康评分、健康建议等"
    parameters = [
        ToolParameter(name="action", type="string", description="操作类型: 'get_score'(获取健康评分), 'get_suggestions'(获取健康建议), 'update_profile'(更新健康档案)"),
        ToolParameter(name="user_id", type="string", description="用户ID", required=False),
        ToolParameter(name="data", type="object", description="操作数据，根据action不同而不同", required=False),
    ]

    def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action", "").strip().lower()
        user_id = kwargs.get("user_id", "1")  # 默认用户ID
        data = kwargs.get("data", {})

        if not action:
            return ToolResult(success=False, output="", error="操作类型不能为空")

        try:
            # 这里应该调用健康管理模块的API
            # 模拟API调用
            if action == "get_score":
                result = {
                    "user_id": user_id,
                    "score": 85,
                    "level": "良好",
                    "suggestions": ["保持良好的饮食习惯", "增加运动量", "保证充足睡眠"]
                }
                output = f"健康评分: {result['score']}\n健康等级: {result['level']}\n建议: {', '.join(result['suggestions'])}"
            elif action == "get_suggestions":
                suggestions = ["多吃蔬菜水果", "每天运动30分钟", "保持心情愉悦"]
                output = "健康建议: " + ", ".join(suggestions)
            elif action == "update_profile":
                output = f"健康档案已更新: {json.dumps(data, ensure_ascii=False)}"
            else:
                return ToolResult(success=False, output="", error=f"不支持的操作: {action}")

            return ToolResult(success=True, output=output, metadata={"action": action, "result": result if 'result' in locals() else {}})
        except Exception as e:
            return ToolResult(success=False, output="", error=f"操作失败: {str(e)}")


class CookingExpertTool(BaseTool):
    name = "cooking_expert"
    description = "烹饪专家模块操作工具，用于获取食谱推荐、烹饪指导等"
    parameters = [
        ToolParameter(name="action", type="string", description="操作类型: 'get_recipes'(获取食谱), 'get_cooking_guide'(获取烹饪指导), 'search_recipes'(搜索食谱)"),
        ToolParameter(name="keywords", type="string", description="搜索关键词", required=False),
        ToolParameter(name="recipe_id", type="string", description="食谱ID", required=False),
    ]

    def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action", "").strip().lower()
        keywords = kwargs.get("keywords", "")
        recipe_id = kwargs.get("recipe_id", "")

        if not action:
            return ToolResult(success=False, output="", error="操作类型不能为空")

        try:
            if action == "get_recipes":
                recipes = [
                    {"id": "1", "name": "麻婆豆腐", "cooking_time": "30分钟", "difficulty": "中等"},
                    {"id": "2", "name": "红烧排骨", "cooking_time": "45分钟", "difficulty": "中等"},
                    {"id": "3", "name": "清炒时蔬", "cooking_time": "15分钟", "difficulty": "简单"}
                ]
                output = "推荐食谱:\n" + "\n".join([f"  {r['name']} (烹饪时间: {r['cooking_time']}, 难度: {r['difficulty']})" for r in recipes])
            elif action == "search_recipes":
                if not keywords:
                    return ToolResult(success=False, output="", error="搜索关键词不能为空")
                output = f"搜索 '{keywords}' 的食谱: 找到3个相关食谱"
            elif action == "get_cooking_guide":
                if not recipe_id:
                    return ToolResult(success=False, output="", error="食谱ID不能为空")
                output = f"食谱 {recipe_id} 的烹饪指导: 1. 准备食材 2. 热锅倒油 3. 放入主料 4. 调味 5. 翻炒出锅"
            else:
                return ToolResult(success=False, output="", error=f"不支持的操作: {action}")

            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, output="", error=f"操作失败: {str(e)}")


class TakeawayAssessmentTool(BaseTool):
    name = "takeaway_assessment"
    description = "外卖评估模块操作工具，用于评估外卖健康度、获取健康外卖推荐等"
    parameters = [
        ToolParameter(name="action", type="string", description="操作类型: 'assess_health'(评估外卖健康度), 'get_healthy_recommendations'(获取健康外卖推荐)"),
        ToolParameter(name="food_name", type="string", description="外卖名称", required=False),
        ToolParameter(name="restaurant", type="string", description="餐厅名称", required=False),
    ]

    def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action", "").strip().lower()
        food_name = kwargs.get("food_name", "")
        restaurant = kwargs.get("restaurant", "")

        if not action:
            return ToolResult(success=False, output="", error="操作类型不能为空")

        try:
            if action == "assess_health":
                if not food_name:
                    return ToolResult(success=False, output="", error="外卖名称不能为空")
                output = f"{food_name} 的健康评估: 健康评分 75/100，建议适量食用"
            elif action == "get_healthy_recommendations":
                recommendations = ["沙拉套餐", "清蒸鱼", "蔬菜三明治"]
                output = "健康外卖推荐: " + ", ".join(recommendations)
            else:
                return ToolResult(success=False, output="", error=f"不支持的操作: {action}")

            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, output="", error=f"操作失败: {str(e)}")


class RestaurantRecommendationTool(BaseTool):
    name = "restaurant_recommendation"
    description = "餐厅推荐模块操作工具，用于获取附近餐厅、餐厅评分等"
    parameters = [
        ToolParameter(name="action", type="string", description="操作类型: 'get_nearby'(获取附近餐厅), 'get_reviews'(获取餐厅评价)"),
        ToolParameter(name="location", type="string", description="位置", required=False),
        ToolParameter(name="restaurant_id", type="string", description="餐厅ID", required=False),
    ]

    def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action", "").strip().lower()
        location = kwargs.get("location", "当前位置")
        restaurant_id = kwargs.get("restaurant_id", "")

        if not action:
            return ToolResult(success=False, output="", error="操作类型不能为空")

        try:
            if action == "get_nearby":
                restaurants = [
                    {"id": "1", "name": "健康餐厅", "distance": "500米", "rating": "4.5"},
                    {"id": "2", "name": "绿色食堂", "distance": "800米", "rating": "4.2"}
                ]
                output = f"{location} 附近的餐厅:\n" + "\n".join([f"  {r['name']} (距离: {r['distance']}, 评分: {r['rating']})" for r in restaurants])
            elif action == "get_reviews":
                if not restaurant_id:
                    return ToolResult(success=False, output="", error="餐厅ID不能为空")
                output = f"餐厅 {restaurant_id} 的评价: 环境好，服务周到，菜品健康"
            else:
                return ToolResult(success=False, output="", error=f"不支持的操作: {action}")

            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, output="", error=f"操作失败: {str(e)}")


class UserManagementTool(BaseTool):
    name = "user_management"
    description = "用户管理模块操作工具，用于获取用户信息、更新用户资料等"
    parameters = [
        ToolParameter(name="action", type="string", description="操作类型: 'get_profile'(获取用户资料), 'update_profile'(更新用户资料), 'get_achievements'(获取用户成就)"),
        ToolParameter(name="user_id", type="string", description="用户ID", required=False),
        ToolParameter(name="data", type="object", description="更新数据", required=False),
    ]

    def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action", "").strip().lower()
        user_id = kwargs.get("user_id", "1")  # 默认用户ID
        data = kwargs.get("data", {})

        if not action:
            return ToolResult(success=False, output="", error="操作类型不能为空")

        try:
            if action == "get_profile":
                profile = {
                    "user_id": user_id,
                    "name": "张三",
                    "age": 25,
                    "gender": "男",
                    "height": 175,
                    "weight": 65
                }
                output = f"用户资料:\n" + "\n".join([f"  {k}: {v}" for k, v in profile.items()])
            elif action == "update_profile":
                output = f"用户资料已更新: {json.dumps(data, ensure_ascii=False)}"
            elif action == "get_achievements":
                achievements = ["健康达人", "烹饪新手", "外卖鉴赏家"]
                output = "用户成就: " + ", ".join(achievements)
            else:
                return ToolResult(success=False, output="", error=f"不支持的操作: {action}")

            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, output="", error=f"操作失败: {str(e)}")


def register(api):
    api.register_tool(HealthManagerTool())
    api.register_tool(CookingExpertTool())
    api.register_tool(TakeawayAssessmentTool())
    api.register_tool(RestaurantRecommendationTool())
    api.register_tool(UserManagementTool())
