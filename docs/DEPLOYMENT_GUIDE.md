# MCP Hub Server Deployment Guide

This guide covers deploying the MCP Hub Server to various cloud platforms with Docker support for production use.

## 🚀 Quick Deploy Options

### 1. Railway (Recommended for Quick Start)
- **Pros**: Easy deployment, automatic HTTPS, good free tier
- **Cons**: Limited resources on free tier
- **Best for**: Development, testing, small production workloads

### 2. Render
- **Pros**: Good free tier, automatic HTTPS, easy setup
- **Cons**: Cold starts on free tier
- **Best for**: Small to medium production workloads

### 3. DigitalOcean App Platform
- **Pros**: Reliable, good performance, reasonable pricing
- **Cons**: No free tier
- **Best for**: Production workloads

### 4. AWS/GCP/Azure
- **Pros**: Full control, scalable, enterprise features
- **Cons**: More complex setup, higher cost
- **Best for**: Large scale production, enterprise use

## 📋 Prerequisites

### Required Accounts
- GitHub account (for code hosting)
- Cloud platform account (Railway, Render, etc.)
- Docker Hub account (optional, for custom images)

### Required Tools
- Docker installed locally
- Git
- API keys for MCP services (Slack, Brave Search, Wolfram Alpha)

## 🐳 Docker Deployment

### Local Docker Setup

1. **Create Dockerfile**
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY run_mcp_hub.py .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start the application
CMD ["python", "run_mcp_hub.py", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Create docker-compose.yml**
```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-hub:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
      - SLACK_TEAM_ID=${SLACK_TEAM_ID}
      - SLACK_CHANNEL_IDS=${SLACK_CHANNEL_IDS}
      - BRAVE_API_KEY=${BRAVE_API_KEY}
      - WOLFRAM_API_KEY=${WOLFRAM_API_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Add Redis for session management
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

3. **Build and Run Locally**
```bash
# Build the image
docker build -t mcp-hub-server .

# Run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f mcp-hub
```

## ☁️ Cloud Deployment

### Railway Deployment

1. **Prepare Your Repository**
```bash
# Add Railway configuration
mkdir .railway
```

2. **Create railway.json**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "python run_mcp_hub.py --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

3. **Deploy to Railway**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Add environment variables
railway variables set SLACK_BOT_TOKEN=your_token
railway variables set SLACK_TEAM_ID=your_team_id
railway variables set BRAVE_API_KEY=your_key
railway variables set WOLFRAM_API_KEY=your_key

# Deploy
railway up
```

### Render Deployment

1. **Create render.yaml**
```yaml
services:
  - type: web
    name: mcp-hub-server
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python run_mcp_hub.py --host 0.0.0.0 --port $PORT
    healthCheckPath: /
    envVars:
      - key: SLACK_BOT_TOKEN
        sync: false
      - key: SLACK_TEAM_ID
        sync: false
      - key: BRAVE_API_KEY
        sync: false
      - key: WOLFRAM_API_KEY
        sync: false
```

2. **Deploy to Render**
- Connect your GitHub repository
- Set environment variables in Render dashboard
- Deploy automatically on push

### DigitalOcean App Platform

1. **Create app.yaml**
```yaml
name: mcp-hub-server
services:
  - name: web
    source_dir: /
    github:
      repo: your-username/your-repo
      branch: main
    run_command: python run_mcp_hub.py --host 0.0.0.0 --port $PORT
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
    health_check:
      http_path: /
    envs:
      - key: SLACK_BOT_TOKEN
        scope: RUN_AND_BUILD_TIME
        value: ${SLACK_BOT_TOKEN}
      - key: SLACK_TEAM_ID
        scope: RUN_AND_BUILD_TIME
        value: ${SLACK_TEAM_ID}
      - key: BRAVE_API_KEY
        scope: RUN_AND_BUILD_TIME
        value: ${BRAVE_API_KEY}
      - key: WOLFRAM_API_KEY
        scope: RUN_AND_BUILD_TIME
        value: ${WOLFRAM_API_KEY}
```

### AWS ECS Deployment

1. **Create task-definition.json**
```json
{
  "family": "mcp-hub-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::your-account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "mcp-hub",
      "image": "your-account/mcp-hub-server:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "SLACK_BOT_TOKEN",
          "value": "your-token"
        },
        {
          "name": "SLACK_TEAM_ID",
          "value": "your-team-id"
        },
        {
          "name": "BRAVE_API_KEY",
          "value": "your-key"
        },
        {
          "name": "WOLFRAM_API_KEY",
          "value": "your-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mcp-hub-server",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

2. **Deploy to ECS**
```bash
# Build and push Docker image
docker build -t mcp-hub-server .
docker tag mcp-hub-server:latest your-account/mcp-hub-server:latest
docker push your-account/mcp-hub-server:latest

# Create ECS cluster and service
aws ecs create-cluster --cluster-name mcp-hub-cluster
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs create-service --cluster mcp-hub-cluster --service-name mcp-hub-service --task-definition mcp-hub-server:1 --desired-count 1
```

## 🔒 Security Considerations

### Environment Variables
- Never commit API keys to version control
- Use platform-specific secret management
- Rotate keys regularly

### Network Security
```python
# Add to mcp_hub_server.py for production
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return credentials.credentials

# Add to your endpoints
@app.get("/tools")
async def list_tools(token: str = Depends(verify_token)):
    # Your code here
    pass
```

### Rate Limiting
```python
# Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/tools")
@limiter.limit("10/minute")
async def list_tools(request: Request):
    # Your code here
    pass
```

## 📊 Monitoring and Logging

### Health Checks
```python
# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "uptime": time.time() - start_time,
        "servers": len(mcp_manager.active_connections),
        "tools": len(tool_hub.tool_registry)
    }
