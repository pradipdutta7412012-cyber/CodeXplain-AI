@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo        CodeXplain - Start
echo ========================================
py -3.12 -c "import streamlit" >nul 2>&1
if errorlevel 1 (
  echo Installing required Python packages...
  py -3.12 -m pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo Package installation failed. Make sure Python 3.12 and internet access are available.
    pause
    exit /b 1
  )
)
echo Starting CodeXplain...
py -3.12 -m streamlit run app.py
pause
