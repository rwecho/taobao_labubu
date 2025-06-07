@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🎭 淘宝直播间LABUBU商品搜索程序启动器
echo ================================================

:: 检查Python是否已安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if !errorlevel! == 0 (
    echo ✅ Python已安装
    python --version
    goto :check_pip
) else (
    echo ❌ 未检测到Python
    goto :install_python
)

:install_python
echo 📥 正在自动安装Python...
echo 这可能需要几分钟时间，请耐心等待...

:: 创建临时目录
if not exist "temp" mkdir temp

:: 下载Python安装程序
echo 🌐 正在下载Python 3.11.7...
powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe', 'temp\python-installer.exe')"

if !errorlevel! neq 0 (
    echo ❌ Python下载失败，请检查网络连接
    echo 💡 您也可以手动下载Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 静默安装Python
echo 🔧 正在安装Python...
temp\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

if !errorlevel! neq 0 (
    echo ❌ Python安装失败
    pause
    exit /b 1
)

:: 刷新环境变量
echo 🔄 刷新环境变量...
call refreshenv >nul 2>&1

:: 重新检查Python
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ⚠️ Python安装完成，但可能需要重启命令行
    echo 请关闭此窗口，重新打开命令行后再次运行此脚本
    pause
    exit /b 1
)

echo ✅ Python安装成功！
python --version

:: 清理临时文件
if exist "temp\python-installer.exe" del "temp\python-installer.exe"
if exist "temp" rmdir "temp"

:check_pip
:: 检查pip是否可用
echo 🔍 检查pip环境...
python -m pip --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ pip不可用，尝试安装...
    python -m ensurepip --upgrade
)

:: 创建pip升级标记文件
set PIP_UPGRADED_FLAG=.pip_upgraded

:: 检查是否已经升级过pip
if exist "%PIP_UPGRADED_FLAG%" (
    echo ✅ pip已升级，跳过升级步骤
    goto :check_requirements
)

:: 升级pip
echo 📦 升级pip到最新版本...
python -m pip install --upgrade pip

if !errorlevel! == 0 (
    echo pip upgraded successfully > "%PIP_UPGRADED_FLAG%"
    echo ✅ pip升级完成，已创建标记文件
) else (
    echo ⚠️ pip升级失败，但不影响程序运行
)

:check_requirements
:: 检查依赖安装状态
echo 🔍 检查项目依赖状态...

if not exist "requirements.txt" (
    echo ❌ 未找到requirements.txt文件
    echo 请确保在正确的项目目录中运行此脚本
    pause
    exit /b 1
)

:: 创建依赖安装标记文件
set DEPS_INSTALLED_FLAG=.deps_installed

:: 检查是否已经安装过依赖
if exist "%DEPS_INSTALLED_FLAG%" (
    echo ✅ 依赖已安装，跳过安装步骤
    goto :verify_dependencies
)

:install_requirements
:: 首次安装依赖
echo 📦 首次安装项目依赖...
python -m pip install -r requirements.txt

if !errorlevel! neq 0 (
    echo ❌ 依赖安装失败
    echo 💡 尝试使用国内镜像源...
    python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    
    if !errorlevel! neq 0 (
        echo ❌ 依赖安装仍然失败，请检查网络连接
        pause
        exit /b 1
    )
)

:: 创建安装完成标记文件
echo Dependencies installed successfully > "%DEPS_INSTALLED_FLAG%"
echo ✅ 依赖安装完成，已创建标记文件

:verify_dependencies
:: 验证关键依赖是否正确安装
echo 🔍 验证关键依赖...

python -c "import playwright" >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Playwright未正确安装，重新安装依赖...
    if exist "%DEPS_INSTALLED_FLAG%" del "%DEPS_INSTALLED_FLAG%"
    goto :install_requirements
)

python -c "import yaml" >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ PyYAML未正确安装，重新安装依赖...
    if exist "%DEPS_INSTALLED_FLAG%" del "%DEPS_INSTALLED_FLAG%"
    goto :install_requirements
)

python -c "import pyttsx3" >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ pyttsx3未正确安装，重新安装依赖...
    if exist "%DEPS_INSTALLED_FLAG%" del "%DEPS_INSTALLED_FLAG%"
    goto :install_requirements
)

echo ✅ 所有依赖验证通过

:install_playwright
:: 检查Playwright浏览器是否需要安装
echo 🔍 检查Playwright浏览器...

:: 创建浏览器安装标记文件
set BROWSER_INSTALLED_FLAG=.browser_installed

if exist "%BROWSER_INSTALLED_FLAG%" (
    echo ✅ Playwright浏览器已安装，跳过安装步骤
    goto :check_config
)

echo 🎭 安装Playwright浏览器...
python -m playwright install chromium

if !errorlevel! == 0 (
    echo Playwright browser installed successfully > "%BROWSER_INSTALLED_FLAG%"
    echo ✅ Playwright浏览器安装完成
) else (
    echo ⚠️ Playwright浏览器安装失败，程序会在运行时自动尝试安装
)

:check_config
:: 检查配置文件
echo 🔍 检查配置文件...
if not exist "config.yaml" (
    echo ❌ 未找到config.yaml配置文件
    echo 请确保配置文件存在
    pause
    exit /b 1
)

echo ✅ 配置文件检查完成

:run_program
:: 运行主程序
echo ================================================
echo 🚀 启动LABUBU商品搜索程序...
echo ================================================
echo.

python main.py

:: 程序结束后的处理
echo.
echo ================================================
echo 🏁 程序已结束
echo ================================================

:end
echo.
echo 按任意键退出...
pause >nul
exit /b 0