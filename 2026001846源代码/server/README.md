# 设备检修知识作业系统 - 快速启动指南

## 📋 项目概述

这是一个设备检修知识检索与标准作业系统，基于 Flask 后端 + uni-app 前端构建。

## 🚀 快速开始

### 方式一：使用快速启动脚本（推荐）

#### Windows 用户

```bash
# 1. 双击运行快速启动脚本
quick_start.bat

# 2. 按照提示操作：
#    - 检查系统环境
#    - 配置数据库连接
#    - 安装 Python 依赖
#    - 启动后端服务
```

#### Linux/Mac 用户

```bash
# 1. 添加执行权限
chmod +x quick_start.sh

# 2. 运行快速启动脚本
sudo ./quick_start.sh

# 3. 按照提示操作
```

### 方式二：手动部署

#### 1. 环境要求

- **Python**: 3.8+
- **MySQL**: 5.7+
- **Node.js**: 16+ (用于前端开发，可选)

#### 2. 安装系统依赖

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-client
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip mysql
```

**Windows:**
- 安装 Python 3.8+: https://www.python.org/downloads/
- 安装 MySQL: https://dev.mysql.com/downloads/installer/

#### 3. 配置数据库

```bash
# 1. 登录 MySQL
mysql -u root -p

# 2. 创建数据库
CREATE DATABASE health_diet_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON health_diet_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 3. 导入表结构
cd database
mysql -u root -p health_diet_db < schema.sql
mysql -u root -p health_diet_db < community_schema.sql
mysql -u root -p health_diet_db < equipment_maintenance_schema.sql
mysql -u root -p health_diet_db < init.sql
```

#### 4. 配置后端

```bash
# 1. 进入后端目录
cd backend

# 2. 复制环境变量模板
cp .env.example .env

# 3. 编辑 .env 文件，配置以下内容：
#    - DATABASE_HOST (数据库主机)
#    - DATABASE_PORT (数据库端口)
#    - DATABASE_USER (数据库用户)
#    - DATABASE_PASSWORD (数据库密码)
#    - DATABASE_NAME (数据库名称)
#    - DASHSCOPE_API_KEY (阿里云百炼 API Key)
```

#### 5. 创建虚拟环境并安装依赖

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

#### 6. 启动后端服务

```bash
# 确保虚拟环境已激活
python unified_app.py
```

服务启动后，访问 http://localhost:5000 验证。

## 🔧 配置说明

### 环境变量配置 (.env)

```bash
# 数据库配置
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=your_password
DATABASE_NAME=health_diet_db

# 安全密钥
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# AI 服务配置 (必需)
DASHSCOPE_API_KEY=your_dashscope_api_key

# 地图服务 (可选)
AMAP_API_KEY=your_amap_api_key
```

### 获取 API Key

1. **阿里云百炼 (DashScope)**: https://dashscope.console.aliyun.com/
2. **高德地图 (AMap)**: https://lbs.amap.com/

## 📦 项目结构

```
server/
├── backend/                    # 后端代码
│   ├── routes/                 # 路由模块
│   ├── services/               # 业务逻辑
│   ├── unified_app.py          # 主入口
│   ├── requirements.txt        # Python 依赖
│   └── .env                    # 环境变量
├── database/                   # 数据库脚本
│   ├── schema.sql              # 主表结构
│   ├── community_schema.sql    # 社区模块
│   └── ...
├── map-agent/                  # 地图智能体
├── start_all_services.py       # 服务管理脚本
├── quick_start.sh              # Linux 快速启动
├── quick_start.bat             # Windows 快速启动
├── deploy_check.py             # 部署检查脚本
└── init_database.py            # 数据库初始化脚本
```

## 🧪 测试部署

### 1. 运行部署检查脚本

```bash
python deploy_check.py
```

该脚本会检查：
- ✅ Python 环境
- ✅ MySQL 数据库
- ✅ 项目目录
- ✅ 环境配置
- ✅ Python 依赖
- ✅ 端口可用性

### 2. 测试 API 接口

```bash
# 系统健康检查
curl http://localhost:5000/

# 获取系统信息
curl http://localhost:5000/api/system/health
```

### 3. 测试用户注册

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000", "password": "test123", "name": "测试用户"}'
```

## 🐛 常见问题

### Q1: 后端启动失败

**症状**: `python unified_app.py` 报错

**解决方案**:
```bash
# 1. 检查 Python 依赖
pip list | grep flask

# 2. 检查 .env 配置
cat .env | grep DATABASE

# 3. 测试数据库连接
mysql -u root -p -e "SHOW DATABASES;"

# 4. 查看详细错误
python unified_app.py 2>&1 | tee startup.log
```

### Q2: 数据库连接失败

**症状**: `pymysql.err.OperationalError`

**解决方案**:
```bash
# 1. 检查 MySQL 服务状态
sudo systemctl status mysql

# 2. 检查密码是否正确
mysql -u root -p

# 3. 检查用户权限
mysql -u root -p -e "SELECT user, host FROM mysql.user;"
```

### Q3: 缺少 Python 包

**症状**: `ModuleNotFoundError`

**解决方案**:
```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 重新安装依赖
pip install -r requirements.txt
```

### Q4: 端口被占用

**症状**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# 终止进程
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

## 📊 功能列表

- ✅ 用户认证（注册、登录、Token）
- ✅ 设备管理（添加、查询、状态监控）
- ✅ 智能问答（AI 助手）
- ✅ 检修评估（设备故障诊断）
- ✅ 标准化作业（作业指引）
- ✅ 空间智能（地图服务）
- ✅ 知识库（LightRAG）
- ✅ 社区功能（案例分享）
- ✅ 语音识别（ASR/TTS）

## 🔗 相关链接

- **阿里云百炼**: https://dashscope.console.aliyun.com/
- **高德地图**: https://lbs.amap.com/
- **Flask 文档**: https://flask.palletsprojects.com/
- **PyMySQL 文档**: https://pymysql.readthedocs.io/

## 📞 技术支持

遇到问题？请查看：
1. **日志文件**: 后端启动时的控制台输出
2. **部署检查**: 运行 `python deploy_check.py`
3. **详细文档**: 查看 `../PROJECT_CHECK_REPORT.md`

## 📝 更新日志

### v1.0.0 (2026-06-16)
- ✅ 初始版本发布
- ✅ 完成所有核心功能
- ✅ 添加快速启动脚本
- ✅ 添加部署检查工具

---

**项目团队**: 软件杯竞赛团队
**最后更新**: 2026-06-16
