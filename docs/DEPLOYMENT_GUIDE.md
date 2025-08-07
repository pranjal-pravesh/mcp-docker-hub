# MCP Hub Deployment Guide

This guide covers different deployment options for the MCP Hub, with a focus on the recommended direct Python execution approach.

## 🎯 Recommended Approach: Direct Python Execution

The recommended deployment approach is to run the MCP Hub directly on the host system using Python, while still using Docker for individual MCP servers. This avoids the complexity of Docker-in-Docker and provides better reliability.

## 🚀 Google Cloud VM Deployment (Recommended)

### Quick Start

```bash
# 1. Create VM
gcloud compute instances create mcp-hub \
  --zone=us-central1-a \
  --machine-type=f1-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server

# 2. SSH and deploy
gcloud compute ssh mcp-hub --zone=us-central1-a
curl -fsSL https://raw.githubusercontent.com/pranjalpravesh121/mcp-docker-hub/main/deploy-gcp.sh | bash

# 3. Configure firewall
gcloud compute firewall-rules create allow-mcp-hub \
  --allow tcp:8000 \
  --target-tags=http-server
```

### Manual Setup

1. **Install Dependencies**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   sudo apt-get install -y python3 python3-pip python3-venv git curl
   
   # Install Docker for MCP servers
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   rm get-docker.sh
   newgrp docker
   ```

2. **Clone and Setup**
   ```bash
   git clone https://github.com/pranjalpravesh121/mcp-docker-hub.git
   cd mcp-docker-hub
   
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Configure Environment**
   ```bash
   cp env.example .env
   nano .env  # Add your API keys
   ```

4. **Create Systemd Service**
   ```bash
   sudo tee /etc/systemd/system/mcp-hub.service > /dev/null << EOF
   [Unit]
   Description=MCP Hub Server
   After=network.target docker.service
   Requires=docker.service
   
   [Service]
   Type=simple
   User=$USER
   WorkingDirectory=$(pwd)
   Environment=PATH=$(pwd)/venv/bin
   ExecStart=$(pwd)/venv/bin/python -m mcp_hub.mcp_hub_server --host 0.0.0.0 --port 8000 --load-config
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   sudo systemctl daemon-reload
   sudo systemctl enable mcp-hub.service
   sudo systemctl start mcp-hub.service
   ```

## 🐳 Docker Deployment (Alternative)

### Local Docker Deployment

```bash
# Build and run
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  mcp-hub:
    build:
      context: .
      dockerfile: deployment/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
      - BRAVE_API_KEY=${BRAVE_API_KEY}
      # ... other environment variables
    volumes:
      - ./logs:/app/logs
      - ./configs:/app/configs
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
```

## 🔧 Development Setup

### Local Development

```bash
# Clone repository
git clone https://github.com/pranjalpravesh121/mcp-docker-hub.git
cd mcp-docker-hub

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Configure environment
cp env.example .env
# Edit .env with your API keys

# Start development server
python -m mcp_hub.mcp_hub_server --dev --load-config
```

### Development with Docker

```bash
# Build development image
docker build -f deployment/Dockerfile -t mcp-hub:dev .

# Run with volume mounts for development
docker run -it --rm \
  -p 8000:8000 \
  -v $(pwd):/app \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --env-file .env \
  mcp-hub:dev
```

## 🌐 Cloud Platform Deployments

### Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Render Deployment

```bash
# Connect your GitHub repository to Render
# Render will automatically detect the Python app and deploy
```

### Heroku Deployment

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Create app and deploy
heroku create your-mcp-hub
git push heroku main
```

## 📋 Environment Configuration

### Required Environment Variables

```bash
# Core Configuration
PORT=8000
HOST=0.0.0.0

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

# Optional Services
GITHUB_TOKEN=your-github-token
POSTGRES_CONNECTION_STRING=your-postgres-connection
REDIS_URL=your-redis-url
NEWS_API_KEY=your-news-api-key
```

### Environment Setup Script

```bash
# Interactive environment setup
python scripts/setup_env.py

# Check server availability
python scripts/check_servers.py
```

## 🔍 Monitoring and Logging

### Log Management

```bash
# View service logs (systemd)
sudo journalctl -u mcp-hub.service -f

# View application logs
tail -f logs/mcp-hub.log

# View Docker logs
docker logs <container_name>
```

### Health Checks

```bash
# Service health
curl http://localhost:8000/

# Server status
curl http://localhost:8000/servers

# Tools availability
curl http://localhost:8000/tools
```

### Performance Monitoring

```bash
# System resources
htop
df -h
free -h

# Docker resources
docker system df
docker stats
```

## 🔒 Security Considerations

### Firewall Configuration

```bash
# Google Cloud
gcloud compute firewall-rules create allow-mcp-hub \
  --allow tcp:8000 \
  --target-tags=http-server

# Local firewall (UFW)
sudo ufw allow 8000
sudo ufw enable
```

### SSL/HTTPS Setup

```bash
# Install nginx and certbot
sudo apt-get install nginx certbot python3-certbot-nginx

# Configure SSL
sudo certbot --nginx -d your-domain.com
```

### API Key Security

- Store API keys in environment variables
- Never commit `.env` files to version control
- Use different keys for different environments
- Rotate keys regularly

## 🚨 Troubleshooting

### Common Issues

1. **Service Not Starting**
   ```bash
   # Check logs
   sudo journalctl -u mcp-hub.service -f
   
   # Check port availability
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

4. **MCP Servers Not Starting**
   ```bash
   # Check Docker containers
   docker ps -a
   
   # Check MCP server logs
   docker logs <container_name>
   
   # Test individual server
   curl -X POST http://localhost:8000/servers/slack/start
   ```

### Debug Commands

```bash
# Check service status
sudo systemctl status mcp-hub.service

# Check configuration
python scripts/check_servers.py

# Test API endpoints
curl http://localhost:8000/
curl http://localhost:8000/servers
curl http://localhost:8000/tools

# Check Docker
docker ps
docker images
```

## 📊 Performance Optimization

### Resource Limits

```bash
# Monitor resource usage
htop
docker stats

# Optimize Docker
docker system prune -a
```

### Scaling Considerations

- Use load balancers for high traffic
- Implement caching for frequently accessed data
- Monitor and optimize database connections
- Consider using CDN for static assets

## 🔄 Updates and Maintenance

### Application Updates

```bash
# Update code
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Restart service
sudo systemctl restart mcp-hub.service
```

### System Updates

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Update Docker
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

### Backup Strategy

```bash
# Backup configuration
cp .env .env.backup
cp configs/mcp_servers.json configs/mcp_servers.json.backup

# Backup logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

## 📞 Support

For additional help:

1. Check the [README.md](../README.md) for basic setup
2. Review the [Google Cloud Setup Guide](../GOOGLE_CLOUD_SETUP.md)
3. Check logs for specific error messages
4. Create an issue in the repository

## 🎉 Success Checklist

- [ ] MCP Hub service is running
- [ ] API is accessible at `/docs`
- [ ] Environment variables are configured
- [ ] MCP servers are starting successfully
- [ ] Tools are being discovered
- [ ] Firewall is configured
- [ ] Monitoring is set up
- [ ] Backups are configured 