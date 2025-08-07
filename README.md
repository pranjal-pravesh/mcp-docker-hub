# MCP Hub - Centralized API for MCP Tools

A centralized FastAPI server that provides a unified interface for all Model Context Protocol (MCP) tools. This hub allows you to easily manage and interact with multiple MCP servers through a single API endpoint.

## 🚀 Features

- **Centralized API**: Single endpoint for all MCP tools
- **Dynamic Server Management**: Add/remove Docker MCP servers effortlessly
- **Multiple Transport Support**: stdio, http, sse
- **Interactive Documentation**: Swagger UI and ReDoc
- **Health Monitoring**: Built-in health checks and status endpoints
- **Environment Variable Management**: Automatic configuration from .env files
- **Docker Support**: Run MCP servers in containers with proper isolation

## 🛠️ Quick Setup

### Prerequisites
- Python 3.11+
- Docker (for MCP servers)
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pranjalpravesh121/mcp-docker-hub.git
   cd mcp-docker-hub
   ```

2. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Start the hub**:
   ```bash
   python -m mcp_hub.mcp_hub_server --host 0.0.0.0 --port 8000 --load-config
   ```

5. **Access the API**:
   - Main API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/

## 🌐 Google Cloud VM Deployment

### Automated Deployment

1. **Create a Google Cloud VM** (f1-micro recommended for free tier):
   ```bash
   gcloud compute instances create mcp-hub \
     --zone=us-central1-a \
     --machine-type=f1-micro \
     --image-family=ubuntu-2204-lts \
     --image-project=ubuntu-os-cloud \
     --tags=http-server,https-server \
     --metadata=startup-script='#! /bin/bash
     curl -fsSL https://raw.githubusercontent.com/pranjalpravesh121/mcp-docker-hub/main/deploy-gcp.sh | bash'
   ```

2. **SSH into the VM**:
   ```bash
   gcloud compute ssh mcp-hub --zone=us-central1-a
   ```

3. **Run the deployment script**:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/pranjalpravesh121/mcp-docker-hub/main/deploy-gcp.sh | bash
   ```

### Manual Deployment

1. **SSH into your VM**:
   ```bash
   gcloud compute ssh YOUR_VM_NAME --zone=YOUR_ZONE
   ```

2. **Clone and run the deployment script**:
   ```bash
   git clone https://github.com/pranjalpravesh121/mcp-docker-hub.git
   cd mcp-docker-hub
   chmod +x deploy-gcp.sh
   ./deploy-gcp.sh
   ```

### Firewall Configuration

Allow port 8000 in your Google Cloud firewall:
```bash
gcloud compute firewall-rules create allow-mcp-hub \
  --allow tcp:8000 \
  --target-tags=http-server \
  --description="Allow MCP Hub traffic"
```

## 🔧 Dynamic MCP Server Management

### Adding Docker MCP Servers

#### Via API
```bash
curl -X POST "http://localhost:8000/servers/add-docker" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-server",
    "docker_image": "mcp/my-server",
    "transport": "stdio",
    "env_vars": {"API_KEY": "your-key"}
  }'
```

#### Via CLI
```bash
python scripts/manage_mcp_servers.py add \
  --name my-server \
  --docker-image mcp/my-server \
  --transport stdio \
  --env-vars '{"API_KEY": "your-key"}'
```

#### Via JSON Configuration
Edit `configs/mcp_servers.json`:
```json
{
  "my-server": {
    "docker_image": "mcp/my-server",
    "transport": "stdio",
    "env_vars": {
      "API_KEY": "your-key"
    }
  }
}
```

### Removing Servers
```bash
# Via API
curl -X DELETE "http://localhost:8000/servers/my-server"

# Via CLI
python scripts/manage_mcp_servers.py remove --name my-server
```

## 📋 Available API Endpoints

### Core Endpoints
- `GET /` - Server status and health check
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

### Server Management
- `GET /servers` - List all MCP servers
- `POST /servers/start-all` - Start all servers
- `POST /servers/stop-all` - Stop all servers
- `POST /servers/add-docker` - Add Docker MCP server
- `DELETE /servers/{name}` - Remove server

### Tool Management
- `GET /tools` - List all available tools
- `POST /tools/call` - Call any MCP tool
- `GET /tools/info/{tool_name}` - Get tool details

### Configuration
- `GET /servers/configured` - List configured servers
- `POST /servers/load-config` - Load from JSON config
- `POST /servers/save-config` - Save to JSON config
- `GET /servers/check-availability` - Check server availability

## 🔍 Troubleshooting

### Common Issues

1. **Docker Permission Denied**:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Port Already in Use**:
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

3. **Environment Variables Not Loading**:
   ```bash
   python scripts/check_servers.py
   ```

4. **Service Not Starting**:
   ```bash
   sudo systemctl status mcp-hub.service
   sudo journalctl -u mcp-hub.service -f
   ```

### Migration from Docker-in-Docker

If you're currently using Docker-in-Docker and experiencing permission issues:

```bash
# Run the migration script
./migrate-to-direct.sh
```

This will:
- Stop the Docker container
- Set up a Python virtual environment
- Create a systemd service
- Start the MCP Hub directly on the host

## 📚 Documentation

- [Dynamic MCP Servers Guide](docs/DYNAMIC_MCP_SERVERS.md)
- [Google Cloud Setup Guide](GOOGLE_CLOUD_SETUP.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 