#!/bin/bash
set -e

echo "🔄 Migrating from Docker-in-Docker to direct Python execution..."

# Stop the current Docker container
echo "🛑 Stopping current Docker container..."
docker-compose down

# Fix Docker permissions (without newgrp to avoid hanging)
echo "🔧 Setting up Docker permissions..."
sudo usermod -aG docker $USER

# Test Docker installation (this will work in the current session)
echo "🧪 Testing Docker installation..."
if docker run hello-world > /dev/null 2>&1; then
    echo "✅ Docker test successful"
else
    echo "⚠️  Docker test failed - this is normal if you need to restart the session"
    echo "   The service will work correctly after restart"
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

# Create systemd service for auto-start
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
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=DOCKER_HOST=unix:///var/run/docker.sock
ExecStart=$(pwd)/venv/bin/python -m mcp_hub.mcp_hub_server --host 0.0.0.0 --port 8000 --load-config
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

echo ""
echo "✅ Migration completed!"
echo ""
echo "🔧 Useful Commands:"
echo "  • Check service status: sudo systemctl status mcp-hub.service"
echo "  • View logs: sudo journalctl -u mcp-hub.service -f"
echo "  • Restart service: sudo systemctl restart mcp-hub.service"
echo "  • Stop service: sudo systemctl stop mcp-hub.service"
echo ""
echo "🌐 Your MCP Hub should now be accessible at:"
echo "  • http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google"):8000" 