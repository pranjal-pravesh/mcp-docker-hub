# Dynamic MCP Server Management Guide

This guide explains how to dynamically add and remove Docker MCP servers to your MCP Hub with minimal configuration changes.

## 🎯 Overview

The MCP Hub supports effortless addition and removal of any Docker MCP server through three methods:
- **REST API** - Programmatic server management
- **CLI Tool** - Command-line interface
- **JSON Configuration** - File-based configuration

## 🚀 Quick Start

### 1. Check Available Servers

```bash
# Check which servers are available with your current environment variables
python scripts/check_servers.py
```

### 2. Start Hub with Available Servers

```bash
# Start the hub and automatically load available servers
python -m mcp_hub.mcp_hub_server --load-config
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/
- **Server Status**: http://localhost:8000/servers

## 🔧 CLI Management

### Installation

The CLI tool is included in the project. No additional installation needed.

### Basic Commands

```bash
# Add a new server
python scripts/manage_mcp_servers.py add \
  --name my-slack \
  --docker-image mcp/slack \
  --env-vars SLACK_BOT_TOKEN SLACK_TEAM_ID

# Add server with HTTP transport
python scripts/manage_mcp_servers.py add \
  --name brave \
  --docker-image mcp/brave-search \
  --transport http \
  --ports 8080:8080

# List all servers
python scripts/manage_mcp_servers.py list

# Show server details
python scripts/manage_mcp_servers.py show --name my-slack

# Remove a server
python scripts/manage_mcp_servers.py remove --name my-slack
```

### Advanced CLI Options

```bash
# Add server with custom configuration
python scripts/manage_mcp_servers.py add \
  --name custom-server \
  --docker-image mcp/custom-server \
  --transport stdio \
  --env-vars API_KEY SECRET_KEY \
  --ports 9000:9000 \
  --volumes /host/path:/container/path \
  --health-check-url http://localhost:9000/health \
  --health-check-timeout 60

# Add server with additional arguments
python scripts/manage_mcp_servers.py add \
  --name file-system \
  --docker-image mcp/filesystem \
  --transport stdio \
  --additional-args /workspace
```

## 🌐 REST API Management

### Server Operations

```bash
# Check server availability
curl "http://localhost:8000/servers/check-availability"

# Add a new server
curl -X POST "http://localhost:8000/servers/add-docker" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-server",
    "docker_image": "mcp/slack",
    "transport": "stdio",
    "env_vars": {
      "SLACK_BOT_TOKEN": "xoxb-your-token",
      "SLACK_TEAM_ID": "your-team-id"
    }
  }'

# List configured servers
curl "http://localhost:8000/servers/configured"

# Get server configuration
curl "http://localhost:8000/servers/config/my-server"

# Remove a server
curl -X DELETE "http://localhost:8000/servers/my-server"

# Load configuration from file
curl -X POST "http://localhost:8000/servers/load-config"

# Save current configuration
curl -X POST "http://localhost:8000/servers/save-config"
```

### Server Control

```bash
# Start all servers
curl -X POST "http://localhost:8000/servers/start-all"

# Stop all servers
curl -X POST "http://localhost:8000/servers/stop-all"

# Start specific server
curl -X POST "http://localhost:8000/servers/my-server/start"

