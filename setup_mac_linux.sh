#!/usr/bin/env bash
# ============================================================
#  Leave & Attendance Management System - macOS/Linux Setup
# ============================================================
set -e

echo "====================================================="
echo "  Leave & Attendance Management System - Setup"
echo "====================================================="

# --- Check Python ---
command -v python3 >/dev/null 2>&1 || { echo "[ERROR] Python3 not found."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "[ERROR] Node.js not found."; exit 1; }
echo "[OK] Pre-requisites found."

cd "$(dirname "$0")"

# ===================== BACKEND =====================
echo ""
echo "[1/5] Setting up backend..."
cd backend

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "[OK] Python packages installed."

if [ ! -f .env ]; then
    cp .env.example .env
    echo "[OK] .env created (SQLite default)."
else
    echo "[OK] .env already present."
fi

echo "Running migrations..."
python manage.py makemigrations --noinput || true
python manage.py migrate
echo "[OK] Database ready."

echo "Seeding demo data..."
python manage.py seed_data
echo "[OK] Demo data seeded."
cd ..

# ===================== FRONTEND =====================
echo ""
echo "[2/5] Setting up frontend..."
cd frontend
npm install
cd ..

echo ""
echo "====================================================="
echo "  SETUP COMPLETE!"
echo "====================================================="
echo ""
echo "  Admin   : admin    / admin12345"
echo "  Manager : manager  / manager12345"
echo "  Employee: john     / employee12345"
echo ""
echo "  Run backend :  cd backend && source venv/bin/activate && python manage.py runserver 8000"
echo "  Run frontend:  cd frontend && npm run dev"
echo ""
