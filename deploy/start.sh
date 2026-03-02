#!/bin/bash
# PineVC-PR 启动脚本
# 用法: ./start.sh [命令]
#
# 命令:
#   start     - 启动所有服务
#   stop      - 停止所有服务
#   restart   - 重启所有服务
#   status    - 查看服务状态
#   logs      - 查看日志
#   down      - 停止并删除容器
#   reset     - 完全重置 (包括数据)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 .env 文件
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}未找到 .env 文件，正在创建...${NC}"
        cp .env.example .env 2>/dev/null || echo -e "${RED}请手动创建 .env 文件${NC}"
        echo -e "${GREEN}.env 文件已创建，请编辑并填入必要的 API Key${NC}"
    fi
}

# 检查 Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker 未安装${NC}"
        echo "请先安装 Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}错误: Docker Compose 未安装${NC}"
        exit 1
    fi
}

# 获取 docker compose 命令
get_compose_cmd() {
    if docker compose version &> /dev/null 2>&1; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

COMPOSE_CMD=$(get_compose_cmd)

# 启动服务
start() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  PineVC-PR 启动中...${NC}"
    echo -e "${BLUE}============================================${NC}"

    check_env
    check_docker

    $COMPOSE_CMD up -d

    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  服务启动成功!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "访问地址:"
    echo -e "  ${YELLOW}Dify Web:${NC}   http://localhost:3000"
    echo -e "  ${YELLOW}Dify API:${NC}   http://localhost:5001"
    echo -e "  ${YELLOW}n8n:${NC}        http://localhost:5678"
    echo -e "  ${YELLOW}Weaviate:${NC}   http://localhost:8080"
    echo ""
    echo -e "首次使用请在 Dify 中设置管理员账号"
    echo ""
}

# 停止服务
stop() {
    echo -e "${YELLOW}停止所有服务...${NC}"
    $COMPOSE_CMD stop
    echo -e "${GREEN}服务已停止${NC}"
}

# 重启服务
restart() {
    echo -e "${YELLOW}重启所有服务...${NC}"
    $COMPOSE_CMD restart
    echo -e "${GREEN}服务已重启${NC}"
}

# 查看状态
status() {
    echo -e "${BLUE}服务状态:${NC}"
    $COMPOSE_CMD ps
}

# 查看日志
logs() {
    local service=$1
    if [ -z "$service" ]; then
        $COMPOSE_CMD logs -f --tail=100
    else
        $COMPOSE_CMD logs -f --tail=100 "$service"
    fi
}

# 停止并删除容器
down() {
    echo -e "${YELLOW}停止并删除容器 (保留数据)...${NC}"
    $COMPOSE_CMD down
    echo -e "${GREEN}容器已删除，数据卷保留${NC}"
}

# 完全重置
reset() {
    echo -e "${RED}警告: 这将删除所有数据!${NC}"
    read -p "确定要继续吗? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        $COMPOSE_CMD down -v
        echo -e "${GREEN}已完全重置${NC}"
    else
        echo -e "${YELLOW}已取消${NC}"
    fi
}

# 主命令
case "${1:-start}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    down)
        down
        ;;
    reset)
        reset
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs|down|reset}"
        exit 1
        ;;
esac
