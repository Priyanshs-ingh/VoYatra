@echo off
echo 🎯 VoYatra Flight Search Setup
echo ==============================

echo 📦 Installing Python dependencies...
pip install scrapy requests lxml cssselect

echo 📁 Creating data directories...
if not exist "..\data\raw\flights" mkdir "..\data\raw\flights"
if not exist "..\logs\scrapy" mkdir "..\logs\scrapy"

echo ✅ Setup complete!
echo.

echo ✈️  Starting Flight Search...
python search_flights.py

pause
