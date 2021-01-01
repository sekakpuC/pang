@echo off

set "PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python38;%PATH%"
set "PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python38-32;%PATH%"

for /f "usebackq" %%f in (`gp_basename.bat`) do set grandparent_basename=%%f
set venv_path=..\..\%grandparent_basename%.venv

echo Checking %venv_path%...
if not exist %venv_path% python -m venv %venv_path%
call %venv_path%\scripts\activate

echo Checking pip...
%venv_path%\scripts\python -m pip install --upgrade pip

echo Checking dependencies...
%venv_path%\scripts\pip install -r ..\requirements.txt
