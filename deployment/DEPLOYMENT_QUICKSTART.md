# MCP Hub Server - Quick Deployment Guide

## 🚀 Deploy in 5 Minutes

### Option 1: Railway (Easiest - Free Tier Available)

1. **Fork this repository** to your GitHub account

2. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

3. **Deploy:**
```bash
# Login to Railway
railway login

# Deploy your forked repository
railway init
railway up
```

4. **Set Environment Variables** in Railway dashboard:
- `SLACK_BOT_TOKEN`
- `SLACK_TEAM_ID` 
- `BRAVE_API_KEY`
- `WOLFRAM_API_KEY`

5. **Get your URL:**
```bash
railway domain
```

### Option 2: Render (Alternative - Free Tier Available)

1. **Connect your GitHub repository** to Render
2. **Add the `render.yaml`** file (already included)
3. **Set environment variables** in Render dashboard
4. **Deploy automatically** on push

### Option 3: Local Docker

1. **Create `.env` file:**
```bash
SLACK_BOT_TOKEN=your-token
SLACK_TEAM_ID=your-team-id
BRAVE_API_KEY=your-key
WOLFRAM_API_KEY=your-key
```

2. **Deploy:**
```bash
./deploy.sh local
```

3. **Access at:** http://localhost:8000

## 📋 What You Get

- ✅ **Unified API** for all MCP tools
- ✅ **Auto-generated docs** at `/docs`
- ✅ **Health monitoring** at `/`
- ✅ **Tool discovery** at `/tools`
- ✅ **Server management** at `/servers`

## 🔧 API Usage

Once deployed, your clients can:

```python
import aiohttp

async def use_mcp_hub():
    async with aiohttp.ClientSession() as session:
        # List all tools
        async with session.get("https://your-app.railway.app/tools") as response:
            tools = await response.json()
            print(f"Available tools: {len(tools)}")
        
        # Call a tool
        payload = {
            "tool_name": "query-wolfram-alpha",
            "arguments": {"query": "solve x^2 + 5x + 6 = 0"}
        }
        async with session.post("https://your-app.railway.app/tools/call", json=payload) as response:
            result = await response.json()
            print(f"Result: {result}")
```

## 🛠️ Management Commands

```bash
# Test deployment
./deploy.sh test

# View logs
./deploy.sh logs

# Stop deployment
./deploy.sh stop

# Build Docker image
./deploy.sh build
```

## 🔒 Security Notes

- Never commit API keys to Git
- Use platform secret management
- Consider adding authentication for production
- Monitor usage and set rate limits

## 📞 Support

- **Documentation**: `/docs` endpoint when running
- **Health Check**: `/` endpoint
- **Logs**: Platform-specific logging
- **Issues**: Check platform status pages

## 🎯 Next Steps

1. **Test your deployment** with the client example
2. **Add more MCP servers** as needed
3. **Implement authentication** for production
4. **Set up monitoring** and alerts
5. **Scale up** as your usage grows

Your MCP Hub Server is now ready to serve tools to clients worldwide! 🌍 