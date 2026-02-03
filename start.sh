#!/bin/bash

echo "=========================================="
echo "小学英语智慧试卷平台 - Docker快速启动"
echo "=========================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    echo "安装地址：https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker和Docker Compose已安装"
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p backend/uploads
mkdir -p backend/logs
mkdir -p nginx/ssl
echo "✅ 目录创建完成"
echo ""

# 复制环境变量文件
if [ ! -f .env ]; then
    echo "📋 复制环境变量模板..."
    cp .env.example .env
    echo "✅ 已创建.env文件，请根据需要修改配置"
    echo ""
fi

# 构建并启动服务
echo "🚀 开始构建和启动服务..."
echo "这可能需要几分钟，请耐心等待..."
echo ""

docker-compose up -d --build

echo ""
echo "=========================================="
echo "✅ 服务启动完成！"
echo "=========================================="
echo ""
echo "📊 服务状态："
docker-compose ps
echo ""
echo "🌐 访问地址："
echo "   前端应用：http://localhost"
echo "   后端API：http://localhost:8000"
echo "   API文档：http://localhost:8000/docs"
echo "   数据库：localhost:5432"
echo "   Redis：localhost:6379"
echo ""
echo "📝 查看日志："
echo "   docker-compose logs -f"
echo ""
echo "🛑 停止服务："
echo "   docker-compose down"
echo ""
echo "=========================================="
