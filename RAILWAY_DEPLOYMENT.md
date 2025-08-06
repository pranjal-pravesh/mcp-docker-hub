# Railway Deployment Guide - MCP Hub Server

## 🚀 **Railway Deployment (Recommended)**

Railway is the easiest way to deploy your MCP Hub Server. No Docker installation needed!

### ✅ **Why Railway?**
- **Zero configuration** - Just connect your GitHub repo
- **Automatic Docker builds** - Railway handles everything
- **Free tier** - 500 hours/month free
- **Automatic HTTPS** - SSL certificates included
- **Easy environment variables** - Perfect for API keys

### 📋 **Prerequisites**
1. **GitHub account** with your MCP Hub Server repository
2. **Railway account** (free at railway.app)
3. **API keys** for your MCP servers (Slack, Brave, Wolfram)

### 🎯 **Step-by-Step Deployment**

#### **Step 1: Prepare Your Repository**
```bash
# Make sure your code is pushed to GitHub
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

#### **Step 2: Connect to Railway**
1. Go to [railway.app](https://railway.app)
2. Sign up/Login with your GitHub account
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your MCP Hub Server repository

#### **Step 3: Configure Environment Variables**
In Railway dashboard, go to your project → Variables tab and add:

```bash
# Required API Keys
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_TEAM_ID=your_slack_team_id_here
SLACK_CHANNEL_IDS=channel1,channel2

BRAVE_API_KEY=your_brave_api_key_here
WOLFRAM_APP_ID=your_wolfram_app_id_here

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8000
```

#### **Step 4: Deploy**
1. Railway will automatically detect the `deployment/railway.json` file
2. Click "Deploy" 
3. Wait for build to complete (usually 2-3 minutes)

#### **Step 5: Get Your URL**
1. Go to "Settings" tab in Railway
2. Copy your deployment URL (e.g., `https://your-app.railway.app`)
3. Your API will be available at:
   - **API**: `https://your-app.railway.app`
   - **Docs**: `https://your-app.railway.app/docs`
   - **Interactive**: `https://your-app.railway.app/redoc`

### 🔧 **Railway Configuration**

The project includes `deployment/railway.json` which tells Railway:
- Use the Dockerfile in `deployment/Dockerfile`
- Start command: `python scripts/run_hub.py --host 0.0.0.0 --port $PORT`
- Health check at `/` endpoint

### 🌐 **Using Your Deployed API**

Once deployed, you can use your MCP Hub Server from anywhere:

```python
import aiohttp

async def use_deployed_hub():
    url = "https://your-app.railway.app"
    
    async with aiohttp.ClientSession() as session:
        # Get all tools
        async with session.get(f"{url}/tools") as response:
            tools = await response.json()
            print(f"Available tools: {len(tools)}")
        
        # Call a tool
        payload = {
            "tool_name": "query-wolfram-alpha",
            "arguments": {"query": "solve x^2 + 5x + 6 = 0"}
        }
        async with session.post(f"{url}/tools/call", json=payload) as response:
            result = await response.json()
            print(f"Result: {result}")

# Run the function
import asyncio
asyncio.run(use_deployed_hub())
```

### 🔍 **Monitoring Your Deployment**

Railway provides:
- **Logs** - View real-time application logs
- **Metrics** - CPU, memory usage
- **Deployments** - View deployment history
- **Health checks** - Automatic monitoring

### 💰 **Costs**
- **Free tier**: 500 hours/month
- **Paid plans**: Start at $5/month for unlimited usage

### 🚨 **Troubleshooting**

**Common Issues:**
1. **Build fails**: Check Railway logs for dependency issues
2. **Environment variables**: Make sure all API keys are set
3. **Port issues**: Railway automatically sets `$PORT` environment variable

**Need help?**
- Check Railway logs in the dashboard
- Verify all environment variables are set
- Test locally first with `make dev`

---

**Your MCP Hub Server will be live on the internet in minutes!** 🌐 