@echo off
chcp 65001
cd /d "%~dp0"

echo ==============================================
echo        AetherSwap 全自动部署脚本（Python3.10）
echo ==============================================

echo.
echo [1/4] 正在安装 pythonnet（解决编译报错）...
python -m pip install pythonnet --only-binary=:all: -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [2/4] 正在安装全部依赖...
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo [3/4] 正在安装浏览器内核...
python -m playwright install chromium

echo.
echo [4/4] 启动程序...
python run.py

echo.
echo 运行结束
pause