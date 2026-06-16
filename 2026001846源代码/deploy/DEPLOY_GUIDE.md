# 设备检修知识作业系统 - 部署指南

## 适用环境

- **CPU**: LoongArch 自主指令集架构（龙芯）
- **操作系统**: 银河麒麟高级服务器操作系统 V10/V11
- **硬件要求**: 4核 CPU / 8GB 内存 / 256GB 硬盘

---

## 一、部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                LoongArch + 银河麒麟服务器                      │
│                                                             │
│  ┌───────────────┐         ┌───────────────┐               │
│  │     Nginx     │ ──────→ │   Flask 后端   │               │
│  │  (前端 H5)    │         │   (Python)    │               │
│  └───────────────┘         └───────────────┘               │
│         │                         │                        │
│    80/443 端口               5000 端口                      │
│         │                         │                        │
│         ▼                         ▼                        │
│  ┌───────────────┐         ┌───────────────┐               │
│  │   静态文件    │         │    SQLite     │               │
│  │  (HTML/JS/CSS)│         │    数据库     │               │
│  └───────────────┘         └───────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、部署前准备

### 2.1 在开发机上编译前端

**重要**: uni-app 需要编译为 H5 网页版本才能在服务器上运行

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 编译 H5 版本
npm run build:h5

# 编译完成后，会在 dist/build/h5 目录生成静态文件
```

### 2.2 准备部署文件

将以下文件打包上传到服务器：

```
deploy-package/
├── deploy/                    # 部署脚本
│   ├── deploy.sh             # 一键部署脚本
│   └── DEPLOY_GUIDE.md       # 本文档
├── server/
│   └── backend/              # 后端代码
└── frontend/
    └── dist/
        └── build/
            └── h5/           # 编译后的前端文件
```

---

## 三、一键部署（推荐）

### 3.1 上传部署包到服务器

```bash
# 在开发机上打包
tar -czf deploy-package.tar.gz deploy/ server/backend/ frontend/dist/

# 上传到服务器（替换为实际 IP）
scp deploy-package.tar.gz user@server-ip:/tmp/

# 登录服务器
ssh user@server-ip

# 解压
cd /tmp
tar -xzf deploy-package.tar.gz
cd deploy-package
```

### 3.2 执行部署脚本

```bash
# 添加执行权限
chmod +x deploy/deploy.sh

# 执行部署
sudo bash deploy/deploy.sh
```

脚本会自动完成：
1. ✅ 检查系统环境（LoongArch + 银河麒麟）
2. ✅ 安装系统依赖
3. ✅ 创建目录结构
4. ✅ 部署后端代码
5. ✅ 配置环境变量
6. ✅ 部署前端代码
7. ✅ 配置 Systemd 服务
8. ✅ 配置 Nginx
9. ✅ 启动服务
10. ✅ 验证部署

---

## 四、手动部署（如果一键脚本失败）

### 4.1 安装系统依赖

```bash
# 更新系统
sudo yum update -y

# 安装必要软件
sudo yum install -y \
    python3 \
    python3-pip \
    python3-devel \
    gcc \
    nginx \
    wget \
    curl \
    git
```

### 4.2 部署后端

```bash
# 创建目录
sudo mkdir -p /opt/device-maintenance/backend
sudo mkdir -p /opt/device-maintenance/frontend
sudo chown -R $USER:$USER /opt/device-maintenance

