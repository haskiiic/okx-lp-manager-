#!/bin/bash

# OKX钱包LP管理系统启动脚本
# 自动检查环境、配置依赖并启动服务

set -e

echo "🚀 OKX钱包LP管理系统启动脚本"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Python版本
check_python() {
    echo -e "${BLUE}检查Python版本...${NC}"
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3未安装，请先安装Python 3.8+${NC}"
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo -e "${GREEN}✅ Python版本: $python_version${NC}"
    
    if [[ $(echo "$python_version 3.8" | tr ' ' '\n' | sort -V | head -1) != "3.8" ]]; then
        echo -e "${RED}❌ Python版本必须是3.8或更高${NC}"
        exit 1
    fi
}

# 检查并创建虚拟环境
setup_virtualenv() {
    echo -e "${BLUE}设置虚拟环境...${NC}"
    
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}创建虚拟环境...${NC}"
        python3 -m venv .venv
    fi
    
    echo -e "${GREEN}✅ 激活虚拟环境${NC}"
    source .venv/bin/activate
}

# 安装依赖
install_dependencies() {
    echo -e "${BLUE}安装Python依赖...${NC}"
    
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✅ 依赖安装完成${NC}"
    else
        echo -e "${RED}❌ requirements.txt文件不存在${NC}"
        exit 1
    fi
}

# 检查配置文件
check_config() {
    echo -e "${BLUE}检查配置文件...${NC}"
    
    if [ ! -f ".env" ]; then
        if [ -f "config.env.example" ]; then
            echo -e "${YELLOW}⚠️  .env文件不存在，从示例文件复制...${NC}"
            cp config.env.example .env
            echo -e "${YELLOW}⚠️  请编辑.env文件并配置你的OKX API密钥${NC}"
        else
            echo -e "${RED}❌ 配置文件不存在${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ 配置文件存在${NC}"
}

# 检查数据库连接
check_database() {
    echo -e "${BLUE}检查数据库连接...${NC}"
    
    # 这里可以添加数据库连接检查逻辑
    # 暂时跳过，因为可能使用Docker
    echo -e "${YELLOW}⚠️  请确保PostgreSQL和Redis服务已启动${NC}"
}

# 创建必要目录
create_directories() {
    echo -e "${BLUE}创建必要目录...${NC}"
    
    mkdir -p logs
    mkdir -p data
    
    echo -e "${GREEN}✅ 目录创建完成${NC}"
}

# 启动服务
start_service() {
    echo -e "${BLUE}启动OKX LP管理服务...${NC}"
    echo -e "${GREEN}🌐 服务将在 http://localhost:8000 启动${NC}"
    echo -e "${GREEN}📖 API文档: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}📝 ReDoc文档: http://localhost:8000/redoc${NC}"
    echo ""
    echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
    echo ""
    
    python main.py
}

# Docker启动选项
start_with_docker() {
    echo -e "${BLUE}使用Docker启动服务...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker未安装${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose未安装${NC}"
        exit 1
    fi
    
    # 检查.env文件
    if [ ! -f ".env" ]; then
        if [ -f "config.env.example" ]; then
            cp config.env.example .env
            echo -e "${YELLOW}⚠️  请编辑.env文件并配置你的OKX API密钥${NC}"
            echo -e "${YELLOW}⚠️  配置完成后重新运行: $0 --docker${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}🐳 启动Docker服务...${NC}"
    docker-compose up --build
}

# 显示帮助信息
show_help() {
    echo "OKX钱包LP管理系统启动脚本"
    echo ""
    echo "用法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示帮助信息"
    echo "  --docker, -d   使用Docker启动"
    echo "  --check, -c    仅检查环境，不启动服务"
    echo ""
    echo "示例:"
    echo "  $0              # 正常启动"
    echo "  $0 --docker     # 使用Docker启动"
    echo "  $0 --check      # 检查环境"
}

# 主函数
main() {
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --docker|-d)
            start_with_docker
            exit 0
            ;;
        --check|-c)
            check_python
            check_config
            check_database
            echo -e "${GREEN}✅ 环境检查完成${NC}"
            exit 0
            ;;
        "")
            # 正常启动流程
            check_python
            setup_virtualenv
            install_dependencies
            check_config
            create_directories
            check_database
            start_service
            ;;
        *)
            echo -e "${RED}❌ 未知选项: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 捕获中断信号
trap 'echo -e "\n${YELLOW}👋 服务已停止${NC}"; exit 0' INT TERM

# 执行主函数
main "$@" 