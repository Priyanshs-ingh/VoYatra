@echo off
echo VoYatra Flight Search
echo ====================

echo Choose your option:
echo 1. Test Mode (No dependencies needed)
echo 2. Full Scrapy Mode (Requires Scrapy installation)
echo.

set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Running Test Mode...
    echo.
    python test_flight_search.py
) else if "%choice%"=="2" (
    echo.
    echo Running Full Scrapy Mode...
    echo.
    cd /d "%~dp0"
    python search_flights.py
) else (
    echo Invalid choice. Running Test Mode by default...
    echo.
    python test_flight_search.py
)

pause
