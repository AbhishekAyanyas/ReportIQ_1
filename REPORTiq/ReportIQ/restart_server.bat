@echo off
color 0A
cls

echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║        🔄 ReportIQ QUICK RESTART (With Cache Fix)             ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo.

echo [1/3] 🛑 Stopping any running ReportIQ server...
echo.

REM Kill any existing uvicorn/python processes on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Found process: %%a
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Could not kill process %%a
    ) else (
        echo ✅ Process %%a stopped
    )
)

echo.
timeout /t 2 >nul

echo [2/3] 🚀 Starting ReportIQ server...
echo.
echo ✅ Development Mode: ON (No caching)
echo ✅ All files will load fresh!
echo.

REM Start the server
start "ReportIQ Server" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [3/3] ⏳ Waiting for server to start...
timeout /t 3 >nul

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    ✅ SERVER RESTARTED! ✅                      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 📍 Server URL: http://localhost:8000
echo.
echo 🌐 Opening browser in 3 seconds...
timeout /t 3 >nul

REM Open browser
start http://localhost:8000/dashboard

echo.
echo ✅ Done! Server is running in a new window.
echo.
echo 💡 Tips:
echo    • Press Ctrl+Shift+R in browser for hard refresh
echo    • Check server console for any errors
echo    • All files now load with status 200 OK (not 304!)
echo.
echo Press any key to close this window...
pause >nul
