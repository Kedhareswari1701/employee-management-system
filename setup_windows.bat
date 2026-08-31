@echo off
REM ============================================================
REM  Leave & Attendance Management System - Windows Setup Script
REM  Sets up backend (Django) + frontend (React) automatically
REM ============================================================
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo =====================================================
echo   Leave & Attendance Management System - Setup
echo =====================================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ and try again.
    exit /b 1
)
echo [OK] Python found.

REM --- Check Node ---
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Install Node 18+ and try again.
    exit /b 1
)
echo [OK] Node.js found.

echo.
echo Would you like to use SQLite (easy, default) or PostgreSQL?
echo  1) SQLite  (recommended, no setup needed)
echo  2) PostgreSQL
set /p DBCHOICE="Enter choice [1/2]: "

cd /d "%~dp0"

REM ===================== BACKEND =====================
echo.
echo [1/5] Setting up backend...
cd backend

if not exist venv (
    echo   Creating virtual environment...
    python -m venv venv
)

echo   Activating virtual environment and installing packages...
call venv\Scripts\activate.bat

pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python packages.
    exit /b 1
)
echo [OK] Python packages installed.

REM --- Configure .env ---
if not exist .env (
    copy .env.example .env >nul
)

if "%DBCHOICE%"=="2" (
    echo.
    echo Enter PostgreSQL details:
    set /p DBNAME="Database name [leave_management]: "
    set /p DBUSER="Database user [postgres]: "
    set /p DBPASS="Database password: "
    set /p DBHOST="Database host [localhost]: "

    if "!DBNAME!"=="" set DBNAME=leave_management
    if "!DBUSER!"=="" set DBUSER=postgres
    if "!DBHOST!"=="" set DBHOST=localhost

    powershell -Command "(Get-Content .env) -replace '^DB_ENGINE=.*','DB_ENGINE=django.db.backends.postgresql' -replace '^DB_NAME=.*','DB_NAME=!DBNAME!' -replace '^DB_USER=.*','DB_USER=!DBUSER!' -replace '^DB_PASSWORD=.*','DB_PASSWORD=!DBPASS!' -replace '^DB_HOST=.*','DB_HOST=!DBHOST!' | Set-Content .env"
    echo [OK] .env updated for PostgreSQL.
)

echo   Running migrations...
python manage.py makemigrations --noinput >nul 2>&1
python manage.py migrate
if errorlevel 1 (
    echo [ERROR] Migrations failed.
    exit /b 1
)
echo [OK] Database ready.

echo   Seeding demo data (admin, manager, employees, departments, leave types)...
python manage.py seed_data
echo [OK] Demo data seeded.

cd ..

REM ===================== FRONTEND =====================
echo.
echo [2/5] Setting up frontend...
cd frontend
if not exist node_modules (
    echo   Installing npm packages (this may take a minute)...
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed.
        exit /b 1
    )
) else (
    echo   node_modules already present, skipping install.
)
cd ..

echo.
echo =====================================================
echo   SETUP COMPLETE!
echo =====================================================
echo.
echo   Demo credentials (pre-seeded):
echo     Admin   : admin    / admin12345
echo     Manager : manager  / manager12345
echo     Employee: john     / employee12345
echo.
echo   Django Admin Portal : http://127.0.0.1:8000/admin/
echo     (login: admin / admin12345)
echo.

echo Press any key to start the BACKEND server in a new window...
pause >nul
start "LMS Backend" cmd /k "cd /d backend && venv\Scripts\activate.bat && python manage.py runserver 8000"

echo Press any key to start the FRONTEND server in a new window...
pause >nul
start "LMS Frontend" cmd /k "cd /d frontend && npm run dev"

echo.
echo Both servers are starting...
echo   Frontend (React) : http://localhost:3000
echo   Backend  (Django): http://127.0.0.1:8000
echo.
endlocal
