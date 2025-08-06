#!/bin/bash

# MCP Hub Server Deployment Script
# Supports local, Railway, and Render deployments

set -e

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

# Function to check if Docker is running
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to check if Railway CLI is installed
check_railway() {
    if ! command_exists railway; then
        print_warning "Railway CLI not found. Installing..."
        npm install -g @railway/cli
    fi
}

# Function to check if Render CLI is installed
check_render() {
    if ! command_exists render; then
        print_warning "Render CLI not found. Please install from https://render.com/docs/cli"
        exit 1
    fi
}

# Function to create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_status "Creating .env file with template..."
        cat > .env << EOF
# MCP Hub Server Environment Variables

# Slack Configuration
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_TEAM_ID=your_slack_team_id_here
SLACK_CHANNEL_IDS=channel1,channel2

# Brave Search Configuration
BRAVE_API_KEY=your_brave_api_key_here

# Wolfram Alpha Configuration
WOLFRAM_APP_ID=your_wolfram_app_id_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
EOF
        print_success "Created .env file. Please update it with your actual API keys."
    else
        print_status ".env file already exists."
    fi
}

# Function to validate environment variables
validate_env() {
    print_status "Validating environment variables..."
    
    if [ -z "$SLACK_BOT_TOKEN" ] || [ "$SLACK_BOT_TOKEN" = "your_slack_bot_token_here" ]; then
        print_warning "SLACK_BOT_TOKEN not set or using default value"
    fi
    
    if [ -z "$SLACK_TEAM_ID" ] || [ "$SLACK_TEAM_ID" = "your_slack_team_id_here" ]; then
        print_warning "SLACK_TEAM_ID not set or using default value"
    fi
    
    if [ -z "$BRAVE_API_KEY" ] || [ "$BRAVE_API_KEY" = "your_brave_api_key_here" ]; then
        print_warning "BRAVE_API_KEY not set or using default value"
    fi
    
    if [ -z "$WOLFRAM_APP_ID" ] || [ "$WOLFRAM_APP_ID" = "your_wolfram_app_id_here" ]; then
        print_warning "WOLFRAM_APP_ID not set or using default value"
    fi
}

# Function to deploy locally with Docker
deploy_local() {
    print_status "Deploying MCP Hub Server locally with Docker..."
    
    check_docker
    create_env_file
    validate_env
    
    # Build and run with docker-compose
    cd deployment
    docker-compose up --build -d
    
    print_success "MCP Hub Server is running locally!"
    print_status "Access the API at: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
    print_status "Interactive API: http://localhost:8000/redoc"
    print_status ""
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop: docker-compose down"
}

# Function to deploy to Railway
deploy_railway() {
    print_status "Deploying MCP Hub Server to Railway..."
    
    check_railway
    create_env_file
    validate_env
    
    # Login to Railway if not already logged in
    if ! railway whoami >/dev/null 2>&1; then
        print_status "Please login to Railway..."
        railway login
    fi
    
    # Deploy to Railway
    railway up
    
    print_success "MCP Hub Server deployed to Railway!"
    print_status "Check your Railway dashboard for the deployment URL."
}

# Function to deploy to Render
deploy_render() {
    print_status "Deploying MCP Hub Server to Render..."
    
    check_render
    create_env_file
    validate_env
    
    # Deploy to Render
    render deploy
    
    print_success "MCP Hub Server deployed to Render!"
    print_status "Check your Render dashboard for the deployment URL."
}

# Function to show help
show_help() {
    echo "MCP Hub Server Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  local     Deploy locally with Docker"
    echo "  railway   Deploy to Railway"
    echo "  render    Deploy to Render"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local"
    echo "  $0 railway"
    echo "  $0 render"
    echo ""
    echo "Environment Variables:"
    echo "  SLACK_BOT_TOKEN     - Slack bot token for Slack MCP server"
    echo "  SLACK_TEAM_ID       - Slack team ID for Slack MCP server"
    echo "  SLACK_CHANNEL_IDS   - Comma-separated list of Slack channel IDs"
    echo "  BRAVE_API_KEY       - Brave Search API key"
    echo "  WOLFRAM_APP_ID      - Wolfram Alpha App ID"
    echo ""
    echo "For more information, see DEPLOYMENT_GUIDE.md"
}

# Main script logic
case "${1:-help}" in
    local)
        deploy_local
        ;;
    railway)
        deploy_railway
        ;;
    render)
        deploy_render
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 