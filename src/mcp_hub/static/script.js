// Global variables
let servers = [];
let tools = [];
let configuredServers = [];
let availableServers = [];

// API base URL
const API_BASE = window.location.origin;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeModal();
    refreshAll();
    
    // Auto-refresh every 30 seconds
    setInterval(refreshAll, 30000);
});

// Modal functionality
function initializeModal() {
    const modal = document.getElementById('tool-modal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
}

// Main refresh function
async function refreshAll() {
    try {
        updateConnectionStatus('connecting');
        
        // Load all data in parallel
        const [serversData, toolsData, configuredData, availableData] = await Promise.all([
            fetchServers(),
            fetchTools(),
            fetchConfiguredServers(),
            fetchAvailableServers()
        ]);
        
        servers = serversData;
        tools = toolsData;
        configuredServers = configuredData;
        availableServers = availableData;
        
        // Update UI
        renderServers();
        renderTools();
        updateConfigurationInfo();
        updateConnectionStatus('connected');
        
    } catch (error) {
        console.error('Error refreshing data:', error);
        updateConnectionStatus('disconnected');
    }
}

// API Functions
async function fetchServers() {
    const response = await fetch(`${API_BASE}/servers`);
    if (!response.ok) throw new Error('Failed to fetch servers');
    return await response.json();
}

async function fetchTools() {
    const response = await fetch(`${API_BASE}/tools`);
    if (!response.ok) throw new Error('Failed to fetch tools');
    return await response.json();
}

async function fetchConfiguredServers() {
    const response = await fetch(`${API_BASE}/servers/configured`);
    if (!response.ok) throw new Error('Failed to fetch configured servers');
    return await response.json();
}

async function fetchAvailableServers() {
    const response = await fetch(`${API_BASE}/servers/check-availability`);
    if (!response.ok) throw new Error('Failed to fetch available servers');
    return await response.json();
}

async function startServer(serverName) {
    const response = await fetch(`${API_BASE}/servers/${serverName}/start`, {
        method: 'POST'
    });
    if (!response.ok) throw new Error(`Failed to start server ${serverName}`);
    return await response.json();
}

async function stopServer(serverName) {
    const response = await fetch(`${API_BASE}/servers/${serverName}/stop`, {
        method: 'POST'
    });
    if (!response.ok) throw new Error(`Failed to stop server ${serverName}`);
    return await response.json();
}

async function startAllServers() {
    const response = await fetch(`${API_BASE}/servers/start-all`, {
        method: 'POST'
    });
    if (!response.ok) throw new Error('Failed to start all servers');
    return await response.json();
}

async function stopAllServers() {
    const response = await fetch(`${API_BASE}/servers/stop-all`, {
        method: 'POST'
    });
    if (!response.ok) throw new Error('Failed to stop all servers');
    return await response.json();
}

async function loadConfig() {
    const response = await fetch(`${API_BASE}/servers/load-config?config_file=configs/mcp_servers.json`, {
        method: 'POST'
    });
    if (!response.ok) throw new Error('Failed to load configuration');
    return await response.json();
}

async function getToolInfo(toolName) {
    const response = await fetch(`${API_BASE}/tools/info/${toolName}`);
    if (!response.ok) throw new Error(`Failed to fetch tool info for ${toolName}`);
    return await response.json();
}

// UI Functions
function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connection-status');
    statusElement.className = `status-indicator ${status}`;
    
    switch(status) {
        case 'connected':
            statusElement.textContent = '🟢 Connected';
            break;
        case 'disconnected':
            statusElement.textContent = '🔴 Disconnected';
            break;
        case 'connecting':
            statusElement.textContent = '🟡 Connecting...';
            break;
    }
}

function renderServers() {
    const serverGrid = document.getElementById('server-grid');
    serverGrid.innerHTML = '';
    
    if (servers.length === 0) {
        serverGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #6c757d;">No servers found</p>';
        return;
    }
    
    servers.forEach(server => {
        const serverCard = createServerCard(server);
        serverGrid.appendChild(serverCard);
    });
}

function createServerCard(server) {
    const card = document.createElement('div');
    card.className = `server-card ${server.status}`;
    
    const statusClass = server.status === 'running' ? 'running' : 
                       server.status === 'error' ? 'error' : 'stopped';
    
    card.innerHTML = `
        <div class="server-header">
            <div class="server-name">${server.name}</div>
            <div class="server-status ${statusClass}">${server.status}</div>
        </div>
        <div class="server-info">
            <div><strong>Transport:</strong> ${server.transport || 'N/A'}</div>
            <div><strong>Tools:</strong> ${server.tools_count || 0}</div>
            ${server.docker_image ? `<div><strong>Image:</strong> ${server.docker_image}</div>` : ''}
        </div>
        <div class="server-actions">
            ${server.status === 'running' ? 
                `<button class="btn btn-danger btn-small" onclick="stopServerAction('${server.name}')">⏹️ Stop</button>` :
                `<button class="btn btn-success btn-small" onclick="startServerAction('${server.name}')">▶️ Start</button>`
            }
        </div>
    `;
    
    return card;
}

