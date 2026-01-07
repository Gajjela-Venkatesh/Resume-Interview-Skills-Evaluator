@echo off
echo ==========================================
echo      Initializing Git Repository
echo ==========================================

:: Check if git is available
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is strictly NOT found in this terminal.
    echo Please install Git from https://git-scm.com/downloads
    echo and restart your terminal.
    pause
    exit /b
)

echo.
echo 1. Initializing repository...
git init

echo.
echo 2. Adding files...
git add .

echo.
echo 3. Creating initial commit...
git commit -m "Initial commit - Cleaned up project"

echo.
echo ==========================================
echo      Repository Ready!
echo ==========================================
echo.
echo To upload to GitHub:
echo 1. Create a new repository on GitHub.com
echo 2. Copy the URL (e.g., https://github.com/username/repo.git)
echo 3. Run the following commands:
echo.
echo    git remote add origin YOUR_URL_HERE
echo    git branch -M main
echo    git push -u origin main
echo.
pause
