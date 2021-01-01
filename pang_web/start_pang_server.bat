@echo off
title %~nx0
call init_python.bat

set "PYTHONPATH=%CD%\.."
echo Using PYTHONPATH=%PYTHONPATH%

echo Starting server...
%venv_path%\scripts\python pang_server_main.py %*
