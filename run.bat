@echo off
REM Productivity Bot Starter Script (Windows)

echo 🤖 Productivity Bot ishga tushmoqda...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python topilmadi! python.org dan o'rnating
    pause
    exit /b 1
)

REM Check .env
if not exist .env (
    echo ⚠️  .env fayli topilmadi!
    echo 📝 .env.example dan nusxa oling va to'ldiring
    echo    copy .env.example .env
    pause
    exit /b 1
)

REM Check venv
if not exist venv (
    echo 📦 Virtual environment yaratilmoqda...
    python -m venv venv
)

REM Activate venv
echo 🔄 Virtual environment aktivlashtirilmoqda...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Kutubxonalar o'rnatilmoqda...
pip install -q -r requirements.txt

REM Create data directory
if not exist data mkdir data
if not exist data\photos mkdir data\photos
if not exist data\charts mkdir data\charts

REM Run bot
echo.
echo ✅ Tayyor! Bot ishga tushmoqda...
echo.
echo To'xtatish uchun: Ctrl+C
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

python bot.py

pause
