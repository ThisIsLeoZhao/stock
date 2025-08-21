#!/bin/bash
echo "🚀 启动股票分析环境..."

# 检查是否已经在虚拟环境中
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ 已经在虚拟环境中: $VIRTUAL_ENV"
    echo "💡 当前Python路径: $(which python3)"
    exit 0
fi

# 检查虚拟环境是否存在且完整
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo "📁 发现虚拟环境，正在激活..."
    source ./venv/bin/activate
    
    # 检查是否成功激活
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "✅ 虚拟环境已激活"
        echo "💡 当前Python路径: $(which python3)"
        
        # 检查是否已安装依赖
        if pip show yfinance > /dev/null 2>&1; then
            echo "📦 依赖包已安装完成"
        else
            echo "📦 检测到依赖包未安装，正在安装..."
            if pip install -r requirements.txt --timeout 30; then
                echo "✅ 依赖安装完成！"
            else
                echo "⚠️  依赖安装失败，稍后可手动运行: pip install -r requirements.txt"
            fi
        fi
    else
        echo "❌ 虚拟环境激活失败，重新创建..."
        rm -rf venv
        python3 -m venv venv
        source ./venv/bin/activate
        echo "📥 安装项目依赖..."
        if pip install -r requirements.txt --timeout 30; then
            echo "✅ 环境设置完成！"
        else
            echo "⚠️  依赖安装失败（可能是网络问题），但虚拟环境已创建"
            echo "💡 稍后可以手动运行: pip install -r requirements.txt"
        fi
    fi
else
    echo "❌ 虚拟环境不存在，正在创建..."
    rm -rf venv  # 清理可能存在的不完整目录
    python3 -m venv venv
    source ./venv/bin/activate
    echo "📥 安装项目依赖..."
    if pip install -r requirements.txt --timeout 30; then
        echo "✅ 环境设置完成！"
    else
        echo "⚠️  依赖安装失败（可能是网络问题），但虚拟环境已创建"
        echo "💡 稍后可以手动运行: pip install -r requirements.txt"
    fi
fi

echo ""
echo "🎯 现在你可以运行你的Python脚本了！"
echo "💡 要退出虚拟环境，输入: deactivate"
