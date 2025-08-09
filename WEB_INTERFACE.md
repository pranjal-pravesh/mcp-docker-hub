# 🌐 MCP Hub Web Interface

A beautiful, modern web interface for managing your MCP Hub servers and tools.

## 🚀 Access

Once your MCP Hub is running, access the web interface at:

```
http://your-server-ip:8000/
```

## ✨ Features

### 📡 Server Management
- **Real-time Status**: See which servers are running, stopped, or in error state
- **Individual Control**: Start/stop individual servers with one click
- **Bulk Operations**: Start all or stop all servers at once
- **Configuration Loading**: Load server configurations from JSON files
- **Availability Check**: See which servers can be started based on environment variables

### 🛠️ Tool Management
- **Tool Discovery**: Browse all available tools from all servers
- **Search & Filter**: Find tools by name, description, or server
- **Tool Details**: Click any tool to see detailed information including input schemas
- **Server Filtering**: Filter tools by specific server

### 📊 Dashboard
- **Live Statistics**: See configured servers, available servers, and total tools
- **Connection Status**: Real-time connection indicator
- **Auto-refresh**: Interface updates automatically every 30 seconds

## 🎨 Interface Sections

### 1. Header
- **Connection Status**: Shows if the interface is connected to the MCP Hub
- **Refresh Button**: Manually refresh all data

### 2. Server Management
- **Control Buttons**: Start All, Stop All, Load Config, Check Available
- **Server Cards**: Each server shows:
  - Name and status
  - Transport type and tool count
  - Docker image (if applicable)
  - Start/Stop button

### 3. Tools Section
- **Filter Controls**: Dropdown to filter by server, search box for tool names
- **Tool Cards**: Each tool shows:
  - Tool name and server
  - Description
  - Click to see detailed information

### 4. Configuration Info
- **Statistics**: Configured servers, available servers, total tools

## 🎯 Quick Actions

### Start All Servers
```bash
# Via Web Interface
Click "▶️ Start All" button

# Via API
curl -X POST http://your-server:8000/servers/start-all
```

### Stop All Servers
```bash
# Via Web Interface
Click "⏹️ Stop All" button

# Via API
curl -X POST http://your-server:8000/servers/stop-all
```

### Load Configuration
```bash
# Via Web Interface
Click "📂 Load Config" button

# Via API
curl -X POST http://your-server:8000/servers/load-config
```

### Check Server Availability
```bash
# Via Web Interface
Click "🔍 Check Available" button

# Via API
curl -X GET http://your-server:8000/servers/check-availability
```

## 🔧 Technical Details

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients, shadows, and animations
- **JavaScript**: Vanilla JS with async/await for API calls
- **Responsive**: Works on desktop, tablet, and mobile

### Backend Integration
- **RESTful API**: Uses existing FastAPI endpoints
- **Real-time Updates**: Auto-refreshes every 30 seconds
- **Error Handling**: Graceful error messages and notifications
- **CORS Enabled**: Can be accessed from any domain

### File Structure
```
src/mcp_hub/static/
├── index.html      # Main interface
├── styles.css      # Styling
└── script.js       # Functionality
```

## 🎨 Design Features

### Modern UI
- **Glassmorphism**: Translucent cards with backdrop blur
- **Gradient Background**: Beautiful purple-blue gradient
- **Smooth Animations**: Hover effects and transitions
- **Color-coded Status**: Green for running, red for stopped, yellow for errors

### User Experience
- **Intuitive Layout**: Clear sections and logical flow
- **Visual Feedback**: Loading states and success/error notifications
- **Keyboard Accessible**: Can be navigated with keyboard
- **Mobile Friendly**: Responsive design for all screen sizes

## 🔒 Security Notes

- The interface connects to your MCP Hub API
- No authentication is required (same as the API)
- Consider setting up HTTPS for production use
- You can restrict access by firewall rules

## 🚀 Getting Started

1. **Start your MCP Hub**:
   ```bash
   python -m mcp_hub.mcp_hub_server --load-config
   ```

2. **Open your browser** and go to:
   ```
   http://your-server-ip:8000/
   ```

3. **Start managing your servers**:
   - Click "Load Config" to load your server configurations
   - Click "Start All" to start all available servers
   - Browse and search through your tools

## 🎉 That's it!

You now have a beautiful, functional web interface for managing your MCP Hub. No additional setup required - it's all built into your existing MCP Hub installation!

