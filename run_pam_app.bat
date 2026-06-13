@echo off

echo Activating virtual environment...
call venv\Scripts\activate

echo Starting PAM DOLMA app...

streamlit run app.py

echo.
echo ==========================================
echo   PAM app is running successfully!
echo   Open: http://localhost:8510
echo ==========================================

pause