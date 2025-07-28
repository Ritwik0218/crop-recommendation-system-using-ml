#!/bin/bash

# Production Deployment Script for Crop Recommendation System
# This script provides multiple deployment options

set -e  # Exit on any error

echo "🚀 Crop Recommendation System - Production Deployment"
echo "===================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project directory."
    exit 1
fi

# Function to display menu
show_menu() {
    echo ""
    echo "📋 Choose deployment option:"
    echo "1) 🐍 Standard Python deployment (recommended for development)"
    echo "2) 🦄 Gunicorn deployment (recommended for production)"
    echo "3) 🐳 Docker deployment (containerized)"
    echo "4) 🐳 Docker Compose deployment (with optional nginx)"
    echo "5) 🔍 Test current deployment"
    echo "6) 📊 Start monitoring"
    echo "7) 🛑 Stop all services"
    echo "8) 📖 Show deployment guide"
    echo "9) ❌ Exit"
    echo ""
}

# Function for standard Python deployment
deploy_python() {
    echo "🐍 Starting standard Python deployment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install -q -r requirements.txt
    
    # Validate setup
    python validate_setup.py
    
    # Set production environment
    export FLASK_ENV=production
    export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
    
    echo "🚀 Starting application on port 5000..."
    python app.py
}

# Function for Gunicorn deployment
deploy_gunicorn() {
    echo "🦄 Starting Gunicorn deployment..."
    
    # Install gunicorn if not present
    pip install gunicorn 2>/dev/null || echo "Gunicorn already installed"
    
    # Create gunicorn config if it doesn't exist
    if [ ! -f "gunicorn.conf.py" ]; then
        cat > gunicorn.conf.py << EOF
# Gunicorn configuration
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
access_log = "access.log"
error_log = "error.log"
log_level = "info"
EOF
    fi
    
    # Set production environment
    export FLASK_ENV=production
    export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
    
    echo "🚀 Starting Gunicorn server..."
    gunicorn --config gunicorn.conf.py app:app
}

# Function for Docker deployment
deploy_docker() {
    echo "🐳 Starting Docker deployment..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Build the image
    echo "🔨 Building Docker image..."
    docker build -t crop-recommendation-system .
    
    # Stop existing container if running
    docker stop crop-app 2>/dev/null || true
    docker rm crop-app 2>/dev/null || true
    
    # Run the container
    echo "🚀 Starting Docker container..."
    docker run -d \
        --name crop-app \
        -p 5000:5000 \
        --restart unless-stopped \
        -e SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))') \
        crop-recommendation-system
    
    echo "✅ Container started. Check logs with: docker logs crop-app"
}

# Function for Docker Compose deployment
deploy_docker_compose() {
    echo "🐳 Starting Docker Compose deployment..."
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "📋 Choose Docker Compose profile:"
    echo "1) Basic (app only)"
    echo "2) With Nginx reverse proxy"
    echo "3) With monitoring"
    echo "4) Full stack (app + nginx + monitoring)"
    
    read -p "Enter choice (1-4): " compose_choice
    
    case $compose_choice in
        1)
            echo "🚀 Starting basic deployment..."
            docker-compose up -d crop-app
            ;;
        2)
            echo "🚀 Starting with Nginx..."
            docker-compose --profile production up -d
            ;;
        3)
            echo "🚀 Starting with monitoring..."
            docker-compose --profile monitoring up -d
            ;;
        4)
            echo "🚀 Starting full stack..."
            docker-compose --profile production --profile monitoring up -d
            ;;
        *)
            echo "❌ Invalid choice"
            return 1
            ;;
    esac
    
    echo "✅ Services started. Check status with: docker-compose ps"
}

# Function to test deployment
test_deployment() {
    echo "🔍 Testing current deployment..."
    
    # Test different ports
    ports=(5000 5001 80)
    
    for port in "${ports[@]}"; do
        echo "Testing port $port..."
        if curl -s "http://localhost:$port/health" > /dev/null; then
            echo "✅ Application responding on port $port"
            echo "📊 Health check result:"
            curl -s "http://localhost:$port/health" | python -m json.tool 2>/dev/null || echo "Health endpoint available but not JSON"
            echo ""
            echo "🌐 Application URL: http://localhost:$port"
            break
        else
            echo "❌ No response on port $port"
        fi
    done
}

# Function to start monitoring
start_monitoring() {
    echo "📊 Starting monitoring..."
    
    # Find the application port
    port=5000
    if curl -s "http://localhost:5001/health" > /dev/null; then
        port=5001
    fi
    
    echo "🔍 Monitoring application on port $port"
    python monitor.py --url "http://localhost:$port"
}

# Function to stop all services
stop_services() {
    echo "🛑 Stopping all services..."
    
    # Stop Docker containers
    docker stop crop-app 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    
    # Kill Python processes on common ports
    for port in 5000 5001; do
        pid=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$pid" ]; then
            echo "🔪 Stopping process on port $port (PID: $pid)"
            kill $pid 2>/dev/null || true
        fi
    done
    
    echo "✅ All services stopped"
}

# Function to show deployment guide
show_guide() {
    echo "📖 Opening deployment guide..."
    if command -v less &> /dev/null; then
        less DEPLOYMENT_GUIDE.md
    else
        cat DEPLOYMENT_GUIDE.md
    fi
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice (1-9): " choice
    
    case $choice in
        1)
            deploy_python
            ;;
        2)
            deploy_gunicorn
            ;;
        3)
            deploy_docker
            ;;
        4)
            deploy_docker_compose
            ;;
        5)
            test_deployment
            ;;
        6)
            start_monitoring
            ;;
        7)
            stop_services
            ;;
        8)
            show_guide
            ;;
        9)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please enter 1-9."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
