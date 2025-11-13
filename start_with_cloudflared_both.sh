#!/bin/bash

# Privacy Policy Analyzer - 使用两个 cloudflared 隧道
# 一个用于后端，一个用于前端

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}使用两个 cloudflared 隧道${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 cloudflared 是否安装
if ! command -v cloudflared &> /dev/null; then
    echo -e "${RED}错误: 未找到 cloudflared${NC}"
    echo -e "${YELLOW}请安装: ${GREEN}brew install cloudflared${NC}"
    exit 1
fi

# 检查并启动后端
echo -e "${BLUE}检查后端服务...${NC}"
BACKEND_PID=""
BACKEND_NEEDS_START=false

if ! curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo -e "${YELLOW}后端服务未运行，正在启动...${NC}"
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo -e "${RED}错误: 未找到虚拟环境 venv${NC}"
        exit 1
    fi
    
    # 启动后端
    source venv/bin/activate
    python run_api.py > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    BACKEND_NEEDS_START=true
    
    # 等待后端启动
    echo -e "${BLUE}等待后端启动...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 后端已启动 (PID: $BACKEND_PID)${NC}"
            break
        fi
        sleep 1
    done
    
    if ! curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
        echo -e "${RED}错误: 后端启动失败${NC}"
        echo -e "${YELLOW}查看日志: ${GREEN}tail -f /tmp/backend.log${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
else
    echo -e "${GREEN}✓ 后端服务运行正常${NC}"
    # 尝试获取后端进程 ID
    BACKEND_PID=$(lsof -ti:5001 | head -1)
fi

# 检查前端是否运行
echo -e "${BLUE}检查前端服务...${NC}"
FRONTEND_PID=""
FRONTEND_NEEDS_START=false

if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    FRONTEND_NEEDS_START=true
    echo -e "${YELLOW}前端服务未运行，将在配置好 API 地址后启动${NC}"
else
    echo -e "${GREEN}✓ 前端服务运行正常${NC}"
    # 尝试获取前端进程 ID（用于重启）
    FRONTEND_PID=$(lsof -ti:3000 | head -1)
fi

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}正在关闭服务...${NC}"
    kill $BACKEND_TUNNEL_PID $FRONTEND_TUNNEL_PID 2>/dev/null || true
    # 只关闭我们启动的进程
    if [ "$BACKEND_NEEDS_START" = true ] && [ ! -z "$BACKEND_PID" ]; then
        echo -e "${YELLOW}关闭后端服务 (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "${YELLOW}关闭前端服务 (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# 启动后端 cloudflared
echo ""
echo -e "${BLUE}启动 cloudflared 代理后端 (端口 5001)...${NC}"

cloudflared tunnel --url http://localhost:5001 > /tmp/cloudflared_backend.log 2>&1 &
BACKEND_TUNNEL_PID=$!

sleep 6

# 获取后端 cloudflared 地址
BACKEND_URL=$(grep -oE 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' /tmp/cloudflared_backend.log 2>/dev/null | head -1)

if [ -z "$BACKEND_URL" ]; then
    # 尝试其他格式
    BACKEND_URL=$(grep -o 'https://[^ ]*' /tmp/cloudflared_backend.log | grep -i cloudflare | head -1)
fi

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}错误: 无法获取后端 cloudflared 地址${NC}"
    echo -e "${YELLOW}请查看日志:${NC}"
    tail -20 /tmp/cloudflared_backend.log
    kill $BACKEND_TUNNEL_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✓ 后端 cloudflared 已启动 (PID: $BACKEND_TUNNEL_PID)${NC}"
echo -e "   后端公网地址: ${GREEN}${BACKEND_URL}${NC}"

# 配置前端使用后端地址（在启动前端之前）
echo ""
echo -e "${BLUE}配置前端使用后端地址...${NC}"
echo "REACT_APP_API_URL=${BACKEND_URL}/api" > frontend/.env
echo "DANGEROUSLY_DISABLE_HOST_CHECK=true" >> frontend/.env
echo -e "${GREEN}✓ 已配置 frontend/.env${NC}"
echo -e "   API 地址: ${GREEN}${BACKEND_URL}/api${NC}"

# 启动或重启前端（在启动 cloudflared 之前）
echo ""
if [ "$FRONTEND_NEEDS_START" = true ]; then
    echo -e "${BLUE}启动前端服务...${NC}"
    cd frontend
    BROWSER=none DANGEROUSLY_DISABLE_HOST_CHECK=true npm start > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # 等待前端启动
    echo -e "${BLUE}等待前端启动...${NC}"
    for i in {1..60}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 前端已启动 (PID: $FRONTEND_PID)${NC}"
            break
        fi
        sleep 1
    done
    
    if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${YELLOW}警告: 前端启动较慢，请稍后检查${NC}"
        echo -e "${YELLOW}查看日志: ${GREEN}tail -f /tmp/frontend.log${NC}"
    fi
else
    # 前端已经在运行，需要重启
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "${BLUE}重启前端以使用新的 API 地址...${NC}"
        echo -e "${YELLOW}正在停止旧的前端进程 (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
        sleep 2
        
        echo -e "${BLUE}启动新的前端进程...${NC}"
        cd frontend
        BROWSER=none DANGEROUSLY_DISABLE_HOST_CHECK=true npm start > /tmp/frontend.log 2>&1 &
        FRONTEND_PID=$!
        cd ..
        
        # 等待前端启动
        echo -e "${BLUE}等待前端启动...${NC}"
        for i in {1..60}; do
            if curl -s http://localhost:3000 > /dev/null 2>&1; then
                echo -e "${GREEN}✓ 前端已重启 (PID: $FRONTEND_PID)${NC}"
                break
            fi
            sleep 1
        done
    else
        echo -e "${YELLOW}⚠️  前端正在运行，但无法自动重启${NC}"
        echo -e "${YELLOW}   请手动停止前端（Ctrl+C），然后运行:${NC}"
        echo -e "   ${GREEN}cd frontend && npm start${NC}"
    fi
fi

# 启动前端 cloudflared（在前端启动后）
echo ""
echo -e "${BLUE}启动 cloudflared 代理前端 (端口 3000)...${NC}"

cloudflared tunnel --url http://localhost:3000 > /tmp/cloudflared_frontend.log 2>&1 &
FRONTEND_TUNNEL_PID=$!

sleep 6

# 获取前端 cloudflared 地址
FRONTEND_URL=$(grep -oE 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' /tmp/cloudflared_frontend.log 2>/dev/null | head -1)

if [ -z "$FRONTEND_URL" ]; then
    # 尝试其他格式
    FRONTEND_URL=$(grep -o 'https://[^ ]*' /tmp/cloudflared_frontend.log | grep -i cloudflare | head -1)
fi

if [ -z "$FRONTEND_URL" ]; then
    echo -e "${YELLOW}警告: 无法获取前端 cloudflared 地址${NC}"
    echo -e "${YELLOW}请查看日志:${NC}"
    tail -20 /tmp/cloudflared_frontend.log
else
    echo -e "${GREEN}✓ 前端 cloudflared 已启动 (PID: $FRONTEND_TUNNEL_PID)${NC}"
    echo -e "   前端公网地址: ${GREEN}${FRONTEND_URL}${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ 所有服务已启动！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "公网前端地址: ${GREEN}${FRONTEND_URL:-未获取}${NC}"
echo -e "公网后端地址: ${GREEN}${BACKEND_URL}${NC}"
echo ""
echo -e "${GREEN}✓ 前端已配置并启动，使用公网后端地址${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有 cloudflared 隧道${NC}"
echo ""
echo -e "${BLUE}提示: 查看日志可以使用以下命令:${NC}"
echo -e "  后端日志: ${GREEN}tail -f /tmp/cloudflared_backend.log${NC}"
echo -e "  前端日志: ${GREEN}tail -f /tmp/cloudflared_frontend.log${NC}"
echo ""

# 等待进程
wait $BACKEND_TUNNEL_PID $FRONTEND_TUNNEL_PID 2>/dev/null || true

