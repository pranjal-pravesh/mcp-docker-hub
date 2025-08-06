# MCP Hub Server

A centralized hub server that provides a unified HTTP API for all MCP (Model Context Protocol) tools. This allows external clients to discover and call tools from multiple MCP servers through a single interface.

## 📁 Project Structure

```
mcp-hub/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── Makefile                     # Development tasks
├── env.example                  # Environment variables template
├── src/                         # Source code
│   └── mcp_hub/                # Main package
│       ├── __init__.py         # Package initialization
│       ├── mcp_hub_server.py   # FastAPI server implementation
│       ├── mcp_manager.py      # MCP server management
│       ├── mcp_cli.py          # Command-line interface
│       └── tool_adapter.py     # Unified tool interface
├── scripts/                     # Executable scripts
│   ├── run_hub.py              # Main server runner
│   └── start.sh                # Quick startup script
├── tests/                       # Test files
│   ├── test_mcp_hub.py         # Test suite
│   └── mcp_hub_client.py       # Example client
├── docs/                        # Documentation
│   └── DEPLOYMENT_GUIDE.md     # Detailed deployment guide
├── deployment/                  # Deployment configurations
│   ├── Dockerfile              # Production Docker container
│   ├── docker-compose.yml      # Local deployment with monitoring
│   ├── railway.json            # Railway cloud deployment
│   ├── render.yaml             # Render cloud deployment
│   └── deploy.sh               # Automated deployment script
└── configs/                     # Configuration files (future use)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- Node.js and npm (for some MCP servers)

### Local Development

1. **Clone and setup:**
```bash
git clone <your-repo-url>
cd mcp-hub
```

2. **Setup environment:**
```bash
# Install dependencies and setup environment
make setup

# Or manually:
pip install -r requirements.txt
pip install -e .
cp env.example .env
# Edit .env with your API keys
```

3. **Start development server:**
```bash
# Using Makefile
make dev

# Or using the startup script
./scripts/start.sh

# Or manually
python scripts/run_hub.py --dev --add-all-servers
```

### Docker Deployment

```bash
# Local Docker deployment
make deploy-local

# Or manually
./deployment/deploy.sh local
```

### Cloud Deployment

```bash
# Railway (recommended)
./deployment/deploy.sh railway

# Render
./deployment/deploy.sh render
```

## 🔧 Core Components

### `src/mcp_hub/mcp_hub_server.py`
- FastAPI-based HTTP server
- Unified API for all MCP tools
- Auto-generated documentation
- Health checks and monitoring

### `src/mcp_hub/mcp_manager.py`
- Manages MCP server connections
- Handles different transport protocols (stdio, HTTP, SSE)
- Server lifecycle management
- Tool discovery

### `src/mcp_hub/tool_adapter.py`
- Unified interface for all MCP protocols
- Transparent tool calling
- Protocol abstraction layer

### `src/mcp_hub/mcp_cli.py`
- Interactive command-line interface
- Server management commands
- Tool testing and debugging

## 📋 API Endpoints

- `GET /` - Server status and health
- `GET /servers` - List all MCP servers
- `GET /tools` - List all available tools
- `GET /tools/{server}` - List tools from specific server
- `GET /tools/info/{tool}` - Get tool details
- `POST /tools/call` - Call a tool
- `POST /servers/{name}/start` - Start a server
- `POST /servers/{name}/stop` - Stop a server
- `POST /servers/start-all` - Start all servers
- `POST /servers/stop-all` - Stop all servers

## 🛠️ Usage Examples

### Python Client

```python
import asyncio
import aiohttp

async def use_mcp_hub():
    async with aiohttp.ClientSession() as session:
        # List all tools
        async with session.get("http://localhost:8000/tools") as response:
            tools = await response.json()
            print(f"Available tools: {len(tools)}")
        
        # Call a tool
        payload = {
            "tool_name": "query-wolfram-alpha",
            "arguments": {"query": "solve x^2 + 5x + 6 = 0"}
        }
        async with session.post("http://localhost:8000/tools/call", json=payload) as response:
            result = await response.json()
            print(f"Result: {result}")

asyncio.run(use_mcp_hub())
```

### Command Line

```bash
# Start hub server
python scripts/run_hub.py --add-all-servers

# Test with client
python tests/mcp_hub_client.py --demo

# Run tests
python tests/test_mcp_hub.py --offline
```

## 🔒 Security

- Environment variable management for API keys
- Non-root Docker containers
- Health checks and monitoring
- Rate limiting ready
- Authentication ready for production

## 📊 Monitoring

- Health check endpoints
- Prometheus metrics (optional)
- Grafana dashboards (optional)
- Structured logging
- Performance monitoring

## 🌐 Deployment

### Local
```bash
make deploy-local
```

### Railway (Recommended)
```bash
./deployment/deploy.sh railway
```

### Render
```bash
./deployment/deploy.sh render
```

### Custom
See `docs/DEPLOYMENT_GUIDE.md` for detailed instructions.

## 🔄 Development

### Available Commands

```bash
make help          # Show all available commands
make setup         # Initial setup
make dev           # Start development server
make test          # Run offline tests
make test-online   # Run online tests
make clean         # Clean up cache files
make deploy-local  # Deploy locally with Docker
```

### Adding New MCP Servers

1. Add server configuration to `src/mcp_hub/mcp_manager.py`
2. Add API endpoints to `src/mcp_hub/mcp_hub_server.py`
3. Update deployment configurations if needed

### Testing

```bash
# Run offline tests
make test

# Run online tests (requires running server)
make test-online

# Test client
python tests/mcp_hub_client.py --demo
```

## 📚 Documentation

- **API Docs**: Available at `/docs` when server is running
- **Deployment Guide**: `docs/DEPLOYMENT_GUIDE.md`
- **Examples**: `tests/` directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- Check the deployment guide for troubleshooting
- Review API documentation at `/docs`
- Check server logs for detailed error messages
- Test with the provided examples

---

**Your MCP Hub Server is now organized and ready for production use!** 🎉 