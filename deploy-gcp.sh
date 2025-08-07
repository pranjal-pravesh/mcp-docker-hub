#!/bin/bash
set -e

echo "🚀 MCP Hub - Google Cloud VM Deployment Script"
echo "================================================"

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

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root. Use a regular user."
    exit 1
fi

print_status "Starting MCP Hub deployment..."

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
print_status "Installing Docker..."
sudo apt install -y docker.io docker-compose

# Start and enable Docker
print_status "Starting Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

# Add current user to docker group
print_status "Adding user to docker group..."
sudo usermod -aG docker $USER

# Reload shell to apply docker group
print_status "Reloading shell to apply docker group..."
newgrp docker

# Test Docker installation
print_status "Testing Docker installation..."
docker run hello-world

# Create project directory
PROJECT_DIR="$HOME/mcp-hub"
print_status "Setting up project directory: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    print_warning "Project directory already exists. Updating..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    print_status "Cloning project..."
    git clone https://github.com/yourusername/mcp-hub.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp env.example .env
    print_warning "Please edit .env file with your API keys before starting the hub."
    print_warning "You can use: nano .env"
else
    print_success ".env file already exists."
fi

# Create logs directory
mkdir -p logs

# Build and start the MCP Hub
print_status "Building and starting MCP Hub..."
docker-compose up -d --build

# Wait for the service to start
print_status "Waiting for MCP Hub to start..."
sleep 10

# Check if the service is running
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    print_success "MCP Hub is running successfully!"
    print_success "API Documentation: http://localhost:8000/docs"
    print_success "Health Check: http://localhost:8000/"
else
    print_error "MCP Hub failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Get external IP
EXTERNAL_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google" 2>/dev/null || echo "unknown")

if [ "$EXTERNAL_IP" != "unknown" ]; then
    print_success "External IP: $EXTERNAL_IP"
    print_success "Your MCP Hub is available at: http://$EXTERNAL_IP:8000"
    print_warning "Make sure port 8000 is open in your firewall rules."
else
    print_warning "Could not determine external IP. Check your VM's external IP manually."
fi

# Show useful commands
echo ""
print_status "Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop hub: docker-compose down"
echo "  Restart hub: docker-compose restart"
echo "  Update hub: git pull && docker-compose up -d --build"
echo "  Check status: docker-compose ps"

print_success "Deployment completed successfully! 🎉" 