# Stop specific server
curl -X POST "http://localhost:8000/servers/my-server/stop"
```

## 📄 JSON Configuration

### Configuration File Structure

Edit `configs/mcp_servers.json` to define your servers:

```json
{
  "slack": {
    "docker_image": "mcp/slack",
    "transport": "stdio",
    "env_vars": {
      "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
      "SLACK_TEAM_ID": "${SLACK_TEAM_ID}",
      "SLACK_CHANNEL_IDS": "${SLACK_CHANNEL_IDS}"
    },
    "description": "Slack integration for messaging and notifications"
  },
  "brave-search": {
    "docker_image": "mcp/brave-search",
    "transport": "http",
    "env_vars": {
      "BRAVE_API_KEY": "${BRAVE_API_KEY}"
    },
    "docker_ports": ["8080:8080"],
    "health_check_url": "http://localhost:8080/health",
    "health_check_timeout": 30,
    "description": "Brave Search for web queries"
  },
  "wolfram-alpha": {
    "docker_image": "mcp/wolfram-alpha",
    "transport": "stdio",
    "env_vars": {
      "WOLFRAM_API_KEY": "${WOLFRAM_API_KEY}"
    },
    "description": "Wolfram Alpha for computational knowledge"
  },
  "openweather": {
    "docker_image": "mcp/openweather",
    "transport": "stdio",
    "env_vars": {
      "OPENWEATHER_API_KEY": "${OPENWEATHER_API_KEY}"
    },
    "description": "OpenWeather for weather information"
  }
}
```

### Environment Variable Substitution

The configuration supports environment variable substitution:

```json
{
  "my-server": {
    "docker_image": "mcp/my-server",
    "env_vars": {
      "API_KEY": "${MY_API_KEY}",
      "SECRET": "${MY_SECRET}",
      "WORKSPACE": "${PWD}"
    }
  }
}
```

**Supported substitutions:**
- `${VARIABLE_NAME}` - Environment variables
- `${PWD}` - Current working directory
- `${HOME}` - User home directory

### Loading Configuration

```bash
# Load configuration on startup
python -m mcp_hub.mcp_hub_server --load-config

# Load configuration via API
curl -X POST "http://localhost:8000/servers/load-config"

# Load specific configuration file
curl -X POST "http://localhost:8000/servers/load-config?config_file=configs/custom_servers.json"
```

## 🔧 Configuration Options

### Transport Types

| Transport | Description | Use Case |
|-----------|-------------|----------|
| `stdio` | Standard input/output | Most MCP servers |
| `http` | HTTP/HTTPS | Web-based servers |
| `sse` | Server-Sent Events | Real-time servers |

### Docker Configuration

```json
{
  "server-name": {
    "docker_image": "mcp/server-image",
    "transport": "stdio",
    "env_vars": {
      "API_KEY": "your-key"
    },
    "docker_ports": ["8080:8080", "9000:9000"],
    "docker_volumes": ["/host/path:/container/path"],
    "additional_args": ["arg1", "arg2"],
    "health_check_url": "http://localhost:8080/health",
    "health_check_timeout": 30
  }
}
```

### Health Check Configuration

```json
{
  "server-name": {
    "docker_image": "mcp/server-image",
    "health_check_url": "http://localhost:8080/health",
    "health_check_timeout": 60,
    "health_check_interval": 30
  }
}
```

## 🛠️ Server Management Workflow

### 1. Add New Server

```bash
# Step 1: Add server configuration
python scripts/manage_mcp_servers.py add \
  --name new-server \
  --docker-image mcp/new-server \
  --transport stdio \
  --env-vars API_KEY

# Step 2: Start the server
curl -X POST "http://localhost:8000/servers/new-server/start"

# Step 3: Verify server is running
curl "http://localhost:8000/servers"
```

### 2. Update Server Configuration

```bash
# Step 1: Remove old configuration
python scripts/manage_mcp_servers.py remove --name old-server

# Step 2: Add new configuration
python scripts/manage_mcp_servers.py add \
  --name new-server \
  --docker-image mcp/updated-server \
  --transport http \
  --ports 8080:8080

# Step 3: Start updated server
curl -X POST "http://localhost:8000/servers/new-server/start"
```

### 3. Remove Server

```bash
# Step 1: Stop the server
curl -X POST "http://localhost:8000/servers/server-name/stop"

# Step 2: Remove configuration
python scripts/manage_mcp_servers.py remove --name server-name

