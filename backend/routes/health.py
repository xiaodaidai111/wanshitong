import os
import sys
import logging
from flask import Blueprint, request
from datetime import datetime

# 添加项目根目录到 sys.path，以便导入HealthManager 模块
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from utils import get_db_connection, success_response, error_response, token_required

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)

@health_bp.route('/today', methods=['GET'])
@token_required
def get_today_health():
    user_id = request.user_id
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            today = datetime.CURRENT_TIMESTAMP.strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT 
                    hr.calories, hg.calorie_goal,
                    hr.protein, hg.protein_goal,
                    hr.fat, hg.fat_goal,
                    hr.carbs, hg.carbs_goal,
                    hr.steps, hg.steps_goal,
                    hr.water, hg.water_goal
                FROM health_records hr
                LEFT JOIN health_goals hg ON hg.user_id = hr.user_id
                WHERE hr.user_id = ? AND hr.record_date = ?
            ''', (user_id, today))
            data = cursor.fetchone()
            
            if not data:
                return success_response({'health': {}}, '暂无今日数据')
            
            nutrition = {
                'calories': {'current': data['calories'], 'target': data['calorie_goal']},
                'protein': {'current': data['protein'], 'target': data['protein_goal']},
                'fat': {'current': data['fat'], 'target': data['fat_goal']},
                'carbs': {'current': data['carbs'], 'target': data['carbs_goal']}
            }
            steps = {'current': data['steps'], 'target': data['steps_goal']}
            water = {'current': data['water'], 'target': data['water_goal']}
            body_metrics = [
                {'label': 'BMI', 'value': '21.5', 'icon': '⚖️', 'status': 'warning', 'statusText': '偏高'},
                {'label': '体脂率', 'value': '18%', 'icon': 'fitness', 'status': 'good', 'statusText': '正常'}
            ]
            
            meal_log = []
            cursor.execute('''
                SELECT id, record_date, calories, protein, fat, carbs
                FROM health_records
                WHERE user_id = ? AND record_date = ?
            ''', (user_id, today))
            for record in cursor.fetchall():
                meal_log.append({
                    'id': record['id'],
                    'time': record['record_date'].strftime('%H:%M'),
                    'name': '餐食',
                    'calories': record['calories'],
                    'protein': record['protein'],
                    'fat': record['fat'],
                    'carbs': record['carbs']
                })
            
            return success_response({
                'nutrition': nutrition,
                'steps': steps,
                'water': water,
                'bodyMetrics': body_metrics,
                'mealLog': meal_log
            }, '获取今日健康数据成功')
        except Exception as e:
            return error_response(500, f'获取失败：{str(e)}')

@health_bp.route('/goals', methods=['GET'])
@token_required
def get_goals():
    user_id = request.user_id
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT calorie_goal, protein_goal, fat_goal, carbs_goal, steps_goal, water_goal
                FROM health_goals WHERE user_id = ?
            ''', (user_id,))
            goals = cursor.fetchone()
            if not goals:
                return success_response({'goals': {}}, '暂无目标设定')
            
            nutrient_goals = [
                {'label': '蛋白质', 'value': goals['protein_goal'], 'min': 50, 'max': 200, 'icon': 'meat'},
                {'label': '脂肪', 'value': goals['fat_goal'], 'min': 30, 'max': 100, 'icon': '🥑'},
                {'label': '碳水', 'value': goals['carbs_goal'], 'min': 150, 'max': 400, 'icon': '🍚'}
            ]
            
            return success_response({
                'calorieGoal': goals['calorie_goal'],
                'nutrientGoals': nutrient_goals
            }, '获取目标成功')
        except Exception as e:
            return error_response(500, f'获取失败：{str(e)}')

@health_bp.route('/goals', methods=['PUT'])
@token_required
def update_goals():
    user_id = request.user_id
    data = request.get_json()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE health_goals
                SET calorie_goal = ?, protein_goal = ?, fat_goal = ?, carbs_goal = ?,
                    steps_goal = ?, water_goal = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (
                data.get('calorieGoal', 2000), data.get('proteinGoal', 120),
                data.get('fatGoal', 60), data.get('carbsGoal', 250),
                data.get('stepsGoal', 10000), data.get('waterGoal', 2000),
                user_id
            ))
            conn.commit()
            return success_response(None, '更新目标成功')
        except Exception as e:
            conn.rollback()
            return error_response(500, f'更新失败：{str(e)}')

