from map_agent.map_processor import MapProcessor

# 初始化地图处理器
mp = MapProcessor()

# 武汉理工大学南湖校区的经纬度
location = (30.50962, 114.328161)

# 搜索附近1000米内的餐厅
results = mp.search_nearby(location, 1000, '餐厅')

# 打印结果
print('Found', len(results), 'restaurants near Wuhan University of Technology Nanhu Campus:')
for i, restaurant in enumerate(results[:10]):
    name = restaurant.get('name', 'Unknown')
    address = restaurant.get('address', 'Unknown')
    rating = restaurant.get('rating', 'N/A')
    print(f'{i+1}. {name} - {address} - Rating: {rating}')