# Step 3: Verify removal
curl "http://localhost:8000/servers/configured"
```

## 🔍 Troubleshooting

### Common Issues

1. **Server Not Starting**
   ```bash
   # Check Docker logs
   docker logs <container-name>
   
   # Check MCP Hub logs
   sudo journalctl -u mcp-hub.service -f
   
   # Test server manually
   docker run --rm mcp/server-image
   ```

2. **Environment Variables Not Loading**
   ```bash
   # Check .env file
   cat .env
   
   # Test environment loading
   python scripts/check_servers.py
   
   # Check environment in container
   docker exec <container-name> env
   ```

3. **Tools Not Discovered**
   ```bash
   # Check server status
   curl "http://localhost:8000/servers"
   
   # Check tools
   curl "http://localhost:8000/tools"
   
   # Restart server
   curl -X POST "http://localhost:8000/servers/server-name/stop"
   curl -X POST "http://localhost:8000/servers/server-name/start"
   ```

4. **Permission Issues**
   ```bash
   # Check Docker permissions
   docker run hello-world
   
   # Add user to docker group
   sudo usermod -aG docker $USER
   newgrp docker
   ```

### Debug Commands

```bash
# Check all running containers
docker ps

# Check all containers (including stopped)
docker ps -a

# Check container logs
docker logs <container-name>

# Check container environment
docker exec <container-name> env

# Check container processes
docker exec <container-name> ps aux

# Test server connectivity
curl http://localhost:8080/health
```

## 📊 Monitoring and Health Checks

### Health Check Endpoints

```bash
# Overall hub health
curl "http://localhost:8000/"

# Server status
curl "http://localhost:8000/servers"

# Tool availability
curl "http://localhost:8000/tools"

# Server availability check
curl "http://localhost:8000/servers/check-availability"
```

### Log Monitoring

```bash
# MCP Hub logs
sudo journalctl -u mcp-hub.service -f

# Docker container logs
docker logs -f <container-name>

# Combined logs
docker-compose logs -f
```

## 🔒 Security Considerations

### Environment Variables

- Store sensitive data in `.env` files
- Never commit `.env` files to version control
- Use different keys for different environments
- Rotate API keys regularly

### Docker Security

- Use specific image tags (not `latest`)
- Run containers as non-root users
- Limit container capabilities
- Use read-only filesystems where possible

### Network Security

- Use internal networks for inter-container communication
- Expose only necessary ports
- Use HTTPS for external communication
- Implement rate limiting

## 📚 Examples

### Complete Server Configuration

```json
{
  "slack": {
    "docker_image": "mcp/slack:latest",
    "transport": "stdio",
    "env_vars": {
      "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
      "SLACK_TEAM_ID": "${SLACK_TEAM_ID}",
      "SLACK_CHANNEL_IDS": "${SLACK_CHANNEL_IDS}"
    },
    "description": "Slack integration for messaging and notifications",
    "health_check_timeout": 30
  },
  "brave-search": {
    "docker_image": "mcp/brave-search:latest",
    "transport": "http",
    "env_vars": {
      "BRAVE_API_KEY": "${BRAVE_API_KEY}"
    },
    "docker_ports": ["8080:8080"],
    "health_check_url": "http://localhost:8080/health",
    "health_check_timeout": 30,
    "description": "Brave Search for web queries"
  }
}
```

### API Usage Examples

```bash
# Add multiple servers
curl -X POST "http://localhost:8000/servers/add-docker" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "slack",
    "docker_image": "mcp/slack",
    "transport": "stdio",
    "env_vars": {"SLACK_BOT_TOKEN": "xoxb-..."}
  }'

curl -X POST "http://localhost:8000/servers/add-docker" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "brave",
    "docker_image": "mcp/brave-search",
    "transport": "http",
    "env_vars": {"BRAVE_API_KEY": "..."},
    "ports": ["8080:8080"]
  }'

# Start all servers
curl -X POST "http://localhost:8000/servers/start-all"

# Check results
curl "http://localhost:8000/servers"
curl "http://localhost:8000/tools"
```

This dynamic server management system allows you to easily add, remove, and configure MCP servers without modifying code or restarting the entire hub! 