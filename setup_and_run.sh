#!/bin/bash
# 隐私政策分析器 - 快速安装和运行脚本

echo "=========================================="
echo "隐私政策分析器 - 自动安装脚本"
echo "=========================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

echo "✓ Python已安装: $(python3 --version)"
echo ""

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    echo "✓ 虚拟环境创建完成"
else
    echo "✓ 虚拟环境已存在"
fi
echo ""

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate
echo ""

# 升级pip
echo "📦 升级pip..."
pip install --upgrade pip -q
echo "✓ pip升级完成"
echo ""

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements.txt -q
echo "✓ 依赖包安装完成"
echo ""

# 下载spaCy模型
echo "📦 下载spaCy英文模型（en_core_web_sm）..."
python -m spacy download en_core_web_sm
echo "✓ spaCy模型下载完成"
echo ""

echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo ""
echo "现在你可以运行以下命令进行测试："
echo ""
echo "  # 1. 激活虚拟环境："
echo "     source venv/bin/activate"
echo ""
echo "  # 2. 运行演示："
echo "     python demo_nlp_vs_simple.py"
echo ""
echo "  # 3. 分析隐私政策："
echo "     python analyze_policy.py example_privacy_policy.txt"
echo ""
echo "  # 4. 退出虚拟环境："
echo "     deactivate"
echo ""

