# 设备检修知识作业系统 - 项目检查报告

## 📋 项目概述

**项目名称**: 设备检修知识检索与标准作业系统
**技术栈**:
- 前端: uni-app (Vue.js) + HBuilderX
- 后端: Python 3 + Flask
- 数据库: MySQL 5.7+
- AI服务: 阿里云百炼 (DashScope)

**主要功能**:
- 智能问答助手 (团团)
- 检修评估智能体
- 标准化作业指引
- 空间智能服务
- 知识库检索 (LightRAG)

---

## ✅ 已确认完整的部分

### 1. 前端代码 ✅
- **位置**: `frontend/`
- **状态**: 已编译为 H5 版本 (`frontend/dist/build/h5/`)
- **配置文件**: `manifest.json`, `pages.json`, `package.json`
- **依赖**: `node_modules` 已安装

### 2. 后端代码 ✅
- **位置**: `server/backend/`
- **主入口**: `unified_app.py`
- **路由文件**: 20+ 个路由模块已就位
- **服务目录**:
  - `routes/` - 路由模块
  - `services/` - 业务逻辑
  - `RAG/` - 知识检索模块
  - `map_agent/` - 地图智能体

### 3. 数据库 Schema ✅
- **位置**: `server/database/`
- **SQL文件**:
  - `schema.sql` - 主数据库结构
  - `community_schema.sql` - 社区模块
  - `equipment_maintenance_schema.sql` - 设备维护
  - `health_score_schema.sql` - 健康评分
  - `recipe_recommendation_schema.sql` - 维修推荐
  - `init.sql` - 初始化脚本

### 4. 部署配置 ✅
- **部署指南**: `deploy/DEPLOY_GUIDE.md`
- **部署脚本**: `deploy/deploy.sh`
- **环境变量模板**: `server/backend/.env.example`

---

## ⚠️ 需要解决的问题

### 1. 🚨 HealthManager 目录缺失 (严重)

**问题**: `start_all_services.py` 引用了 `HealthManager` 模块，但该目录不存在

```python
# start_all_services.py 第 817 行引用
"HealthManager/run.py": script_dir / "HealthManager" / "HealthManager" / "run.py",
```

**影响**:
- 启动脚本会报错
- 标准化作业服务无法启动

**解决方案**:

**方案 A (推荐)**: 创建 HealthManager 模块
```bash
mkdir -p server/HealthManager/HealthManager
# 添加相应的 Python 代码文件
```

**方案 B**: 修改启动脚本移除相关服务
编辑 `server/start_all_services.py`，注释掉 HealthManager 相关代码

**方案 C**: 使用统一后端的 health 路由
项目已在 `routes/health.py` 中实现了标准化作业功能，可以不启动独立服务

---

### 2. 🔑 数据库密码加密问题 (严重)

**问题**: `.env` 文件中的数据库密码使用了加密格式

```env
DATABASE_PASSWORD=ENC:gAAAAABpt_etJ3R1F7AhCU6BAkwj9IPOx6hOb9ORKenBu1lUozGV7tOoysiORCJTBBEX6FDiQEv7rhY8C-QuF9DgYKB7hKquqA==
```

**影响**:
- 数据库连接会失败
- 需要配置加密密钥或使用明文密码

**解决方案**:

**方案 A (简单)**: 修改为明文密码
```bash
cd server/backend
# 编辑 .env 文件
DATABASE_PASSWORD=your_actual_mysql_password
```

**方案 B (安全)**: 配置加密环境变量
在 `.env` 中添加:
```env
DATABASE_ENCRYPTION_KEY=your_encryption_key
DATABASE_ENCRYPTION_SALT=your_encryption_salt
```

---

### 3. 📦 Python 依赖安装 (必需)

**位置**: `server/backend/requirements.txt`

**必需安装**:
```bash
cd server/backend
pip install -r requirements.txt
```