function renderTools() {
    const toolsGrid = document.getElementById('tools-grid');
    const serverFilter = document.getElementById('server-filter');
    
    // Update server filter options
    const servers = [...new Set(tools.map(tool => tool.server))];
    serverFilter.innerHTML = '<option value="">All Servers</option>';
    servers.forEach(server => {
        const option = document.createElement('option');
        option.value = server;
        option.textContent = server;
        serverFilter.appendChild(option);
    });
    
    // Filter and render tools
    filterTools();
}

function filterTools() {
    const toolsGrid = document.getElementById('tools-grid');
    const serverFilter = document.getElementById('server-filter');
    const toolSearch = document.getElementById('tool-search');
    
    const selectedServer = serverFilter.value;
    const searchTerm = toolSearch.value.toLowerCase();
    
    const filteredTools = tools.filter(tool => {
        const serverMatch = !selectedServer || tool.server === selectedServer;
        const searchMatch = !searchTerm || 
            tool.name.toLowerCase().includes(searchTerm) ||
            tool.description.toLowerCase().includes(searchTerm);
        return serverMatch && searchMatch;
    });
    
    toolsGrid.innerHTML = '';
    
    if (filteredTools.length === 0) {
        toolsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #6c757d;">No tools found</p>';
        return;
    }
    
    filteredTools.forEach(tool => {
        const toolCard = createToolCard(tool);
        toolsGrid.appendChild(toolCard);
    });
}

function createToolCard(tool) {
    const card = document.createElement('div');
    card.className = 'tool-card';
    card.onclick = () => showToolDetails(tool);
    
    card.innerHTML = `
        <div class="tool-name">${tool.name}</div>
        <div class="tool-server">${tool.server}</div>
        <div class="tool-description">${tool.description || 'No description available'}</div>
    `;
    
    return card;
}

function updateConfigurationInfo() {
    document.getElementById('configured-count').textContent = configuredServers.length;
    document.getElementById('available-count').textContent = availableServers.length;
    document.getElementById('total-tools').textContent = tools.length;
}

// Action Functions
async function startServerAction(serverName) {
    try {
        await startServer(serverName);
        showNotification(`Started server: ${serverName}`, 'success');
        setTimeout(refreshAll, 1000);
    } catch (error) {
        showNotification(`Failed to start server: ${error.message}`, 'error');
    }
}

async function stopServerAction(serverName) {
    try {
        await stopServer(serverName);
        showNotification(`Stopped server: ${serverName}`, 'success');
        setTimeout(refreshAll, 1000);
    } catch (error) {
        showNotification(`Failed to stop server: ${error.message}`, 'error');
    }
}

async function startAllServers() {
    try {
        await startAllServers();
        showNotification('Started all servers', 'success');
        setTimeout(refreshAll, 1000);
    } catch (error) {
        showNotification(`Failed to start all servers: ${error.message}`, 'error');
    }
}

async function stopAllServers() {
    try {
        await stopAllServers();
        showNotification('Stopped all servers', 'success');
        setTimeout(refreshAll, 1000);
    } catch (error) {
        showNotification(`Failed to stop all servers: ${error.message}`, 'error');
    }
}

async function loadConfig() {
    try {
        await loadConfig();
        showNotification('Configuration loaded successfully', 'success');
        setTimeout(refreshAll, 1000);
    } catch (error) {
        showNotification(`Failed to load configuration: ${error.message}`, 'error');
    }
}

async function checkAvailability() {
    try {
        await refreshAll();
        showNotification('Availability check completed', 'success');
    } catch (error) {
        showNotification(`Failed to check availability: ${error.message}`, 'error');
    }
}

async function showToolDetails(tool) {
    try {
        const toolInfo = await getToolInfo(tool.name);
        const modal = document.getElementById('tool-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        
        modalTitle.textContent = tool.name;
        modalBody.innerHTML = `
            <div style="margin-bottom: 15px;">
                <strong>Server:</strong> ${tool.server}
            </div>
            <div style="margin-bottom: 15px;">
                <strong>Description:</strong> ${tool.description || 'No description available'}
            </div>
            ${toolInfo.inputSchema ? `
                <div style="margin-bottom: 15px;">
                    <strong>Input Schema:</strong>
                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 5px; font-size: 0.9rem; overflow-x: auto;">${JSON.stringify(toolInfo.inputSchema, null, 2)}</pre>
                </div>
            ` : ''}
        `;
        
        modal.style.display = 'block';
    } catch (error) {
        showNotification(`Failed to load tool details: ${error.message}`, 'error');
    }
}

// Utility Functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        max-width: 300px;
        word-wrap: break-word;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Set background color based on type
    switch(type) {
        case 'success':
            notification.style.background = '#28a745';
            break;
        case 'error':
            notification.style.background = '#dc3545';
            break;
        case 'warning':
            notification.style.background = '#ffc107';
            notification.style.color = '#212529';
            break;
        default:
            notification.style.background = '#17a2b8';
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

