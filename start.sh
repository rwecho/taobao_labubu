#!/bin/bash

# 设置UTF-8编码
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

echo "🎭 淘宝直播间LABUBU商品搜索程序启动器"
echo "================================================"

# 检测操作系统
OS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "📱 检测到操作系统: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "🍎 检测到操作系统: macOS"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    echo "💡 此脚本仅支持Linux和macOS"
    exit 1
fi

# 检查Python是否已安装
echo "🔍 检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Python3已安装"
    python3 --version
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
        echo "✅ Python已安装"
        python --version
    else
        echo "❌ 检测到Python 2，需要Python 3"
        install_python
    fi
else
    echo "❌ 未检测到Python"
    install_python
fi

install_python() {
    echo "📥 正在自动安装Python..."
    
    if [[ "$OS" == "macos" ]]; then
        # macOS - 检查是否有Homebrew
        if command -v brew &> /dev/null; then
            echo "🍺 使用Homebrew安装Python..."
            brew install python3
            if [[ $? -eq 0 ]]; then
                PYTHON_CMD="python3"
                echo "✅ Python安装成功！"
            else
                echo "❌ Python安装失败"
                echo "💡 请手动安装Python: https://www.python.org/downloads/"
                exit 1
            fi
        else
            echo "❌ 未找到Homebrew包管理器"
            echo "💡 请先安装Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "💡 或手动安装Python: https://www.python.org/downloads/"
            exit 1
        fi
    elif [[ "$OS" == "linux" ]]; then
        # Linux - 尝试不同的包管理器
        if command -v apt &> /dev/null; then
            echo "🐧 使用apt安装Python..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            echo "🐧 使用yum安装Python..."
            sudo yum install -y python3 python3-pip
        elif command -v dnf &> /dev/null; then
            echo "🐧 使用dnf安装Python..."
            sudo dnf install -y python3 python3-pip
        elif command -v pacman &> /dev/null; then
            echo "🐧 使用pacman安装Python..."
            sudo pacman -S python python-pip
        else
            echo "❌ 未找到支持的包管理器"
            echo "💡 请手动安装Python3和pip"
            exit 1
        fi
        
        if command -v python3 &> /dev/null; then
            PYTHON_CMD="python3"
            echo "✅ Python安装成功！"
        else
            echo "❌ Python安装失败"
            exit 1
        fi
    fi
}

# 检查pip是否可用
echo "🔍 检查pip环境..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "❌ pip不可用，尝试安装..."
    if [[ "$OS" == "macos" ]]; then
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $PYTHON_CMD get-pip.py
        rm get-pip.py
    elif [[ "$OS" == "linux" ]]; then
        $PYTHON_CMD -m ensurepip --upgrade
    fi
fi

# 创建pip升级标记文件
PIP_UPGRADED_FLAG=".pip_upgraded"

# 检查是否已经升级过pip
if [[ -f "$PIP_UPGRADED_FLAG" ]]; then
    echo "✅ pip已升级，跳过升级步骤"
else
    # 升级pip
    echo "📦 升级pip到最新版本..."
    $PYTHON_CMD -m pip install --upgrade pip
    
    if [[ $? -eq 0 ]]; then
        echo "pip upgraded successfully" > "$PIP_UPGRADED_FLAG"
        echo "✅ pip升级完成，已创建标记文件"
    else
        echo "⚠️ pip升级失败，但不影响程序运行"
    fi
fi

# 检查依赖安装状态
echo "🔍 检查项目依赖状态..."

if [[ ! -f "requirements.txt" ]]; then
    echo "❌ 未找到requirements.txt文件"
    echo "请确保在正确的项目目录中运行此脚本"
    exit 1
fi

# 创建依赖安装标记文件
DEPS_INSTALLED_FLAG=".deps_installed"

# 检查是否已经安装过依赖
if [[ -f "$DEPS_INSTALLED_FLAG" ]]; then
    echo "✅ 依赖已安装，跳过安装步骤"
else
    # 首次安装依赖
    echo "📦 首次安装项目依赖..."
    $PYTHON_CMD -m pip install -r requirements.txt
    
    if [[ $? -ne 0 ]]; then
        echo "❌ 依赖安装失败"
        echo "💡 尝试使用国内镜像源..."
        $PYTHON_CMD -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
        
        if [[ $? -ne 0 ]]; then
            echo "❌ 依赖安装仍然失败，请检查网络连接"
            exit 1
        fi
    fi
    
    # 创建安装完成标记文件
    echo "Dependencies installed successfully" > "$DEPS_INSTALLED_FLAG"
    echo "✅ 依赖安装完成，已创建标记文件"
fi

# 验证关键依赖是否正确安装
echo "🔍 验证关键依赖..."

verify_dependency() {
    local module=$1
    if ! $PYTHON_CMD -c "import $module" &> /dev/null; then
        echo "❌ $module未正确安装，重新安装依赖..."
        rm -f "$DEPS_INSTALLED_FLAG"
        $PYTHON_CMD -m pip install -r requirements.txt
        if [[ $? -ne 0 ]]; then
            echo "❌ 重新安装依赖失败"
            exit 1
        fi
        echo "Dependencies installed successfully" > "$DEPS_INSTALLED_FLAG"
    fi
}

verify_dependency "playwright"
verify_dependency "yaml"
verify_dependency "pyttsx3"

echo "✅ 所有依赖验证通过"

# 检查Playwright浏览器是否需要安装
echo "🔍 检查Playwright浏览器..."

# 创建浏览器安装标记文件
BROWSER_INSTALLED_FLAG=".browser_installed"

if [[ -f "$BROWSER_INSTALLED_FLAG" ]]; then
    echo "✅ Playwright浏览器已安装，跳过安装步骤"
else
    echo "🎭 安装Playwright浏览器..."
    $PYTHON_CMD -m playwright install chromium
    
    if [[ $? -eq 0 ]]; then
        echo "Playwright browser installed successfully" > "$BROWSER_INSTALLED_FLAG"
        echo "✅ Playwright浏览器安装完成"
    else
        echo "⚠️ Playwright浏览器安装失败，程序会在运行时自动尝试安装"
    fi
fi

# 检查配置文件
echo "🔍 检查配置文件..."
if [[ ! -f "config.yaml" ]]; then
    echo "❌ 未找到config.yaml配置文件"
    echo "请确保配置文件存在"
    exit 1
fi

echo "✅ 配置文件检查完成"

# 运行主程序
echo "================================================"
echo "🚀 启动LABUBU商品搜索程序..."
echo "================================================"
echo

$PYTHON_CMD main.py

# 程序结束后的处理
echo
echo "================================================"
echo "🏁 程序已结束"
echo "================================================"

echo
echo "按回车键退出..."
read