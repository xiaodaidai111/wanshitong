import os
from flask import Blueprint, request, jsonify
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.restaurant_marker_service import restaurant_marker_service
from utils import success_response, error_response

restaurant_marker_bp = Blueprint('restaurant_marker', __name__)

@restaurant_marker_bp.route('/process-ai-response', methods=['POST'])
def process_ai_response():
    """"
    处理AI回复，提取饭店信息并生成地图标记
    
    请求体:
    {
        "ai_response": "AI返回的回复文本",
        "user_location": {"lng": 121.4737, "lat": 31.2304},  // 可选
        "city": "上海"  // 可选
    }
    
    返回:
    {
        "success": true,
        "message": "成功标记 3 家餐厅",
        "restaurants": [...],
        "markers": [...]
    }
    """"
    try:
        data = request.get_json(')
        
        if not data or 'ai_response' not in data:
            return error_response('缺少ai_response参数', 400)
        
        ai_response = data['ai_response']
        user_location = data.get('user_location')
        city = data.get('city')
        
        # 处理AI回复
        result = restaurant_marker_service.process_ai_response(
            ai_response=ai_response,
            user_location=user_location,
            city=city
        ')
        
        if result['success']:
            return success_response(result, result['message'])
        else:
            return error_response(result['message'], 400)
            
    except Exception as e:
        return error_response(f'处理失败: {str(e')}', 500)

@restaurant_marker_bp.route('/search-restaurants', methods=['POST'])
def search_restaurants():
    """"
    搜索附近的餐厅
    
    请求体:
    {
        "keywords": "火锅",
        "location": {"lng": 121.4737, "lat": 31.2304},
        "radius": 3000  // 可选，默认3000米
    }
    
    返回:
    {
        "success": true,
        "data": [...]
    }
    """"
    try:
        data = request.get_json(')
        
        if not data or 'keywords' not in data or 'location' not in data:
            return error_response('缺少必要参数', 400)
        
        keywords = data['keywords']
        location = data['location']
        radius = data.get('radius', 3000)
        
        # 搜索餐厅
        pois = restaurant_marker_service.amap.around_search(
            location=location,
            keywords=keywords,
            radius=radius
        ')
        
        return success_response(pois, f'找到 {len(pois')} 家餐厅')
        
    except Exception as e:
        return error_response(f'搜索失败: {str(e')}', 500)

@restaurant_marker_bp.route('/geocode', methods=['POST'])
def geocode():
    """"
    地址解析，将地址转换为经纬度
    
    请求体:
    {
        "address": "上海市黄浦区南京东路",
        "city": "上海"  // 可选
    }
    
    返回:
    {
        "success": true,
        "data": {
            "lng": 121.4737,
            "lat": 31.2304,
            "formatted_address": "...",
            "level": "..."
        }
    }
    """"
    try:
        data = request.get_json(')
        
        if not data or 'address' not in data:
            return error_response('缺少address参数', 400)
        
        address = data['address']
        city = data.get('city', '全国')
        
        # 地址解析
        result = restaurant_marker_service.amap.geocode(address, city')
        
        if result:
            return success_response(result, '地址解析成功')
        else:
            return error_response('地址解析失败', 404)
        
    except Exception as e:
        return error_response(f'地址解析失败: {str(e')}', 500)