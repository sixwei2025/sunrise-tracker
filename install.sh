#!/bin/bash
# 小红书AI爆文检测器 - 安装脚本

echo "🔥 小红书AI爆文检测器 - 安装向导"
echo "====================================="
echo ""

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "   请先安装 Python 3.8 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python 版本: $PYTHON_VERSION"

# 创建虚拟环境
echo ""
echo "📦 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo ""
echo "📥 安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
echo ""
echo "📁 创建目录结构..."
mkdir -p data
mkdir -p logs

# 复制配置文件
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 复制配置模板..."
    cp .env.example .env
    echo "   ✓ 已创建 .env 文件"
fi

# 使脚本可执行
chmod +x run.sh

echo ""
echo "====================================="
echo "✅ 安装完成！"
echo "====================================="
echo ""
echo "下一步："
echo "1. 配置环境变量:"
echo "   nano .env"
echo ""
echo "2. 编辑配置文件（可选）:"
echo "   nano config/config.yaml"
echo ""
echo "3. 运行程序:"
echo "   ./run.sh"
echo ""
echo "📖 查看完整文档: cat README.md"
echo ""
