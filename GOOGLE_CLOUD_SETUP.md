# Google Cloud VM Setup Guide for MCP Hub

This guide will help you set up the MCP Hub on a Google Cloud VM using direct Python execution (no Docker-in-Docker complexity).

## 🚀 Quick Start (Automated)

### 1. Create Google Cloud VM

```bash
gcloud compute instances create mcp-hub \
  --zone=us-central1-a \
  --machine-type=f1-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server \
  --metadata=startup-script='#! /bin/bash
  curl -fsSL https://raw.githubusercontent.com/pranjal-pravesh/mcp-docker-hub/main/deploy-gcp.sh | bash'
```

### 2. SSH and Deploy

```bash
# SSH into the VM
gcloud compute ssh mcp-hub --zone=us-central1-a

# Run deployment script
curl -fsSL https://raw.githubusercontent.com/pranjal-pravesh/mcp-docker-hub/main/deploy-gcp.sh | bash
```

### 3. Configure Firewall

```bash
gcloud compute firewall-rules create allow-mcp-hub \
  --allow tcp:8000 \
  --target-tags=http-server \
  --description="Allow MCP Hub traffic"
```

## 📋 Manual Setup (Step by Step)

### Prerequisites

- Google Cloud account
- `gcloud` CLI installed
- Basic knowledge of SSH and Linux commands

### Step 1: Create VM Instance

```bash
# Create a VM instance (f1-micro is free tier)
gcloud compute instances create mcp-hub \
  --zone=us-central1-a \
  --machine-type=f1-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server \
  --description="MCP Hub Server"
```

### Step 2: SSH into VM

```bash
gcloud compute ssh mcp-hub --zone=us-central1-a
```

### Step 3: Update System

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

### Step 4: Install Dependencies

```bash
# Install Python and pip
sudo apt-get install -y python3 python3-pip python3-venv git curl

# Install Docker (for MCP servers)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

# Reload shell to apply docker group
newgrp docker
```

### Step 5: Clone Repository

```bash
# Clone the repository
git clone https://github.com/pranjal-pravesh/mcp-docker-hub.git
cd mcp-docker-hub
```

### Step 6: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### Step 7: Configure Environment Variables

```bash
# Create .env file
cp env.example .env

# Edit with your API keys
nano .env
```

**Required environment variables:**
```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_TEAM_ID=your-team-id
SLACK_CHANNEL_IDS=channel1,channel2

# Brave Search Configuration
BRAVE_API_KEY=your-brave-api-key

# Wolfram Alpha Configuration
WOLFRAM_API_KEY=your-wolfram-api-key

# OpenWeather Configuration
OPENWEATHER_API_KEY=your-openweather-api-key

# Optional: Other services
GITHUB_TOKEN=your-github-token
POSTGRES_CONNECTION_STRING=your-postgres-connection
REDIS_URL=your-redis-url
NEWS_API_KEY=your-news-api-key
```

### Step 8: Create Systemd Service

```bash
# Create systemd service file
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

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable mcp-hub.service
sudo systemctl start mcp-hub.service
```

### Step 9: Configure Firewall

```bash
# Allow port 8000 in Google Cloud firewall
gcloud compute firewall-rules create allow-mcp-hub \
  --allow tcp:8000 \
  --target-tags=http-server \
  --description="Allow MCP Hub traffic"
```

### Step 10: Verify Installation

```bash
# Check service status
sudo systemctl status mcp-hub.service

# Get external IP
EXTERNAL_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")

# Test the API
curl http://$EXTERNAL_IP:8000/
```

## 🔧 Management Commands

### Service Management

```bash
# Check service status
sudo systemctl status mcp-hub.service

# View logs
sudo journalctl -u mcp-hub.service -f

# Restart service
sudo systemctl restart mcp-hub.service

# Stop service
sudo systemctl stop mcp-hub.service

# Start service
sudo systemctl start mcp-hub.service
```

### Application Management

```bash
# Check available servers
curl http://localhost:8000/servers/check-availability

# List all tools
curl http://localhost:8000/tools

# Start all servers
curl -X POST http://localhost:8000/servers/start-all

# Stop all servers
curl -X POST http://localhost:8000/servers/stop-all
```

### Updates and Maintenance

```bash
# Update the application
cd /home/$USER/mcp-docker-hub
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Restart service
sudo systemctl restart mcp-hub.service
```

## 🌐 Access URLs

After setup, your MCP Hub will be available at:

- **Main API**: `http://YOUR_VM_IP:8000`
- **API Documentation**: `http://YOUR_VM_IP:8000/docs`
- **Health Check**: `http://YOUR_VM_IP:8000/`
- **Alternative Docs**: `http://YOUR_VM_IP:8000/redoc`

## 🔍 Troubleshooting

### Common Issues

1. **Service Not Starting**
   ```bash
   # Check logs
   sudo journalctl -u mcp-hub.service -f
   
   # Check if port is in use
   sudo lsof -i :8000
   ```

2. **Docker Permission Issues**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   newgrp docker
   
   # Test Docker
   docker run hello-world
   ```

3. **Environment Variables Not Loading**
   ```bash
   # Check .env file
   cat .env
   
   # Test environment loading
   python scripts/check_servers.py
   ```

4. **Firewall Issues**
   ```bash
   # Check firewall rules
   gcloud compute firewall-rules list
   
   # Create firewall rule if missing
   gcloud compute firewall-rules create allow-mcp-hub \
     --allow tcp:8000 \
     --target-tags=http-server
   ```

5. **MCP Servers Not Starting**
   ```bash
   # Check Docker containers
   docker ps -a
   
   # Check MCP server logs
   docker logs <container_name>
   
   # Test individual server
   curl -X POST http://localhost:8000/servers/slack/start
   ```

### Performance Monitoring

```bash
# Check system resources
htop

# Check disk usage
df -h

# Check memory usage
free -h

# Check Docker resources
docker system df
```

## 🔒 Security Considerations

1. **Firewall Configuration**
   - Only allow necessary ports (8000 for MCP Hub)
   - Consider restricting access to specific IPs

2. **API Keys Security**
   - Store API keys in `.env` file
   - Never commit `.env` to version control
   - Use environment-specific configurations

3. **Service Security**
   - Run service as non-root user
   - Use virtual environment for isolation
   - Regular security updates

4. **HTTPS Setup (Optional)**
   ```bash
   # Install nginx for reverse proxy
   sudo apt-get install nginx
   
   # Configure SSL with Let's Encrypt
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## 📊 Monitoring and Logs

### Log Locations

- **Service logs**: `sudo journalctl -u mcp-hub.service`
- **Application logs**: `/home/$USER/mcp-docker-hub/logs/`
- **Docker logs**: `docker logs <container_name>`

### Health Checks

```bash
# Check service health
curl http://localhost:8000/

# Check server status
curl http://localhost:8000/servers

# Check tools availability
curl http://localhost:8000/tools
```

## 🚀 Next Steps

1. **Configure your API keys** in the `.env` file
2. **Test the API** using the documentation at `/docs`
3. **Add custom MCP servers** as needed
4. **Set up monitoring** and alerts
5. **Configure backups** for your configuration

## 📞 Support

If you encounter issues:

1. Check the logs: `sudo journalctl -u mcp-hub.service -f`
2. Verify environment variables: `python scripts/check_servers.py`
3. Test Docker: `docker run hello-world`
4. Check firewall: `gcloud compute firewall-rules list`

For additional help, refer to the main [README.md](README.md) or create an issue in the repository. 