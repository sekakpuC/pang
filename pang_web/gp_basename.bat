@echo off
setlocal enabledelayedexpansion
set PARENT_PATH=%CD%
for %%f in ("!PARENT_PATH!") do set PARENT_BASENAME=%%~nf
set GRANDPARENT_PATH=!CD:\%PARENT_BASENAME%=!
for %%f in ("!GRANDPARENT_PATH!") do set GRANDPARENT_BASENAME=%%~nf
REM echo !PARENT_PATH!
REM echo !PARENT_BASENAME!
REM echo !GRANDPARENT_PATH!
echo !GRANDPARENT_BASENAME!
