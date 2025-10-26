@echo off
REM Activate virtual environment and run CueConverter
call .venv\Scripts\activate.bat
python cueconverter.py
pause