@echo off
setlocal

cd /d "%~dp0"

if exist ".streamlit\secrets.toml" goto run_app

echo Missing .streamlit\secrets.toml
echo.
echo Create it from .streamlit\secrets.toml.example and add your rotated Gemini API key.
echo.
pause
exit /b 1

:run_app
where py >nul 2>nul
if %errorlevel%==0 (
    py -m streamlit run kamote.py
    goto done
)

where python >nul 2>nul
if %errorlevel%==0 (
    python -m streamlit run kamote.py
    goto done
)

echo Python was not found on PATH.
echo Install Python and Streamlit, then try again.

:done
echo.
pause
endlocal
