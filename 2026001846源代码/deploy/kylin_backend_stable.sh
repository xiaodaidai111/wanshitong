#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-$HOME/2026001846源代码}"
BACKEND_DIR="$APP_ROOT/server/backend"
SERVICE_NAME="${SERVICE_NAME:-yixiu-backend}"
SERVICE_USER="${SERVICE_USER:-$(id -un)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PORT="${PORT:-5000}"

echo "== 一修后端稳定部署 =="
echo "项目目录: $APP_ROOT"
echo "后端目录: $BACKEND_DIR"
echo "运行用户: $SERVICE_USER"
echo "端口: $PORT"

if [ ! -d "$BACKEND_DIR" ]; then
  echo "后端目录不存在: $BACKEND_DIR"
  echo "请先把项目源代码放到 APP_ROOT，或这样指定目录："
  echo "APP_ROOT=/实际项目目录 bash deploy/kylin_backend_stable.sh"
  exit 1
fi

cd "$BACKEND_DIR"

echo "== 系统信息 =="
uname -a || true
$PYTHON_BIN --version

echo "== 停止占用 $PORT 的旧进程 =="
if command -v ss >/dev/null 2>&1; then
  ss -lntp | grep ":$PORT " || true
fi
if command -v fuser >/dev/null 2>&1; then
  sudo fuser -k "${PORT}/tcp" || true
fi

echo "== 检查数据库服务 =="
if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl enable --now mariadb 2>/dev/null || sudo systemctl enable --now mysql 2>/dev/null || true
  sudo systemctl status mariadb --no-pager 2>/dev/null | head -20 || sudo systemctl status mysql --no-pager 2>/dev/null | head -20 || true
fi

echo "== 创建 Python 虚拟环境 =="
if [ ! -d ".venv" ]; then
  $PYTHON_BIN -m venv .venv
fi
. .venv/bin/activate

echo "== 安装基础依赖 =="
python -m pip install -U pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple

cat > /tmp/yixiu_requirements_runtime.txt <<'REQ'
flask
flask-cors
python-dotenv
pydantic
langchain-openai
langchain-core
bcrypt
PyJWT
PyMySQL
werkzeug
requests
numpy
dashscope
httpx
DBUtils
cryptography
lightrag-hku
openai
tiktoken
REQ

python -m pip install -r /tmp/yixiu_requirements_runtime.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "== 检查 .env =="
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "已从 .env.example 创建 .env，请马上填写数据库和千问配置后再运行本脚本。"
    exit 1
  fi
  echo "缺少 .env，请创建 $BACKEND_DIR/.env"
  exit 1
fi

echo "== 检查数据库连接 =="
PYTHONPATH="$APP_ROOT/server" python - <<'PY'
from backend.utils import get_db_connection

tables = [
    "users", "guest_sessions", "equipment", "maintenance_records",
    "knowledge_base", "health_records", "takeaway_analysis"
]

with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT DATABASE() AS db")
    print("数据库连接正常")
    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
            print(f"{table}: OK")
        except Exception as exc:
            print(f"{table}: 缺失或异常: {exc}")
PY

echo "== 写入 systemd 服务 =="
sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" >/dev/null <<EOF
[Unit]
Description=Yixiu Unified Backend
After=network.target mariadb.service mysql.service

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${BACKEND_DIR}
Environment=PYTHONPATH=${APP_ROOT}/server
ExecStart=${BACKEND_DIR}/.venv/bin/python ${BACKEND_DIR}/unified_app.py
Restart=always
RestartSec=3
KillSignal=SIGINT
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
EOF

echo "== 启动服务 =="
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"
sleep 3
sudo systemctl status "$SERVICE_NAME" --no-pager | head -40 || true

echo "== 放开防火墙端口 =="
if command -v firewall-cmd >/dev/null 2>&1; then
  sudo firewall-cmd --add-port="${PORT}/tcp" --permanent || true
  sudo firewall-cmd --reload || true
fi

echo "== 验证 HTTP =="
curl -fsS "http://127.0.0.1:${PORT}/api/system/health"
echo
echo "== 完成 =="
echo "本机健康检查: http://127.0.0.1:${PORT}/api/system/health"
echo "外部访问检查: http://$(hostname -I | awk '{print $1}'):${PORT}/api/system/health"