```

### Logging Configuration
```python
# Add to mcp_hub_server.py
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/mcp_hub.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### Metrics (Optional)
```python
# Add Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
tool_calls_total = Counter('tool_calls_total', 'Total tool calls', ['tool_name', 'server_name'])
tool_call_duration = Histogram('tool_call_duration_seconds', 'Tool call duration', ['tool_name'])

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 🔧 Production Optimizations

### Performance Tuning
```python
# Add connection pooling
import asyncio
import aiohttp

# Configure connection limits
connector = aiohttp.TCPConnector(
    limit=100,
    limit_per_host=30,
    ttl_dns_cache=300,
    use_dns_cache=True
)

# Use in your HTTP clients
async with aiohttp.ClientSession(connector=connector) as session:
    # Your HTTP requests
    pass
```

### Caching
```python
# Add Redis caching
import redis.asyncio as redis

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.get("/tools")
async def list_tools():
    # Try cache first
    cached = await redis_client.get("tools_list")
    if cached:
        return json.loads(cached)
    
    # Get fresh data
    tools = get_all_tools()
    
    # Cache for 5 minutes
    await redis_client.setex("tools_list", 300, json.dumps(tools))
    return tools
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All API keys configured
- [ ] Environment variables set
- [ ] Docker image built and tested
- [ ] Health checks implemented
- [ ] Logging configured
- [ ] Security measures in place

### Post-Deployment
- [ ] Health check endpoint responding
- [ ] All MCP servers starting correctly
- [ ] Tools being discovered
- [ ] API documentation accessible
- [ ] Monitoring alerts configured
- [ ] Backup strategy in place

## 🔗 Example Deployments

### Railway (Easiest)
```bash
# 1. Fork/clone your repository
git clone https://github.com/your-username/your-repo
cd your-repo

# 2. Add Railway configuration files
# (railway.json and Dockerfile as shown above)

# 3. Push to GitHub
git add .
git commit -m "Add Railway deployment config"
git push

# 4. Deploy on Railway
railway login
railway init
railway up
```

### Render (Alternative)
```bash
# 1. Connect GitHub repository to Render
# 2. Add render.yaml configuration
# 3. Set environment variables in Render dashboard
# 4. Deploy automatically
```

## 📞 Support

For deployment issues:
1. Check platform-specific logs
2. Verify environment variables
3. Test locally with Docker first
4. Check health check endpoints
5. Review platform documentation

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Railway
        uses: railway/deploy@v1
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
```

This deployment guide covers all major cloud platforms and provides production-ready configurations for hosting your MCP Hub Server on the internet! 