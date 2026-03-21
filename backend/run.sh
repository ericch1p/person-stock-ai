#!/bin/bash

# A股智能选股系统 - 启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境（如果有）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 安装依赖
echo "检查依赖..."
pip install -r requirements.txt -q

# 启动服务
echo "启动后端服务..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