# 复制后端代码
cp -r server/backend/* /opt/device-maintenance/backend/

# 创建虚拟环境
cd /opt/device-maintenance/backend
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install flask flask-cors python-dotenv gunicorn
pip install requests pillow
pip freeze > requirements.txt

# 退出虚拟环境
deactivate
```

### 4.3 配置环境变量

```bash
cat > /opt/device-maintenance/backend/.env << 'EOF'
FLASK_APP=unified_app.py
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=sqlite:///database.db
AI_API_KEY=your-api-key
AI_BASE_URL=https://api.deepseek.com
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
EOF
```

### 4.4 部署前端

```bash
# 复制编译好的前端文件
cp -r frontend/dist/build/h5/* /opt/device-maintenance/frontend/
```

### 4.5 配置 Systemd 服务

```bash
sudo tee /etc/systemd/system/device-maintenance.service << 'EOF'
[Unit]
Description=Device Maintenance Backend
After=network.target

[Service]
User=$(whoami)
Group=$(whoami)
WorkingDirectory=/opt/device-maintenance/backend
Environment="PATH=/opt/device-maintenance/backend/venv/bin"
ExecStart=/opt/device-maintenance/backend/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    unified_app:create_unified_app()
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 重载并启动
sudo systemctl daemon-reload
sudo systemctl enable device-maintenance
sudo systemctl start device-maintenance
```

### 4.6 配置 Nginx

```bash
sudo tee /etc/nginx/conf.d/device-maintenance.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        root /opt/device-maintenance/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
        client_max_body_size 16M;
    }

    location /uploads/ {
        alias /opt/device-maintenance/backend/uploads/;
        expires 30d;
    }
}
EOF

# 测试并重载
sudo nginx -t
sudo systemctl reload nginx
```

---

## 五、验证部署

### 5.1 检查服务状态

```bash
# 检查后端服务
sudo systemctl status device-maintenance

# 检查 Nginx
sudo systemctl status nginx

# 查看后端日志
sudo journalctl -u device-maintenance -f
```

### 5.2 访问测试

```bash
# 获取服务器 IP
hostname -I

# 测试 API
curl http://localhost/api/health

# 在浏览器访问
# http://你的服务器IP
```

### 5.3 防火墙配置（如果无法访问）

```bash
# 开放 80 端口
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload

# 或者关闭防火墙（仅测试环境）
sudo systemctl stop firewalld
sudo systemctl disable firewalld
```

---

## 六、常见问题

### Q1: Python 依赖安装失败

```bash
# 龙芯架构可能需要特殊版本的包
# 尝试使用 --no-binary 选项
pip install --no-binary :all: package-name

# 或使用龙芯官方源
pip install -i https://pypi.loongnix.cn/simple/ package-name
```

### Q2: Nginx 502 Bad Gateway

```bash
# 检查后端是否运行
sudo systemctl status device-maintenance

# 检查端口是否监听
netstat -tlnp | grep 5000

# 查看错误日志
sudo tail -f /var/log/nginx/device-maintenance-error.log
```

### Q3: 前端页面空白

```bash
# 检查前端文件是否存在
ls -la /opt/device-maintenance/frontend/

# 检查 index.html 是否存在
cat /opt/device-maintenance/frontend/index.html
```

### Q4: 权限问题

```bash
# 修复目录权限
sudo chown -R $USER:$USER /opt/device-maintenance
sudo chmod -R 755 /opt/device-maintenance/backend/uploads
```

---

## 七、服务管理命令

```bash
# 启动服务
sudo systemctl start device-maintenance
sudo systemctl start nginx

# 停止服务
sudo systemctl stop device-maintenance

# 重启服务
sudo systemctl restart device-maintenance

# 查看状态
sudo systemctl status device-maintenance

# 查看实时日志
sudo journalctl -u device-maintenance -f

# 开机自启
sudo systemctl enable device-maintenance
```

---

## 八、更新部署

当需要更新代码时：

```bash
# 1. 停止服务
sudo systemctl stop device-maintenance

# 2. 更新后端代码
cp -r server/backend/* /opt/device-maintenance/backend/

# 3. 更新前端代码（需要先在开发机编译）
cp -r frontend/dist/build/h5/* /opt/device-maintenance/frontend/

# 4. 更新依赖（如有新增）
cd /opt/device-maintenance/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 5. 重启服务
sudo systemctl start device-maintenance
sudo systemctl reload nginx
```

---

## 九、证明材料准备

为证明软件部署在 LoongArch + 银河麒麟环境，建议准备：

1. **系统信息截图**：
   ```bash
   # 执行以下命令并截图
   uname -a                    # 显示系统架构
   cat /etc/os-release         # 显示操作系统信息
   lscpu                       # 显示 CPU 信息
   free -h                     # 显示内存信息
   df -h                       # 显示磁盘信息
   ```

2. **服务运行截图**：
   ```bash
   systemctl status device-maintenance
   systemctl status nginx
   ```

3. **访问截图**：
   - 浏览器访问首页
   - API 接口测试

4. **部署日志**：保存部署过程的完整日志

---

## 十、技术支持

如遇问题，请检查：
1. `/var/log/nginx/device-maintenance-error.log` - Nginx 错误日志
2. `sudo journalctl -u device-maintenance` - 后端服务日志
3. `/opt/device-maintenance/backend/.env` - 环境变量配置

---

**文档版本**: v1.0
**适用环境**: LoongArch + 银河麒麟高级服务器 V10/V11
