# 🚀 MCP Hub Web Management Console

A sophisticated web-based interface for managing Docker MCP servers and tools with granular control over what gets exposed to clients.

## 🌐 Access the Interface

Once your MCP Hub is running, access the web interface at:

```
http://localhost:8000/
```

## ✨ Key Features

### 🎯 **Precision Server Management**
- **View All Available Servers**: See all configured servers from your `mcp_servers.json`
- **Selective Server Control**: Use checkboxes to select which servers to start
- **Individual Server Actions**: Start/stop individual servers or all at once
- **Real-time Status**: Live status indicators showing active/inactive servers
- **Server Configuration**: View detailed configuration for each server

### 🛠️ **Granular Tool Control**
- **Tool Visibility Management**: Enable/disable specific tools via checkboxes
- **Tool Filtering**: Search tools by name or filter by server
- **Bulk Operations**: Enable/disable all tools with single clicks
- **Tool Details**: Click any tool to see detailed information and input schemas
- **Persistent Configuration**: Tool settings are saved and restored on restart

### 📊 **Real-time Dashboard**
- **Active Servers Count**: Live count of running servers
- **Total Tools Available**: Count of all discovered tools
- **Enabled Tools Count**: Count of currently enabled tools
- **API Connection Status**: Real-time connection indicator

### 🔧 **Configuration Management**
- **Load Server Config**: Load servers from `mcp_servers.json`
- **Check Availability**: Verify which servers can be started based on environment variables
- **Save Tool Config**: Persist tool enable/disable settings
- **Configuration Info**: View API base URL, server counts, and last update time

## 🎨 Interface Sections

### 1. **Server Management Section**
```
📡 Server Management
├── Load Config          # Load servers from config file
├── Check Availability   # Check which servers can start
├── Start Selected       # Start only selected servers
└── Stop All            # Stop all running servers
```

**Server Cards Show:**
- ✅ Checkbox for selection
- 🟢 Status indicator (active/inactive)
- 📊 Tool count
- 🚀 Transport type
- ⚡ Action buttons (Start/Stop/Config)

### 2. **Tool Management Section**
```
🛠️ Tool Management
├── Refresh Tools        # Reload tool list
├── Enable All          # Enable all tools
├── Disable All         # Disable all tools
└── Save Config         # Save current tool settings
```

**Tool Cards Show:**
- ✅ Checkbox for enable/disable
- 🏷️ Tool name and description
- 🖥️ Server name
- 🎨 Visual state (enabled/disabled)

### 3. **Status Dashboard**
```
📊 Status Dashboard
├── Active Servers      # Count of running servers
├── Total Tools         # Count of all available tools
├── Enabled Tools       # Count of enabled tools
└── API Status          # Connection status
```

### 4. **Configuration Info**
```
⚙️ Configuration
├── API Base URL        # Current API endpoint
├── Available Servers   # Count of configured servers
└── Last Updated        # Timestamp of last update
```

## 🎯 **Workflow Examples**

### **Starting Specific Servers**
1. Click **"Load Config"** to load server configurations
2. Click **"Check Availability"** to see which servers can start
3. ✅ Check the boxes for servers you want to start
4. Click **"Start Selected"** to start only those servers
5. Watch the status indicators turn green as servers start

### **Managing Tool Visibility**
1. Click **"Refresh Tools"** to load available tools
2. ✅ Check/uncheck tool boxes to enable/disable them
3. Use search and filters to find specific tools
4. Click **"Save Config"** to persist your settings
5. Only enabled tools will be exposed to API clients

### **Bulk Operations**
- **Enable All Tools**: Click "Enable All" to enable every tool
- **Disable All Tools**: Click "Disable All" to disable every tool
- **Start All Servers**: Select all servers and click "Start Selected"
- **Stop All Servers**: Click "Stop All" to stop everything

## 🔍 **Search and Filtering**

### **Tool Search**
- Type in the search box to filter tools by name
- Real-time filtering as you type
- Case-insensitive search

### **Server Filtering**
- Use the dropdown to filter tools by server
- Select "All Servers" to see all tools
- Combine with search for precise filtering

## 💾 **Configuration Persistence**

### **Tool Configuration**
- Tool enable/disable settings are saved to `configs/tool_config.json`
- Settings persist across server restarts
- Configuration is loaded automatically on page load

### **Server Configuration**
- Server settings are managed via `configs/mcp_servers.json`
- Environment variables control server availability
- Server status is real-time and not persisted

## 🔧 **API Integration**

The web interface integrates with these API endpoints:

- `GET /servers` - List all servers and their status
- `GET /servers/configured` - List configured servers
- `GET /servers/check-availability` - Check which servers can start
- `POST /servers/{name}/start` - Start a specific server
- `POST /servers/{name}/stop` - Stop a specific server
- `GET /tools` - List all available tools
- `POST /tools/save-config` - Save tool enable/disable settings
- `GET /tools/config` - Load saved tool configuration

## 🎨 **Design Features**

### **Modern UI**
- Glassmorphism design with backdrop blur effects
- Gradient backgrounds and smooth animations
- Responsive design that works on all screen sizes
- Color-coded status indicators

### **Interactive Elements**
- Hover effects on cards and buttons
- Smooth transitions and animations
- Real-time status updates
- Toast notifications for user feedback

### **Accessibility**
- High contrast colors for status indicators
- Clear visual hierarchy
- Intuitive checkbox controls
- Responsive touch targets

## 🚀 **Quick Start**

1. **Start the MCP Hub**:
   ```bash
   python -m mcp_hub.mcp_hub_server --load-config
   ```

2. **Open the Web Interface**:
   ```
   http://localhost:8000/
   ```

3. **Load Your Configuration**:
   - Click "Load Config" to load server definitions
   - Click "Check Availability" to see what can start

4. **Start Your Servers**:
   - Select servers you want to start
   - Click "Start Selected"

5. **Manage Your Tools**:
   - Click "Refresh Tools" to see available tools
   - Enable/disable tools as needed
   - Click "Save Config" to persist settings

## 🎯 **Use Cases**

### **Development Environment**
- Quickly start only the servers you need
- Disable tools you're not testing
- Real-time monitoring of server status

### **Production Deployment**
- Selective server startup based on requirements
- Granular control over exposed tools
- Persistent configuration management

### **Client Management**
- Control exactly which tools are available to clients
- Enable/disable tools without restarting servers
- Monitor tool usage and availability

## 🔒 **Security Considerations**

- The web interface is designed for internal management
- Consider adding authentication for production use
- Tool enable/disable affects what's exposed to API clients
- Server configurations are read from trusted JSON files

---

**🎉 You now have a powerful, intuitive web interface for managing your MCP Hub with precision control over servers and tools!**

