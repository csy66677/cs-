@echo off
chcp 65001
cd /d "%~dp0"
echo 正在启动 AetherSwap...
python run.py
pause