**主要依赖**:
- flask
- flask-cors
- python-dotenv
- pymysql
- dashscope
- lightrag-hku
- opencv-python
- ultralytics
- PyJWT

**注意**: 部分包 (如 opencv, ultralytics) 可能需要系统依赖

---

### 4. 🗄️ MySQL 数据库安装与配置 (必需)

**数据库名**: `health_diet_db`
**默认配置**:
- 主机: localhost
- 端口: 3306
- 用户: root

**安装步骤**:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server mysql-client

# CentOS/RHEL
sudo yum install mysql-server mysql

# 启动 MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# 创建数据库和用户
mysql -u root -p
```

**数据库初始化**:
```sql
CREATE DATABASE health_diet_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON health_diet_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

**导入 Schema**:
```bash
cd server/database
mysql -u root -p health_diet_db < schema.sql
mysql -u root -p health_diet_db < community_schema.sql
mysql -u root -p health_diet_db < equipment_maintenance_schema.sql
mysql -u root -p health_diet_db < init.sql
```

---

### 5. 🔑 API 密钥配置 (必需)

**文件**: `server/backend/.env`

**必需配置**:

```env
# 阿里云百炼 API Key (必需)
DASHSCOPE_API_KEY=your_dashscope_api_key

# 地图服务 (可选，如果使用地图功能)
AMAP_API_KEY=your_amap_api_key

# DeepSeek API (可选，如果使用 DeepSeek 模型)
DEEPSEEK_API_KEY=your_deepseek_api_key
```

**获取 API Key**:
1. 阿里云百炼: https://dashscope.console.aliyun.com/
2. 高德地图: https://lbs.amap.com/
3. DeepSeek: https://platform.deepseek.com/

---

### 6. 📁 目录结构问题 (轻微)

**问题**: 部分目录结构不一致

**缺失的目录**:
- `server/HealthManager/` - 标准化作业独立服务
- `server/uploads/` - 文件上传目录 (已在代码中自动创建)

**解决方案**:
```bash
mkdir -p server/uploads
mkdir -p server/backend/uploads
```

---

## 🛠️ 部署步骤 (推荐顺序)

### 步骤 1: 系统环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.10+
sudo apt install python3 python3-pip python3-venv

# 安装 MySQL
sudo apt install mysql-server mysql-client

# 安装 Node.js (用于前端开发)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# 安装 Nginx (用于反向代理)
sudo apt install nginx
```

### 步骤 2: 上传项目文件

```bash
# 上传项目到服务器
scp -r "2026001846源代码/" user@server:/opt/device-maintenance/

# 或者使用 tar 打包
cd "D:/竞赛/软件杯/2026001846源代码"
tar -czf deploy-package.tar.gz server/ frontend/dist/
scp deploy-package.tar.gz user@server:/tmp/
```

### 步骤 3: 配置数据库

```bash
# SSH 登录服务器
ssh user@server

# 配置 MySQL
sudo mysql_secure_installation

# 创建数据库
mysql -u root -p
```

```sql
CREATE DATABASE health_diet_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'maintenance_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON health_diet_db.* TO 'maintenance_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

```bash
# 导入数据库结构
cd /opt/device-maintenance/server/database
mysql -u maintenance_user -p health_diet_db < schema.sql
mysql -u maintenance_user -p health_diet_db < community_schema.sql
mysql -u maintenance_user -p health_diet_db < equipment_maintenance_schema.sql
mysql -u maintenance_user -p health_diet_db < init.sql
```

### 步骤 4: 配置后端

```bash
cd /opt/device-maintenance/server/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env
```

**编辑 .env 文件**:
```env
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=maintenance_user
DATABASE_PASSWORD=your_password
DATABASE_NAME=health_diet_db
DASHSCOPE_API_KEY=your_dashscope_api_key
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

### 步骤 5: 测试后端启动

```bash
cd /opt/device-maintenance/server/backend
source venv/bin/activate

# 直接运行测试
python unified_app.py

