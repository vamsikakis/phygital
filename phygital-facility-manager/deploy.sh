#!/bin/bash

# Phygital Facility Manager - Cloud Deployment Script
# This script helps prepare and deploy the application to cloud platforms

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    # Check Git
    if ! command_exists git; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to validate environment variables
validate_env() {
    print_status "Validating environment variables..."
    
    if [ ! -f ".env.production" ]; then
        print_warning ".env.production file not found"
        print_status "Creating from template..."
        cp .env.production.example .env.production
        print_warning "Please edit .env.production with your actual values before deploying"
        return 1
    fi
    
    # Source the environment file
    source .env.production
    
    # Check required variables
    required_vars=(
        "DATABASE_URL"
        "OPENAI_API_KEY"
        "SECRET_KEY"
        "JWT_SECRET_KEY"
        "VITE_API_URL"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ] || [ "${!var}" = "your-"* ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing or incomplete environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_warning "Please update .env.production with actual values"
        return 1
    fi
    
    print_success "Environment variables validated"
    return 0
}

# Function to build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build backend image
    print_status "Building backend image..."
    docker build -t phygital-backend ./backend
    
    # Build frontend image
    print_status "Building frontend image..."
    docker build -t phygital-frontend ./frontend
    
    print_success "Docker images built successfully"
}

# Function to test local deployment
test_local() {
    print_status "Testing local deployment with Docker Compose..."
    
    # Check if .env file exists for docker-compose
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from production template..."
        cp .env.production .env
    fi
    
    # Start services
    docker-compose up -d
    
    # Wait for services to start
    print_status "Waiting for services to start..."
    sleep 30
    
    # Test backend health
    print_status "Testing backend health..."
    if curl -f http://localhost:5000/health >/dev/null 2>&1; then
        print_success "Backend is healthy"
    else
        print_error "Backend health check failed"
        docker-compose logs backend
        return 1
    fi
    
    # Test frontend
    print_status "Testing frontend..."
    if curl -f http://localhost:3000/health >/dev/null 2>&1; then
        print_success "Frontend is healthy"
    else
        print_error "Frontend health check failed"
        docker-compose logs frontend
        return 1
    fi
    
    # Test Firefly III
    print_status "Testing Firefly III..."
    if curl -f http://localhost:8080/health >/dev/null 2>&1; then
        print_success "Firefly III is healthy"
    else
        print_warning "Firefly III health check failed (this is normal on first run)"
    fi
    
    print_success "Local deployment test completed"
    print_status "Services are running at:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend: http://localhost:5000"
    echo "  - Firefly III: http://localhost:8080"
    echo ""
    print_status "To stop services: docker-compose down"
}

# Function to prepare for cloud deployment
prepare_cloud_deployment() {
    print_status "Preparing for cloud deployment..."
    
    # Ensure all files are committed
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "You have uncommitted changes. Please commit them before deploying."
        git status --short
        return 1
    fi
    
    # Check if on main branch
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
        print_warning "You are not on the main/master branch. Current branch: $current_branch"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi
    
    # Push to remote
    print_status "Pushing to remote repository..."
    git push origin "$current_branch"
    
    print_success "Repository is ready for cloud deployment"
}

# Function to show deployment instructions
show_deployment_instructions() {
    print_success "Deployment preparation complete!"
    echo ""
    print_status "Next steps for cloud deployment:"
    echo ""
    echo "1. RENDER DEPLOYMENT:"
    echo "   - Go to https://dashboard.render.com"
    echo "   - Create new Web Service for backend:"
    echo "     * Environment: Docker"
    echo "     * Root Directory: backend"
    echo "     * Add environment variables from .env.production"
    echo "   - Create new Static Site for frontend:"
    echo "     * Root Directory: frontend"
    echo "     * Build Command: npm ci && npm run build"
    echo "     * Publish Directory: dist"
    echo "   - Create new Web Service for Firefly III:"
    echo "     * Docker Image: fireflyiii/core:latest"
    echo "     * Add Firefly environment variables"
    echo ""
    echo "2. ENVIRONMENT VARIABLES:"
    echo "   - Copy variables from .env.production to your cloud platform"
    echo "   - Update VITE_API_URL with your backend domain"
    echo "   - Update FIREFLY_BASE_URL with your Firefly domain"
    echo ""
    echo "3. CUSTOM DOMAINS (Optional):"
    echo "   - Add custom domains in your cloud platform"
    echo "   - Update DNS records"
    echo "   - Update CORS settings in backend"
    echo ""
    echo "4. DATABASE SETUP:"
    echo "   - Ensure Neon database is configured"
    echo "   - Run database migrations if needed"
    echo ""
    print_status "For detailed instructions, see CLOUD_DEPLOYMENT_GUIDE.md"
}

# Main deployment workflow
main() {
    echo ""
    print_status "🚀 Phygital Facility Manager - Cloud Deployment Preparation"
    echo "=========================================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-help}" in
        "check")
            check_prerequisites
            ;;
        "validate")
            check_prerequisites
            validate_env
            ;;
        "build")
            check_prerequisites
            validate_env || exit 1
            build_images
            ;;
        "test")
            check_prerequisites
            validate_env || exit 1
            build_images
            test_local
            ;;
        "prepare")
            check_prerequisites
            validate_env || exit 1
            build_images
            prepare_cloud_deployment
            show_deployment_instructions
            ;;
        "help"|*)
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  check     - Check prerequisites"
            echo "  validate  - Validate environment configuration"
            echo "  build     - Build Docker images"
            echo "  test      - Test local deployment"
            echo "  prepare   - Full preparation for cloud deployment"
            echo "  help      - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 check                    # Check if all tools are installed"
            echo "  $0 validate                 # Check environment variables"
            echo "  $0 test                     # Test everything locally"
            echo "  $0 prepare                  # Prepare for cloud deployment"
            echo ""
            ;;
    esac
}

# Run main function with all arguments
main "$@"
