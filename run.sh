#!/bin/bash

# Productivity Bot Starter Script (Linux/Mac)

echo "🤖 Productivity Bot ishga tushmoqda..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 topilmadi! O'rnating: sudo apt install python3"
    exit 1
fi

# Check .env
if [ ! -f .env ]; then
    echo "⚠️  .env fayli topilmadi!"
    echo "📝 .env.example dan nusxa oling va to'ldiring:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Check venv
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment yaratilmoqda..."
    python3 -m venv venv
fi

# Activate venv
echo "🔄 Virtual environment aktivlashtirilmoqda..."
source venv/bin/activate

# Install requirements
echo "📥 Kutubxonalar o'rnatilmoqda..."
pip install -q -r requirements.txt

# Create data directory
mkdir -p data/photos data/charts

# Run bot
echo ""
echo "✅ Tayyor! Bot ishga tushmoqda..."
echo ""
echo "To'xtatish uchun: Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python bot.py
