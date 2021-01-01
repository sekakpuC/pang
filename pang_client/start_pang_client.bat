@echo off
title %~nx0
call init_python.bat

set "PYTHONPATH=%CD%\.."
echo Using PYTHONPATH=%PYTHONPATH%

echo Starting client...
%venv_path%\scripts\python pang_client_main.py %*
