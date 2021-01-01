#!/bin/sh
# `@echo off

# title %~nx0
# call init_python.bat
source init_python.sh

# set "PYTHONPATH=%CD%\.."
# echo Using PYTHONPATH=%PYTHONPATH%
export PYTHONPATH=`pwd`/..

echo Starting client...
# %venv_path%\scripts\python pang_client_main.py %*
$venv_path/bin/python pang_client_main.py $*

