#!/bin/sh
export PATH=/usr/local/bin:$PATH

export venv_path=../../pang_game.venv

if [ ! -d $venv_path ]
then
	/usr/local/bin/python -m venv $venv_path
fi

echo Checking pip...
$venv_path/bin/python -m pip install --upgrade pip

echo Checking dependencies...
$venv_path/bin/pip install -r ../requirements.txt