@health_bp.route('/meal', methods=['POST'])
@token_required
def record_meal():
    user_id = request.user_id
    data = request.get_json()
    if not data:
        return error_response(400, '请求数据格式错误')
    
    calories = int(data.get('calories', 0))
    protein = int(data.get('protein', 0))
    fat = int(data.get('fat', 0))
    carbs = int(data.get('carbs', 0))
    
    if calories < 0 or protein < 0 or fat < 0 or carbs < 0:
        return error_response(400, '营养数值不能为负数')
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            today = datetime.CURRENT_TIMESTAMP.strftime('%Y-%m-%d')
            cursor.execute('''
                INSERT INTO health_records (user_id, record_date, calories, protein, fat, carbs)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, today, calories, protein, fat, carbs))
            conn.commit()
            return success_response(None, '记录饮食成功')
        except Exception as e:
            conn.rollback()
            return error_response(500, f'记录失败：{str(e)}')

@health_bp.route('/water', methods=['POST'])
@token_required
def record_water():
    user_id = request.user_id
    amount = request.get_json().get('amount', 0)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            today = datetime.CURRENT_TIMESTAMP.strftime('%Y-%m-%d')
            cursor.execute('''
                UPDATE health_records SET water = water + ?
                WHERE user_id = ? AND record_date = ?
            ''', (amount, user_id, today))
            conn.commit()
            return success_response(None, '记录饮水成功')
        except Exception as e:
            conn.rollback()
            return error_response(500, f'记录失败：{str(e)}')

@health_bp.route('/chat', methods=['POST'])
@token_required
def health_chat():
    data = request.get_json()
    if not data:
        return error_response(400, "请求数据格式错误")

    messages = data.get("messages", [])
    user_context = data.get("user_context", {})

    if not messages:
        return error_response(400, "消息内容不能为空")

    # 规范化消息格式：将bot 转换为assistant，保持user 不变
    formatted_messages = []
    for msg in messages:
        role = msg.get("role", "user")
        if role == "bot":
            role = "assistant"
        elif role not in ["user", "assistant", "system"]:
            role = "user"
        
        content = msg.get("content", "").strip()
        if content:
            formatted_messages.append({
                "role": role,
                "content": content
            })

    if not formatted_messages:
        return error_response(400, "有效消息为空")

    # 获取用户健康数据以丰富上下文
    user_id = request.user_id
    enhanced_context = build_user_context(user_id, user_context)

    # 调用健康管理智能体（React 架构闭环）
    from HealthManager.HealthManager.agent import generate_health_response
    try:
        result = generate_health_response(formatted_messages, enhanced_context)
        if isinstance(result, dict):
            return success_response({"reply": result.get("reply", ""), "thinking_process": result.get("thinking_process", [])})
        return success_response({"reply": str(result), "thinking_process": []})
    except Exception as e:
        logger.error(f"Health chat error: {str(e)}")
        return error_response(500, f"AI服务暂时不可用，请稍后再试")


def build_user_context(user_id, frontend_context):
    """
    构建完整的用户上下文，包括健康数据
    """
    context = {
        "height": frontend_context.get("height"),
        "weight": frontend_context.get("weight"),
        "computed_bmi": frontend_context.get("computed_bmi"),
        "bmi_status_analysis": frontend_context.get("bmi_status_analysis"),
        "directive": frontend_context.get("directive", "")
    }

    # 从数据库获取用户健康数据
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # 获取用户基本信息
            cursor.execute('''
                SELECT height, weight, age, gender
                FROM users 
                WHERE id = ?
            ''', (user_id,))
            user_info = cursor.fetchone()
            
            if user_info:
                if not context.get("height"):
                    context["height"] = f"{user_info.get('height', 0)}cm"
                if not context.get("weight"):
                    context["weight"] = f"{user_info.get('weight', 0)}kg"
                
                # 计算BMI
                height_m = user_info.get('height', 0) / 100
                weight = user_info.get('weight', 0)
                if height_m > 0 and weight > 0:
                    bmi = round(weight / (height_m * height_m), 1)
                    if not context.get("computed_bmi"):
                        context["computed_bmi"] = str(bmi)
                    
                    # BMI状态分析
                    if not context.get("bmi_status_analysis"):
                        if bmi < 18.5:
                            context["bmi_status_analysis"] = "体重过低"
                        elif bmi < 24:
                            context["bmi_status_analysis"] = "标准健康"
                        elif bmi < 28:
                            context["bmi_status_analysis"] = "超重预警"
                        else:
                            context["bmi_status_analysis"] = "肥胖预警"

            # 获取今日健康记录
            today = datetime.CURRENT_TIMESTAMP.strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT calories, protein, fat, carbs, steps, water
                FROM health_records
                WHERE user_id = ? AND record_date = ?
            ''', (user_id, today))
            today_record = cursor.fetchone()
            
            if today_record:
                context["today_calories"] = today_record.get('calories', 0)
                context["today_protein"] = today_record.get('protein', 0)
                context["today_steps"] = today_record.get('steps', 0)
                context["today_water"] = today_record.get('water', 0)

            # 获取健康目标
            cursor.execute('''
                SELECT calorie_goal, protein_goal, steps_goal, water_goal
                FROM health_goals
                WHERE user_id = ?
            ''', (user_id,))
            goals = cursor.fetchone()
            
            if goals:
                context["calorie_goal"] = goals.get('calorie_goal', 2000)
                context["protein_goal"] = goals.get('protein_goal', 120)
                context["steps_goal"] = goals.get('steps_goal', 10000)
                context["water_goal"] = goals.get('water_goal', 2000)

    except Exception as e:
        logger.warning(f"Failed to build user context: {str(e)}")

    return context
