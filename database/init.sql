CREATE DATABASE IF NOT EXISTS food_map_expert_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE food_map_expert_db;

-- Users matching your requirements (optional if you want user management later)
-- CREATE TABLE IF NOT EXISTS users ( ... );

-- Restaurants Data
CREATE TABLE IF NOT EXISTS restaurant (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rating FLOAT,
    type VARCHAR(50),
    price DECIMAL(10, 2),
    distance VARCHAR(20),
    address VARCHAR(255),
    image VARCHAR(255)
);

-- Insert sample data matching frontend Mock
INSERT INTO restaurant (name, rating, type, price, distance, address, image) VALUES 
('海底捞火锅', 4.9, '火锅', 120.00, '1.2km', '万达广场4楼', '/static/food.png'),
('外婆家', 4.6, '杭帮菜', 60.00, '800m', '银泰百货B1', '/static/food.png'),
('星巴克', 4.8, '咖啡', 35.00, '200m', '写字楼大堂', '/static/food.png'),
('肯德基', 4.5, '快餐', 40.00, '500m', '步行街中心', '/static/food.png'),
('必胜客', 4.7, '披萨', 80.00, '600m', '购物中心1楼', '/static/food.png');