# 或者使用启动脚本
cd /opt/device-maintenance/server
python start_all_services.py
```

**验证**:
```bash
# 新终端
curl http://localhost:5000/
curl http://localhost:5000/api/system/health
```

### 步骤 6: 配置 Systemd 服务

```bash
sudo tee /etc/systemd/system/maintenance-backend.service << 'EOF'
[Unit]
Description=Equipment Maintenance Backend
After=network.target mysql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/device-maintenance/server/backend
Environment="PATH=/opt/device-maintenance/server/backend/venv/bin"
ExecStart=/opt/device-maintenance/server/backend/venv/bin/python unified_app.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable maintenance-backend
sudo systemctl start maintenance-backend
```

### 步骤 7: 配置 Nginx

```bash
sudo tee /etc/nginx/sites-available/maintenance << 'EOF'
server {
    listen 80;
    server_name your_domain_or_IP;

    # 前端静态文件
    location / {
        root /opt/device-maintenance/frontend/dist/build/h5;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # 其他后端路由
    location ~ ^/(cook-agent|tuantuan|takeout|health|map|openclaw|speech|rag)/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源
    location /static/ {
        alias /opt/device-maintenance/server/backend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 上传文件
    location /uploads/ {
        alias /opt/device-maintenance/server/uploads/;
        expires 30d;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 日志
    access_log /var/log/nginx/maintenance_access.log;
    error_log /var/log/nginx/maintenance_error.log;
}
EOF

sudo ln -s /etc/nginx/sites-available/maintenance /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 步骤 8: 配置防火墙

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS (如果使用 SSL)
sudo ufw enable
```

---

## 🧪 验证部署

### 1. 检查服务状态

```bash
# 检查后端服务
sudo systemctl status maintenance-backend
sudo journalctl -u maintenance-backend -f

# 检查 MySQL
sudo systemctl status mysql

# 检查 Nginx
sudo systemctl status nginx
```

### 2. 测试 API 接口

```bash
# 系统健康检查
curl http://localhost/api/system/health

# 获取首页数据
curl http://localhost/api/dashboard/overview

# 用户注册测试
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000", "password": "test123", "name": "测试用户"}'
```

### 3. 浏览器访问

- 主页: `http://your_server_ip/`
- API 文档: `http://your_server_ip/api/`

---

## 📊 功能清单

### ✅ 核心功能 (已实现)

| 功能 | 路由 | 说明 |
|------|------|------|
| 用户认证 | `/api/auth/*` | 注册、登录、Token 管理 |
| 用户管理 | `/api/user/*` | 个人信息、成就系统 |
| 智能问答 | `/cook-agent/*` | AI 问答助手 |
| 检修评估 | `/takeout/*` | 设备检修评估智能体 |
| 社区功能 | `/api/community/*` | 知识分享、案例库 |
| 健康管理 | `/health/*` | 标准化作业指引 |
| 空间智能 | `/map/*` | 地图服务、位置查询 |
| 维修推荐 | `/api/recipe-recommendation/*` | 维修方案推荐 |
| 语音识别 | `/api/speech/*` | ASR/TTS 服务 |
| 知识图谱 | `/api/rag/*` | LightRAG 知识检索 |
| 监控服务 | `/api/*` | 系统监控、性能指标 |

### ⚠️ 可选功能 (可能需要额外配置)

| 功能 | 依赖 | 说明 |
|------|------|------|
| 地图服务 | 高德地图 API Key | 需要配置 `AMAP_API_KEY` |
| DeepSeek 模型 | DeepSeek API Key | 可选，可使用通义千问替代 |
| YOLO 目标检测 | ultralytics, opencv | 用于设备图片识别 |
| 语音服务 | DashScope ASR/TTS | 需要公网可访问地址 |

---

## 🔧 常见问题排查

### Q1: 后端启动失败

**症状**: `python unified_app.py` 报错

**排查步骤**:
```bash
# 1. 检查 Python 依赖
pip list | grep flask

# 2. 检查 .env 文件
cat .env | head -20

# 3. 检查数据库连接
mysql -u root -p -e "SHOW DATABASES;"

# 4. 查看详细错误
python unified_app.py 2>&1 | tee startup.log
```

### Q2: 数据库连接失败

**症状**: `pymysql.err.OperationalError`

**解决方案**:
```bash
# 1. 检查 MySQL 是否运行
sudo systemctl status mysql

# 2. 检查密码是否正确
mysql -u maintenance_user -p

# 3. 检查用户权限
mysql -u root -p -e "SELECT user, host FROM mysql.user;"

# 4. 重置密码 (如果需要)
mysql -u root -p
ALTER USER 'maintenance_user'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

### Q3: API 接口 404

**症状**: 访问 `/api/xxx` 返回 404

**排查步骤**:
```bash
# 1. 检查路由是否注册
grep -r "xxx_bp" server/backend/routes/

# 2. 检查 Nginx 配置
sudo nginx -t
cat /etc/nginx/sites-available/maintenance

# 3. 检查后端日志
sudo journalctl -u maintenance-backend -n 100

# 4. 直接测试后端端口
curl http://localhost:5000/api/xxx
```

### Q4: 前端页面空白

**症状**: 浏览器打开后白屏

**排查步骤**:
```bash
# 1. 检查前端文件
ls -la /opt/device-maintenance/frontend/dist/build/h5/

# 2. 检查 index.html
cat /opt/device-maintenance/frontend/dist/build/h5/index.html

# 3. 检查浏览器控制台
# F12 -> Console -> 查看错误信息

# 4. 检查 API 请求
# F12 -> Network -> 查看请求状态
```

---

## 📝 优化建议

### 1. 安全优化

```bash
# 1. 生成随机密钥
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 2. 配置 HTTPS
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com

# 3. 限制上传大小
# 在 Nginx 配置中添加
client_max_body_size 16M;
```

### 2. 性能优化

```bash
# 1. 使用 Gunicorn 生产服务器
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 unified_app:create_unified_app()

# 2. 配置 MySQL 连接池
# .env 文件
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# 3. 启用 Redis 缓存 (可选)
sudo apt install redis-server
pip install redis
```

### 3. 监控优化

```bash
# 1. 配置日志轮转
sudo tee /etc/logrotate.d/maintenance << 'EOF'
/opt/device-maintenance/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0640 www-data www-data
}
EOF

# 2. 安装监控工具
pip install prometheus-client
# 配置 Grafana 监控
```

---

## 🎯 快速部署清单

- [ ] 安装系统依赖 (Python, MySQL, Nginx)
- [ ] 上传项目文件到服务器
- [ ] 创建 MySQL 数据库和用户
- [ ] 导入数据库 Schema
- [ ] 配置 `.env` 文件 (数据库密码、API Key)
- [ ] 安装 Python 依赖 (`pip install -r requirements.txt`)
- [ ] 测试后端启动 (`python unified_app.py`)
- [ ] 配置 Systemd 服务
- [ ] 配置 Nginx 反向代理
- [ ] 配置防火墙规则
- [ ] 测试所有 API 接口
- [ ] 浏览器访问前端页面
- [ ] 配置 SSL 证书 (推荐)
- [ ] 配置监控和日志

---

## 📞 技术支持

**日志位置**:
- 后端日志: `sudo journalctl -u maintenance-backend`
- Nginx 日志: `/var/log/nginx/maintenance_*.log`
- MySQL 日志: `/var/log/mysql/error.log`

**配置文件位置**:
- 后端配置: `/opt/device-maintenance/server/backend/.env`
- Nginx 配置: `/etc/nginx/sites-available/maintenance`
- Systemd 配置: `/etc/systemd/system/maintenance-backend.service`

---

**文档版本**: v1.0
**最后更新**: 2026-06-16
**适用环境**: Linux (Ubuntu 20.04+, CentOS 7+, 银河麒麟 V10/V11)
