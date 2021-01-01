@echo off
call init_python.bat

set "PYTHONPATH=%CD%\.."
echo Using PYTHONPATH=%PYTHONPATH%

echo Starting db_init...
%venv_path%\scripts\python db_init.py %*
