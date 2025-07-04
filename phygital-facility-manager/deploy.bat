@echo off
REM Phygital Facility Manager - Cloud Deployment Script (Windows)
REM This script helps prepare and deploy the application to cloud platforms

setlocal enabledelayedexpansion

REM Function to print status messages
:print_status
echo [INFO] %~1
goto :eof

:print_success
echo [SUCCESS] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

REM Function to check if command exists
:command_exists
where %1 >nul 2>&1
goto :eof

REM Function to check prerequisites
:check_prerequisites
call :print_status "Checking prerequisites..."

REM Check Docker
call :command_exists docker
if %errorlevel% neq 0 (
    call :print_error "Docker is not installed. Please install Docker Desktop first."
    exit /b 1
)

REM Check Node.js
call :command_exists node
if %errorlevel% neq 0 (
    call :print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit /b 1
)

REM Check Python
call :command_exists python
if %errorlevel% neq 0 (
    call :print_error "Python is not installed. Please install Python 3.11+ first."
    exit /b 1
)

REM Check Git
call :command_exists git
if %errorlevel% neq 0 (
    call :print_error "Git is not installed. Please install Git first."
    exit /b 1
)

call :print_success "All prerequisites are installed"
goto :eof

REM Function to validate environment variables
:validate_env
call :print_status "Validating environment variables..."

if not exist ".env.production" (
    call :print_warning ".env.production file not found"
    call :print_status "Creating from template..."
    copy .env.production.example .env.production >nul
    call :print_warning "Please edit .env.production with your actual values before deploying"
    exit /b 1
)

call :print_success "Environment variables file found"
goto :eof

REM Function to build Docker images
:build_images
call :print_status "Building Docker images..."

REM Build backend image
call :print_status "Building backend image..."
docker build -t phygital-backend ./backend
if %errorlevel% neq 0 (
    call :print_error "Failed to build backend image"
    exit /b 1
)

REM Build frontend image
call :print_status "Building frontend image..."
docker build -t phygital-frontend ./frontend
if %errorlevel% neq 0 (
    call :print_error "Failed to build frontend image"
    exit /b 1
)

call :print_success "Docker images built successfully"
goto :eof

REM Function to test local deployment
:test_local
call :print_status "Testing local deployment with Docker Compose..."

REM Check if .env file exists for docker-compose
if not exist ".env" (
    call :print_status "Creating .env file from production template..."
    copy .env.production .env >nul
)

REM Start services
docker-compose up -d
if %errorlevel% neq 0 (
    call :print_error "Failed to start services"
    exit /b 1
)

REM Wait for services to start
call :print_status "Waiting for services to start..."
timeout /t 30 /nobreak >nul

REM Test backend health
call :print_status "Testing backend health..."
curl -f http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Backend is healthy"
) else (
    call :print_error "Backend health check failed"
    docker-compose logs backend
    exit /b 1
)

REM Test frontend
call :print_status "Testing frontend..."
curl -f http://localhost:3000/health >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Frontend is healthy"
) else (
    call :print_error "Frontend health check failed"
    docker-compose logs frontend
    exit /b 1
)

REM Test Firefly III
call :print_status "Testing Firefly III..."
curl -f http://localhost:8080/health >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Firefly III is healthy"
) else (
    call :print_warning "Firefly III health check failed (this is normal on first run)"
)

call :print_success "Local deployment test completed"
call :print_status "Services are running at:"
echo   - Frontend: http://localhost:3000
echo   - Backend: http://localhost:5000
echo   - Firefly III: http://localhost:8080
echo.
call :print_status "To stop services: docker-compose down"
goto :eof

REM Function to prepare for cloud deployment
:prepare_cloud_deployment
call :print_status "Preparing for cloud deployment..."

REM Check git status
git status --porcelain >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('git status --porcelain') do (
        call :print_warning "You have uncommitted changes. Please commit them before deploying."
        git status --short
        exit /b 1
    )
)

REM Push to remote
call :print_status "Pushing to remote repository..."
git push origin HEAD
if %errorlevel% neq 0 (
    call :print_error "Failed to push to remote repository"
    exit /b 1
)

call :print_success "Repository is ready for cloud deployment"
goto :eof

REM Function to show deployment instructions
:show_deployment_instructions
call :print_success "Deployment preparation complete!"
echo.
call :print_status "Next steps for cloud deployment:"
echo.
echo 1. RENDER DEPLOYMENT:
echo    - Go to https://dashboard.render.com
echo    - Create new Web Service for backend:
echo      * Environment: Docker
echo      * Root Directory: backend
echo      * Add environment variables from .env.production
echo    - Create new Static Site for frontend:
echo      * Root Directory: frontend
echo      * Build Command: npm ci ^&^& npm run build
echo      * Publish Directory: dist
echo    - Create new Web Service for Firefly III:
echo      * Docker Image: fireflyiii/core:latest
echo      * Add Firefly environment variables
echo.
echo 2. ENVIRONMENT VARIABLES:
echo    - Copy variables from .env.production to your cloud platform
echo    - Update VITE_API_URL with your backend domain
echo    - Update FIREFLY_BASE_URL with your Firefly domain
echo.
echo 3. CUSTOM DOMAINS (Optional):
echo    - Add custom domains in your cloud platform
echo    - Update DNS records
echo    - Update CORS settings in backend
echo.
echo 4. DATABASE SETUP:
echo    - Ensure Neon database is configured
echo    - Run database migrations if needed
echo.
call :print_status "For detailed instructions, see CLOUD_DEPLOYMENT_GUIDE.md"
goto :eof

REM Main function
:main
echo.
call :print_status "🚀 Phygital Facility Manager - Cloud Deployment Preparation"
echo ==========================================================
echo.

if "%1"=="check" (
    call :check_prerequisites
) else if "%1"=="validate" (
    call :check_prerequisites
    call :validate_env
) else if "%1"=="build" (
    call :check_prerequisites
    call :validate_env
    if !errorlevel! equ 0 call :build_images
) else if "%1"=="test" (
    call :check_prerequisites
    call :validate_env
    if !errorlevel! equ 0 (
        call :build_images
        if !errorlevel! equ 0 call :test_local
    )
) else if "%1"=="prepare" (
    call :check_prerequisites
    call :validate_env
    if !errorlevel! equ 0 (
        call :build_images
        if !errorlevel! equ 0 (
            call :prepare_cloud_deployment
            if !errorlevel! equ 0 call :show_deployment_instructions
        )
    )
) else (
    echo Usage: %0 [command]
    echo.
    echo Commands:
    echo   check     - Check prerequisites
    echo   validate  - Validate environment configuration
    echo   build     - Build Docker images
    echo   test      - Test local deployment
    echo   prepare   - Full preparation for cloud deployment
    echo   help      - Show this help message
    echo.
    echo Examples:
    echo   %0 check                    # Check if all tools are installed
    echo   %0 validate                 # Check environment variables
    echo   %0 test                     # Test everything locally
    echo   %0 prepare                  # Prepare for cloud deployment
    echo.
)

goto :eof

REM Call main function
call :main %*
