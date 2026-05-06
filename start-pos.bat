@echo off
cd /d %~dp0

echo Stopping existing services...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do taskkill /PID %%a /F >nul 2>&1

echo Starting backend...
start "" /b cmd /c "cd backend && .\venv\Scripts\activate && py -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

timeout /t 5

echo Starting frontend...
start "" /b cmd /c "cd frontend && npm run dev"

timeout /t 5 > nul

echo Opening app...
start chrome --app=http://localhost:5173 --start-maximized


:loop
timeout /t 2 > nul
tasklist | find /i "chrome.exe" > nul
if errorlevel 1 (
    echo Browser closed. Shutting down services...
    echo Closing frontend...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do taskkill /PID %%a /F
    
    timeout /t 2 > nul
    echo Closing backend...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /PID %%a /F
    exit
)
echo Browser is still running...
goto loop

exit