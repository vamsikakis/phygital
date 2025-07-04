@echo off
echo 🔍 Firefly III Status Checker
echo ============================

echo.
echo 📋 Checking Docker Desktop status...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not in PATH
    echo    Please install Docker Desktop from https://docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✅ Docker is installed

echo.
echo 📋 Checking Docker service status...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running
    echo    Please start Docker Desktop and wait for it to fully load
    echo    Look for the Docker whale icon in your system tray
    pause
    exit /b 1
)

echo ✅ Docker Desktop is running

echo.
echo 📋 Checking Firefly III container...
docker ps | findstr firefly-iii >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Firefly III container is running
    echo.
    echo 📋 Container details:
    docker ps --filter "name=firefly-iii" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo.
    echo 🌐 Firefly III should be accessible at: http://localhost:8080
    echo.
    echo 📋 Testing web connectivity...
    curl -s -o nul -w "HTTP Status: %%{http_code}" http://localhost:8080 2>nul
    echo.
    echo.
    echo 🎉 Firefly III is ready! Your Financial Dashboard should work now.
) else (
    echo ❌ Firefly III container is not running
    echo.
    echo 📋 Checking if container exists but is stopped...
    docker ps -a | findstr firefly-iii >nul 2>&1
    if %errorlevel% equ 0 (
        echo 🔄 Found stopped Firefly III container. Starting it...
        docker start firefly-iii
        echo ⏳ Waiting for container to start...
        timeout /t 10 /nobreak >nul
        echo ✅ Container started! Testing accessibility...
        timeout /t 5 /nobreak >nul
        curl -s -o nul -w "HTTP Status: %%{http_code}" http://localhost:8080 2>nul
        echo.
        echo 🎉 Firefly III is now running!
    ) else (
        echo ❌ No Firefly III container found
        echo.
        echo 📋 To create a new Firefly III installation:
        echo    1. Run: .\setup-firefly.bat
        echo    2. Or manually run the Docker command from the setup guide
        echo.
        echo 🔧 Quick setup command:
        echo docker run -d --name firefly-iii -p 8080:8080 ^
        echo   -e APP_KEY=SomeRandomStringOf32CharsExactly ^
        echo   -e DB_CONNECTION=sqlite ^
        echo   -e APP_URL=http://localhost:8080 ^
        echo   -v firefly_iii_upload:/var/www/html/storage/upload ^
        echo   fireflyiii/core:latest
    )
)

echo.
echo 📋 Environment Variables Check:
echo FIREFLY_BASE_URL: %FIREFLY_BASE_URL%
echo FIREFLY_API_TOKEN: %FIREFLY_API_TOKEN:~0,20%... (truncated)

echo.
echo 🔍 Status check complete!
pause
