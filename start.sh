#!/bin/bash

# 终止已存在的Flask进程
kill_existing_process() {
    local port=$1
    # 查找使用指定端口的进程
    local pid=$(lsof -ti :$port)
    if [ ! -z "$pid" ]; then
        echo "终止端口 $port 上的现有进程 (PID: $pid)..."
        kill $pid
        sleep 1  # 等待进程完全终止
    fi
}

# 获取端口参数，默认为5000
PORT=${1:-5000}

# 终止现有进程
kill_existing_process $PORT

# 激活虚拟环境
source venv/bin/activate

# 运行应用
python app.py $PORT 