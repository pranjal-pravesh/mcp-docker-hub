#!/bin/bash
set -e

echo "🚀 Starting MCP Hub deployment on Google Cloud VM..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed successfully"
else
    echo "✅ Docker already installed"
fi

# Fix Docker permissions and reload shell
echo "🔧 Setting up Docker permissions..."
sudo usermod -aG docker $USER
newgrp docker

# Test Docker installation
echo "🧪 Testing Docker installation..."
docker run hello-world

# Install Python and pip
echo "🐍 Installing Python and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install git if not present
if ! command -v git &> /dev/null; then
    sudo apt-get install -y git
fi

# Create project directory
PROJECT_DIR="/home/$USER/mcp-docker-hub"
echo "📁 Setting up project directory: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    echo "🔄 Updating existing repository..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone https://github.com/pranjal-pravesh/mcp-docker-hub.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# MCP Server Environment Variables
# Add your API keys and tokens here

# Slack Configuration
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_TEAM_ID=your_slack_team_id_here
SLACK_CHANNEL_IDS=your_channel_ids_here

# Brave Search Configuration
BRAVE_API_KEY=your_brave_api_key_here

# Wolfram Alpha Configuration
WOLFRAM_API_KEY=your_wolfram_api_key_here

# GitHub Configuration
GITHUB_TOKEN=your_github_token_here

# Database Configuration
POSTGRES_CONNECTION_STRING=your_postgres_connection_string_here
REDIS_URL=your_redis_url_here

# Weather and News Configuration
OPENWEATHER_API_KEY=your_openweather_api_key_here
NEWS_API_KEY=your_news_api_key_here

# Google Calendar Configuration
GOOGLE_CALENDAR_CREDENTIALS=your_google_calendar_credentials_here
GOOGLE_CALENDAR_TOKEN=your_google_calendar_token_here
EOF
    echo "⚠️  Please edit .env file with your actual API keys and tokens"
fi

# Create systemd service for auto-start with proper Docker configuration
echo "🔧 Creating systemd service for auto-start..."
sudo tee /etc/systemd/system/mcp-hub.service > /dev/null << EOF
[Unit]
Description=MCP Hub Server
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=$USER
Group=docker
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=DOCKER_HOST=unix:///var/run/docker.sock
ExecStart=$PROJECT_DIR/venv/bin/python -m mcp_hub.mcp_hub_server --host 0.0.0.0 --port 8000 --load-config
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable mcp-hub.service

# Start the service
echo "🚀 Starting MCP Hub service..."
sudo systemctl start mcp-hub.service

# Wait a moment for the service to start
sleep 5

# Check service status
echo "📊 Checking service status..."
sudo systemctl status mcp-hub.service --no-pager

# Get VM's external IP
EXTERNAL_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")

echo ""
echo "🎉 MCP Hub deployment completed!"
echo ""
echo "📋 Deployment Summary:"
echo "  • Project directory: $PROJECT_DIR"
echo "  • Virtual environment: $PROJECT_DIR/venv"
echo "  • Service: mcp-hub.service"
echo "  • External IP: $EXTERNAL_IP"
echo "  • Port: 8000"
echo ""
echo "🌐 Access URLs:"
echo "  • Main API: http://$EXTERNAL_IP:8000"
echo "  • API Documentation: http://$EXTERNAL_IP:8000/docs"
echo "  • Health Check: http://$EXTERNAL_IP:8000/"
echo ""
echo "🔧 Useful Commands:"
echo "  • Check service status: sudo systemctl status mcp-hub.service"
echo "  • View logs: sudo journalctl -u mcp-hub.service -f"
echo "  • Restart service: sudo systemctl restart mcp-hub.service"
echo "  • Stop service: sudo systemctl stop mcp-hub.service"
echo ""
echo "⚠️  Important:"
echo "  • Make sure to edit .env file with your actual API keys"
echo "  • Configure firewall to allow port 8000"
echo "  • The service will auto-start on VM reboot"
echo ""
echo "🔒 Security Note:"
echo "  • Consider setting up HTTPS with a reverse proxy"
echo "  • Restrict firewall access to specific IPs if needed" 