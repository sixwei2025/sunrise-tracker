#!/bin/bash
# 小红书AI爆文检测器 - 启动脚本

echo "🔥 小红书AI爆文检测器"
echo "======================="
echo ""

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "   请先安装 Python 3.8 或更高版本"
    exit 1
fi

# 检查依赖是否安装
if [ ! -d "venv" ]; then
    echo "📦 首次运行，正在创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 安装依赖..."
    pip install -r requirements.txt
    echo ""
fi

# 激活虚拟环境
source venv/bin/activate

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 配置文件"
    echo "   正在复制模板..."
    cp .env.example .env
    echo "   ✓ 已创建 .env 文件"
    echo ""
    echo "📝 请编辑 .env 文件，配置你的API密钥和通知方式："
    echo "   nano .env"
    echo ""
    exit 0
fi

# 选择运行模式
echo "请选择运行模式:"
echo "1) 单次执行（测试）"
echo "2) 定时执行（每天7点自动运行）"
echo ""
read -p "请输入选项 [1/2]: " choice

case $choice in
    1)
        echo ""
        echo "🏃 单次执行模式..."
        echo ""
        cd src && python main.py
        ;;
    2)
        echo ""
        echo "⏰ 定时执行模式..."
        echo "   程序将在每天7点自动执行"
        echo "   按 Ctrl+C 停止"
        echo ""
        cd src && python scheduler.py
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac
