@echo off
REM Competitive Analysis Agent Startup Script for Windows
REM This script helps you set up and run the application easily

echo 🚀 Competitive Analysis Agent Startup Script
echo =============================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python is installed

REM Check if we're in the right directory
if not exist "backend\requirements.txt" (
    echo ❌ Please run this script from the competitive-analysis-agent directory
    pause
    exit /b 1
)

echo ✅ Correct directory detected

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
cd backend
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Create reports directory
if not exist "reports" (
    mkdir reports
    echo ✅ Reports directory created
)

echo.
echo 🎉 Setup complete! Starting the application...
echo.
echo 📍 The application will be available at: http://localhost:8000
echo 🔑 You'll need a Google Gemini API key to use the application
echo 🌐 Get your API key here: https://makersuite.google.com/app/apikey
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the FastAPI server
python main.py

pause
