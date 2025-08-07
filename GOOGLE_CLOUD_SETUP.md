# Google Cloud VM Setup Guide for MCP Hub

This guide will help you deploy your MCP Hub on Google Cloud's free tier VM with full Docker support.

## 🎯 Overview

| Component | Details |
|-----------|---------|
| **Platform** | Google Cloud Free Tier |
| **Instance** | `f1-micro` (free tier eligible) |
| **OS** | Ubuntu 22.04 LTS |
| **Region** | `us-west1` (free tier eligible) |
| **Features** | Docker, Docker Compose, Public IP |

## 📋 Prerequisites

- Google account
- Phone number (for verification)
- Credit/debit card (₹2 refundable charge in India)
- GitHub repository with your MCP Hub code

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud VM

1. **Go to Google Cloud Console**
   ```
   https://console.cloud.google.com
   ```

2. **Create New Project** (if needed)
   - Click on project dropdown → "New Project"
   - Name: `mcp-hub-project`
   - Click "Create"

3. **Enable Compute Engine API**
   - Go to "APIs & Services" → "Library"
   - Search for "Compute Engine API"
   - Click "Enable"

4. **Create VM Instance**
   - Go to "Compute Engine" → "VM instances"
   - Click "Create Instance"

5. **Configure VM Settings**
   ```
   Name: mcp-vm
   Region: us-west1 (free tier eligible)
   Zone: us-west1-a
   Machine type: f1-micro (free tier eligible)
   Boot disk: Ubuntu 22.04 LTS
   Allow HTTP traffic: ✅
   Allow HTTPS traffic: ✅
   ```

6. **Click "Create"**

### Step 2: Connect to VM

1. **SSH into VM**
   - Click "SSH" button next to your VM
   - This opens a browser-based terminal

2. **Update System**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

### Step 3: Deploy MCP Hub

#### Option A: Automated Deployment (Recommended)

1. **Download and run the deployment script**
   ```bash
   # Download the script
   curl -O https://raw.githubusercontent.com/yourusername/mcp-hub/main/deploy-gcp.sh
   
   # Make it executable
   chmod +x deploy-gcp.sh
   
   # Run the deployment
   ./deploy-gcp.sh
   ```

2. **Edit environment variables**
   ```bash
   nano .env
   ```
   
   Add your API keys:
   ```bash
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_TEAM_ID=T1234567890
   BRAVE_API_KEY=your-brave-key
   WOLFRAM_API_KEY=your-wolfram-key
   OPENWEATHER_API_KEY=your-weather-key
   ```

#### Option B: Manual Deployment

1. **Install Docker**
   ```bash
   sudo apt install -y docker.io docker-compose
   sudo systemctl enable docker
   sudo systemctl start docker
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/mcp-hub.git
   cd mcp-hub
   ```

3. **Setup Environment**
   ```bash
   cp env.example .env
   nano .env  # Add your API keys
   ```

4. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

### Step 4: Configure Firewall

1. **Create Firewall Rule**
   ```bash
   gcloud compute firewall-rules create allow-mcp \
       --allow tcp:8000 \
       --source-ranges=0.0.0.0/0 \
       --description="Allow MCP Hub on port 8000"
   ```

2. **Or via Console**
   - Go to "VPC network" → "Firewall"
   - Click "Create Firewall Rule"
   - Name: `allow-mcp`
   - Ports: `tcp:8000`
   - Source: `0.0.0.0/0`

### Step 5: Access Your MCP Hub

1. **Get External IP**
   ```bash
   curl -H "Metadata-Flavor: Google" \
        http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip
   ```

2. **Access URLs**
   ```
   Main API: http://YOUR_EXTERNAL_IP:8000
   Documentation: http://YOUR_EXTERNAL_IP:8000/docs
   Health Check: http://YOUR_EXTERNAL_IP:8000/
   ```

## 🔧 Management Commands

### View Logs
```bash
docker-compose logs -f
```

### Stop Hub
```bash
docker-compose down
```

### Restart Hub
```bash
docker-compose restart
```

### Update Hub
```bash
git pull
docker-compose up -d --build
```

### Check Status
```bash
docker-compose ps
```

## 🛡️ Security Considerations

1. **Firewall Rules**
   - Only open necessary ports (8000)
   - Consider restricting source IPs

2. **Environment Variables**
   - Never commit `.env` file to git
   - Use strong API keys

3. **Regular Updates**
   - Keep system packages updated
   - Update Docker images regularly

## 💰 Cost Optimization

### Free Tier Limits
- **f1-micro**: 1 vCPU, 0.6 GB RAM
- **Region**: us-west1 only
- **Storage**: 30 GB standard persistent disk
- **Network**: 1 GB egress per month

### Monitoring Usage
```bash
# Check resource usage
htop
df -h
docker system df
```

## 🚨 Troubleshooting

### Common Issues

1. **Docker Permission Denied**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Port Already in Use**
   ```bash
   sudo netstat -tulpn | grep 8000
   sudo lsof -i :8000
   ```

3. **Out of Memory**
   ```bash
   # Add swap space
   sudo fallocate -l 1G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

4. **Service Won't Start**
   ```bash
   docker-compose logs mcp-hub
   docker-compose down
   docker-compose up -d --build
   ```

### Get Help
- Check logs: `docker-compose logs -f`
- Check status: `docker-compose ps`
- Restart service: `docker-compose restart`

## 🎉 Success!

Your MCP Hub is now running on Google Cloud with:
- ✅ Full Docker support
- ✅ Public API access
- ✅ Automatic restarts
- ✅ Health monitoring
- ✅ Cost-effective (free tier)

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure firewall rules are configured
4. Check Google Cloud console for VM status 