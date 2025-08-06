# Dynamic Docker MCP Server Management

This document explains how to effortlessly add and remove any Docker MCP server with minimal configuration changes.

## Overview

The MCP Hub now supports dynamic management of Docker MCP servers through:
- **JSON Configuration Files**: Easy server configuration management
- **REST API Endpoints**: Programmatic server management
- **CLI Tool**: Command-line server management
- **Environment Variable Substitution**: Automatic configuration from `.env` files

## Quick Start

### 1. Using the CLI Tool (Recommended)

The easiest way to manage Docker MCP servers is using the CLI tool:

```bash
# Add a new server
python scripts/manage_mcp_servers.py add my-slack mcp/slack --env-vars SLACK_BOT_TOKEN SLACK_TEAM_ID

# Add a server with HTTP transport
python scripts/manage_mcp_servers.py add brave mcp/brave-search --transport http --ports 8080:8080 --health-check-url http://localhost:8080/

# List all servers
python scripts/manage_mcp_servers.py list

# Remove a server
python scripts/manage_mcp_servers.py remove my-slack

# Show server details
python scripts/manage_mcp_servers.py show my-slack
```

### 2. Using JSON Configuration

Edit `configs/mcp_servers.json` to add or remove servers:

```json
{
  "servers": {
    "my-custom-server": {
      "docker_image": "mcp/my-custom-server",
      "transport": "stdio",
      "env_vars": {
        "API_KEY": "${MY_API_KEY}",
        "CUSTOM_SETTING": "value"
      },
      "description": "My custom MCP server"
    }
  }
}
```

### 3. Using the REST API

```bash
# Add a server via API
curl -X POST "http://localhost:8000/servers/add-docker" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-server",
    "docker_image": "mcp/slack",
    "transport": "stdio",
    "env_vars": {"SLACK_BOT_TOKEN": "xoxb-..."}
  }'

# Load configuration from file
curl -X POST "http://localhost:8000/servers/load-config"

# Remove a server
curl -X DELETE "http://localhost:8000/servers/my-server"
```

## Configuration Options

### Server Configuration Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `docker_image` | string | Docker image name | `"mcp/slack"` |
| `transport` | string | Transport type | `"stdio"`, `"http"`, `"sse"` |
| `env_vars` | object | Environment variables | `{"API_KEY": "${API_KEY}"}` |
| `ports` | array | Port mappings | `["8080:8080"]` |
| `volumes` | array | Volume mappings | `["/host:/container"]` |
| `health_check_url` | string | Health check URL | `"http://localhost:8080/"` |
| `health_check_timeout` | integer | Health check timeout | `30` |
| `description` | string | Server description | `"Slack integration"` |

### Transport Types

#### stdio (Default)
- Uses standard input/output for communication
- Best for most MCP servers
- No port configuration needed

```json
{
  "docker_image": "mcp/slack",
  "transport": "stdio",
  "env_vars": {"SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"}
}
```

#### http
- Uses HTTP for communication
- Requires port mapping and health check URL
- Good for servers that expose HTTP endpoints

```json
{
  "docker_image": "mcp/brave-search",
  "transport": "http",
  "ports": ["8080:8080"],
  "health_check_url": "http://localhost:8080/",
  "env_vars": {"BRAVE_API_KEY": "${BRAVE_API_KEY}"}
}
```

#### sse
- Uses Server-Sent Events for communication
- Requires port mapping
- Less common, used by specific servers

## Environment Variable Substitution

The system automatically substitutes environment variables in configuration:

```json
{
  "env_vars": {
    "API_KEY": "${MY_API_KEY}",
    "DATABASE_URL": "${POSTGRES_CONNECTION_STRING}",
    "CUSTOM_VALUE": "static_value"
  }
}
```

Variables with `${VAR_NAME}` syntax are replaced with values from your `.env` file.

## Starting the Hub with Configuration

### Load Configuration on Startup

```bash
# Start hub and load all servers from config
python -m mcp_hub.mcp_hub_server --load-config

# Use custom config file
python -m mcp_hub.mcp_hub_server --load-config --config-file my_config.json
```

### Legacy Mode

```bash
# Start with legacy hardcoded servers
python -m mcp_hub.mcp_hub_server --add-all-servers
```

## API Endpoints

### Server Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/servers/add-docker` | Add a new Docker MCP server |
| `DELETE` | `/servers/{name}` | Remove a server |
| `GET` | `/servers/configured` | List configured servers |
| `GET` | `/servers/config/{name}` | Get server configuration |
| `POST` | `/servers/load-config` | Load from config file |
| `POST` | `/servers/save-config` | Save to config file |

### Server Control

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/servers/{name}/start` | Start a server |
| `POST` | `/servers/{name}/stop` | Stop a server |
| `POST` | `/servers/start-all` | Start all servers |
| `POST` | `/servers/stop-all` | Stop all servers |

## Examples

### Adding Common MCP Servers

#### Slack Integration
```bash
python scripts/manage_mcp_servers.py add slack mcp/slack \
  --env-vars SLACK_BOT_TOKEN SLACK_TEAM_ID SLACK_CHANNEL_IDS \
  --description "Slack integration for messaging"
```

#### GitHub Integration
```bash
python scripts/manage_mcp_servers.py add github mcp/github \
  --env-vars GITHUB_TOKEN \
  --description "GitHub repository management"
```

#### File System Operations
```bash
python scripts/manage_mcp_servers.py add filesystem mcp/file-system \
  --volumes "${PWD}:/workspace" \
  --description "File system operations"
```

#### Database Operations
```bash
python scripts/manage_mcp_servers.py add postgres mcp/postgres \
  --env-vars POSTGRES_CONNECTION_STRING \
  --description "PostgreSQL database operations"
```

### Advanced Configuration

#### Custom Docker Arguments
```json
{
  "servers": {
    "custom-server": {
      "docker_image": "my-custom-mcp:latest",
      "transport": "stdio",
      "env_vars": {"CUSTOM_VAR": "value"},
      "additional_args": ["--network", "host", "--privileged"]
    }
  }
}
```

#### Multiple Port Mappings
```json
{
  "servers": {
    "multi-port-server": {
      "docker_image": "mcp/multi-port",
      "transport": "http",
      "ports": ["8080:8080", "8081:8081"],
      "health_check_url": "http://localhost:8080/health"
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check environment variables are set in `.env`
   - Verify Docker image exists: `docker pull mcp/slack`
   - Check logs: `docker logs <container_name>`

2. **Configuration not loading**
   - Ensure JSON syntax is valid
   - Check file permissions
   - Verify environment variable names match `.env` file

3. **Port conflicts**
   - Use different host ports: `"8081:8080"`
   - Check if ports are already in use: `netstat -tulpn | grep 8080`

### Debug Mode

Enable debug logging to see detailed information:

```bash
export LOG_LEVEL=DEBUG
python -m mcp_hub.mcp_hub_server --load-config
```

## Best Practices

1. **Use descriptive names** for servers
2. **Group related servers** in separate config files
3. **Use environment variables** for sensitive data
4. **Test configurations** before production deployment
5. **Keep configurations** in version control
6. **Document custom servers** with descriptions

## Migration from Legacy System

If you're using the old hardcoded server methods:

1. **Export current configuration**:
   ```bash
   curl -X POST "http://localhost:8000/servers/save-config"
   ```

2. **Update your startup script**:
   ```bash
   # Old way
   python -m mcp_hub.mcp_hub_server --add-all-servers
   
   # New way
   python -m mcp_hub.mcp_hub_server --load-config
   ```

3. **Remove hardcoded server calls** from your code

The new system is backward compatible, so you can migrate gradually. 