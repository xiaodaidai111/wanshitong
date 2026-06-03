from flask import Blueprint
from utils import success_response

restaurants_bp = Blueprint('restaurants', __name__)

@restaurants_bp.route('/', methods=['GET'])
def get_restaurants():
    restaurants = [
        {'name': '海底捞火锅', 'rating': 4.9, 'type': '火锅', 'price': 120, 'distance': '1.2km', 'address': '万达广场4楼', 'image': '/static/food.png'},
        {'name': '外婆家', 'rating': 4.6, 'type': '杭帮菜', 'price': 60, 'distance': '800m', 'address': '银泰百货B1', 'image': '/static/food.png'},
        {'name': '星巴克', 'rating': 4.8, 'type': '咖啡', 'price': 35, 'distance': '200m', 'address': '写字楼大堂', 'image': '/static/food.png'},
        {'name': '小龙坎火锅', 'rating': 4.7, 'type': '火锅', 'price': 100, 'distance': '800m', 'address': '银泰百货3楼', 'image': '/static/food.png'},
        {'name': '江户前寿司', 'rating': 4.5, 'type': '日料', 'price': 80, 'distance': '1.5km', 'address': '美食街', 'image': '/static/food.png'}
    ]
    return success_response(restaurants, '获取餐厅列表成功')
