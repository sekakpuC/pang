@echo off
title %~nx0
call init_python.bat

set "PYTHONPATH=%CD%\.."
echo Using PYTHONPATH=%PYTHONPATH%

echo Starting web...
%venv_path%\scripts\python pang_web_main.py %*
