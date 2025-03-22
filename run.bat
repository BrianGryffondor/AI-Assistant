@echo off
setlocal
chcp 65001 >nul 
echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到Python环境，请先安装Python 3.7+
    pause
    exit /b 1
)

echo 检查依赖包...
pip show PyQt5 >nul 2>&1
if %errorlevel% neq 0 (
    echo 缺少依赖，请先运行 install.bat
    pause
    exit /b 1
)

echo 启动AI聊天程序...
python app.py
if %errorlevel% neq 0 (
    echo 程序异常退出，代码：%errorlevel%
    pause
    exit /b %errorlevel%
)

endlocal