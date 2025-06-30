@echo off
REM Firefly III Quick Setup Script for Phygital Facility Manager (Windows)
REM This script automates the installation of Firefly III for financial management

echo 🏦 Firefly III Setup for Phygital Facility Manager
echo ==================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Visit: https://docs.docker.com/desktop/install/windows/
    pause
    exit /b 1
)

echo ✅ Docker is installed

REM Check if Firefly III is already running
docker ps | findstr firefly-iii >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Firefly III container is already running
    echo    Container status:
    docker ps | findstr firefly-iii
    echo.
    echo    To access Firefly III: http://localhost:8080
    pause
    exit /b 0
)

REM Check if container exists but is stopped
docker ps -a | findstr firefly-iii >nul 2>&1
if %errorlevel% equ 0 (
    echo 🔄 Found existing Firefly III container. Starting it...
    docker start firefly-iii
    echo ✅ Firefly III started successfully!
    echo    Access it at: http://localhost:8080
    pause
    exit /b 0
)

echo 🚀 Installing Firefly III...

REM Generate a random 32-character APP_KEY (simplified for Windows)
set APP_KEY=SomeRandomStringOf32CharsExactly
echo 🔑 Using APP_KEY: %APP_KEY%

REM Create volume for uploads
echo 📁 Creating Docker volume for file uploads...
docker volume create firefly_iii_upload

REM Run Firefly III container
echo 🐳 Starting Firefly III container...
docker run -d ^
  --name firefly-iii ^
  -p 8080:8080 ^
  -e APP_KEY=%APP_KEY% ^
  -e DB_CONNECTION=sqlite ^
  -e APP_URL=http://localhost:8080 ^
  -v firefly_iii_upload:/var/www/html/storage/upload ^
  fireflyiii/core:latest

REM Wait for container to start
echo ⏳ Waiting for Firefly III to start...
timeout /t 15 /nobreak >nul

REM Check if container is running
docker ps | findstr firefly-iii >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Firefly III is now running!
    echo.
    echo 📋 Next Steps:
    echo 1. Open Firefly III: http://localhost:8080
    echo 2. Complete the initial setup wizard
    echo 3. Create your admin account
    echo 4. Go to Profile → OAuth → Personal Access Tokens
    echo 5. Create a new token named 'Facility Manager Integration'
    echo 6. Copy the token and add it to your .env file:
    echo    FIREFLY_BASE_URL=http://localhost:8080
    echo    FIREFLY_API_TOKEN=your_very_long_token_here
    echo 7. Restart your facility manager application
    echo.
    echo 🎉 Setup complete! Your Financial Dashboard will be ready after token configuration.
    echo.
    echo Opening Firefly III in your browser...
    start http://localhost:8080
) else (
    echo ❌ Failed to start Firefly III container
    echo    Check Docker logs: docker logs firefly-iii
)

pause
