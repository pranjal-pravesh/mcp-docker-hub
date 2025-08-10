// MCP Hub Management Console JavaScript
class MCPHubManager {
    constructor() {
        this.apiBase = window.location.origin;
        this.servers = new Map();
        this.tools = new Map();
        this.enabledTools = new Set();
        this.selectedServers = new Set();
        
        this.initializeEventListeners();
        this.loadInitialData();
    }

    initializeEventListeners() {
        // Server management buttons
        document.getElementById('loadConfigBtn').addEventListener('click', () => this.loadConfig());
        document.getElementById('checkAvailabilityBtn').addEventListener('click', () => this.checkAvailability());
        document.getElementById('selectAllBtn').addEventListener('click', () => this.selectAllServers());
        document.getElementById('startSelectedBtn').addEventListener('click', () => this.startSelectedServers());
        document.getElementById('stopSelectedBtn').addEventListener('click', () => this.stopSelectedServers());

        // Tool management buttons
        document.getElementById('refreshToolsBtn').addEventListener('click', () => this.refreshTools());
        document.getElementById('enableAllToolsBtn').addEventListener('click', () => this.enableAllTools());
        document.getElementById('disableAllToolsBtn').addEventListener('click', () => this.disableAllTools());
        document.getElementById('saveToolConfigBtn').addEventListener('click', () => this.saveToolConfig());

        // Status refresh
        document.getElementById('refreshStatusBtn').addEventListener('click', () => this.refreshStatus());

        // Search and filter
        document.getElementById('toolSearch').addEventListener('input', (e) => this.filterTools());
        document.getElementById('serverFilter').addEventListener('change', (e) => this.filterTools());

        // Modal
        const modal = document.getElementById('toolModal');
        const closeBtn = modal.querySelector('.close');
        closeBtn.addEventListener('click', () => this.closeModal());
        window.addEventListener('click', (e) => {
            if (e.target === modal) this.closeModal();
        });
    }

    selectAllServers() {
        // Get all server checkboxes
        const checkboxes = document.querySelectorAll('.server-checkbox');
        
        // Check all checkboxes and add to selected set
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
            const serverName = checkbox.closest('.server-card').dataset.serverName;
            this.selectedServers.add(serverName);
        });
        
        this.showNotification(`Selected ${this.selectedServers.size} servers`, 'info');
    }

    async loadInitialData() {
        // Load configuration first to create server cards
        await this.loadConfig();
        
        // Then refresh status to update server cards with correct status
        await this.refreshStatus();
        
        // Load tool configuration and refresh tools
        await this.loadToolConfig();
        await this.refreshTools();
        
        // Load other data
        await this.updateConfigurationInfo();
    }

    async loadConfig() {
        try {
            this.showNotification('Loading server configuration...', 'info');
            
            const response = await fetch(`${this.apiBase}/servers/load-config?config_file=configs/mcp_servers.json`, {
                method: 'POST'
            });
            if (!response.ok) throw new Error('Failed to load configuration');
            
            const result = await response.json();
            
            // Load configured servers
            await this.loadConfiguredServers();
            
            // Don't show success notification here - wait for status refresh
            
        } catch (error) {
            this.showNotification(`Error loading config: ${error.message}`, 'error');
        }
    }

    async loadConfiguredServers() {
        try {
            const response = await fetch(`${this.apiBase}/servers/configured`);
            if (!response.ok) throw new Error('Failed to load configured servers');
            
            const result = await response.json();
            // Handle both array and object response formats
            const configuredServers = Array.isArray(result) ? result : (result.servers || []);
            this.renderConfiguredServers(configuredServers);
            
        } catch (error) {
            this.showNotification(`Error loading configured servers: ${error.message}`, 'error');
        }
    }

    renderConfiguredServers(configuredServers) {
        const serverGrid = document.getElementById('serverGrid');
        serverGrid.innerHTML = '';

        configuredServers.forEach(serverName => {
            const serverCard = this.createServerCardFromName(serverName);
            serverGrid.appendChild(serverCard);
        });
    }

    createServerCardFromName(serverName) {
        const card = document.createElement('div');
        card.className = 'server-card inactive';
        card.dataset.serverName = serverName;

        card.innerHTML = `
            <div class="server-header">
                <div class="server-name">${serverName}</div>
                <input type="checkbox" class="server-checkbox" ${this.selectedServers.has(serverName) ? 'checked' : ''}>
            </div>
            <div class="server-status">
                <span class="status-indicator status-inactive"></span>
                <span>inactive</span>
            </div>
            <div class="server-info">
                <div class="info-item">
                    <strong>Transport:</strong> stdio
                </div>
                <div class="info-item">
                    <strong>Tools:</strong> 0
                </div>
            </div>
            <div class="server-actions">
                <button class="btn btn-success" onclick="mcpManager.startServer('${serverName}')">Start</button>
                <button class="btn btn-danger" onclick="mcpManager.stopServer('${serverName}')">Stop</button>
                <button class="btn btn-secondary" onclick="mcpManager.showServerConfig('${serverName}')">Config</button>
            </div>
        `;

        // Add checkbox event listener
        const checkbox = card.querySelector('.server-checkbox');
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.selectedServers.add(serverName);
            } else {
                this.selectedServers.delete(serverName);
            }
        });

        return card;
    }

    createServerCard(server) {
        const card = document.createElement('div');
        card.className = 'server-card';
        card.dataset.serverName = server.name;

        const isActive = server.status === 'active';
        if (isActive) card.classList.add('active');
        else card.classList.add('inactive');

        card.innerHTML = `
            <div class="server-header">
                <div class="server-name">${server.name}</div>
                <input type="checkbox" class="server-checkbox" ${this.selectedServers.has(server.name) ? 'checked' : ''}>
            </div>
            <div class="server-status">
                <span class="status-indicator ${isActive ? 'status-active' : 'status-inactive'}"></span>
                <span>${server.status}</span>
            </div>
            <div class="server-info">
                <div class="info-item">
                    <strong>Transport:</strong> ${server.transport}
                </div>
                <div class="info-item">
                    <strong>Tools:</strong> ${server.tools_count || 0}
                </div>
            </div>
            <div class="server-actions">
                <button class="btn btn-success" onclick="mcpManager.startServer('${server.name}')">Start</button>
                <button class="btn btn-danger" onclick="mcpManager.stopServer('${server.name}')">Stop</button>
                <button class="btn btn-secondary" onclick="mcpManager.showServerConfig('${server.name}')">Config</button>
            </div>
        `;

        // Add checkbox event listener
        const checkbox = card.querySelector('.server-checkbox');
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.selectedServers.add(server.name);
            } else {
                this.selectedServers.delete(server.name);
            }
        });

        return card;
    }

    async checkAvailability() {
        try {
            this.showNotification('Checking server availability...', 'info');
            
            const response = await fetch(`${this.apiBase}/servers/check-availability`);
            if (!response.ok) throw new Error('Failed to check availability');
            
            const availableServers = await response.json();
            this.showNotification(`Found ${availableServers.length} available servers`, 'success');
            
            // Update server cards with availability info
            this.updateServerAvailability(availableServers);
            
        } catch (error) {
            this.showNotification(`Error checking availability: ${error.message}`, 'error');
        }
    }

    updateServerAvailability(availableServers) {
        const availableSet = new Set(availableServers.map(s => s.name));
        
        document.querySelectorAll('.server-card').forEach(card => {
            const serverName = card.dataset.serverName;
            const checkbox = card.querySelector('.server-checkbox');
            
            if (availableSet.has(serverName)) {
                checkbox.disabled = false;
                card.style.opacity = '1';
            } else {
                checkbox.disabled = true;
                card.style.opacity = '0.6';
            }
        });
    }

    async startSelectedServers() {
        const selected = Array.from(this.selectedServers);
        if (selected.length === 0) {
            this.showNotification('Please select servers to start', 'warning');
            return;
        }

        this.showNotification(`Starting ${selected.length} servers...`, 'info');
        
        for (const serverName of selected) {
            try {
                await this.startServer(serverName);
                await new Promise(resolve => setTimeout(resolve, 1000)); // Delay between starts
            } catch (error) {
                this.showNotification(`Failed to start ${serverName}: ${error.message}`, 'error');
            }
        }
        
        await this.refreshStatus();
        await this.refreshTools();
    }

    async stopSelectedServers() {
        const selected = Array.from(this.selectedServers);
        if (selected.length === 0) {
            this.showNotification('Please select servers to stop', 'warning');
            return;
        }

        this.showNotification(`Stopping ${selected.length} servers...`, 'info');
        
        for (const serverName of selected) {
            try {
                await this.stopServer(serverName);
                await new Promise(resolve => setTimeout(resolve, 500)); // Delay between stops
            } catch (error) {
                this.showNotification(`Failed to stop ${serverName}: ${error.message}`, 'error');
            }
        }
        
        await this.refreshStatus();
        await this.refreshTools();
    }

    async startServer(serverName) {
        const response = await fetch(`${this.apiBase}/servers/${serverName}/start`, { method: 'POST' });
        if (!response.ok) throw new Error(`Failed to start ${serverName}`);
        
        this.showNotification(`${serverName} started successfully`, 'success');
        await this.refreshStatus();
    }

    async stopServer(serverName) {
        try {
            const response = await fetch(`${this.apiBase}/servers/${serverName}/stop`, { method: 'POST' });
            if (!response.ok) throw new Error('Failed to stop server');
            
            this.showNotification(`Server ${serverName} stopped successfully`, 'success');
            await this.refreshStatus();
            await this.refreshTools();
            
        } catch (error) {
            this.showNotification(`Error stopping server: ${error.message}`, 'error');
        }
    }

    async refreshTools() {
        try {
            const response = await fetch(`${this.apiBase}/tools`);
            if (!response.ok) throw new Error('Failed to fetch tools');
            
            const tools = await response.json();
            this.tools.clear();
            
            tools.forEach(tool => {
                this.tools.set(tool.name, tool);
            });
            
            this.renderTools();
            this.updateToolCounts();
            
        } catch (error) {
            this.showNotification(`Error refreshing tools: ${error.message}`, 'error');
        }
    }

    renderTools() {
        const enabledToolsList = document.getElementById('enabledToolsList');
        const disabledToolsList = document.getElementById('disabledToolsList');
        
        enabledToolsList.innerHTML = '';
        disabledToolsList.innerHTML = '';

        // Update server filter options
        const serverFilter = document.getElementById('serverFilter');
        const servers = [...new Set(Array.from(this.tools.values()).map(t => t.server))];
        
        serverFilter.innerHTML = '<option value="">All Servers</option>';
        servers.forEach(server => {
            const option = document.createElement('option');
            option.value = server;
            option.textContent = server;
            serverFilter.appendChild(option);
        });

        // Separate tools into enabled and disabled lists
        Array.from(this.tools.values()).forEach(tool => {
            const isEnabled = this.enabledTools.has(tool.name);
            const toolItem = this.createToolItem(tool, isEnabled);
            
            if (isEnabled) {
                enabledToolsList.appendChild(toolItem);
            } else {
                disabledToolsList.appendChild(toolItem);
            }
        });
    }

    createToolItem(tool, isEnabled) {
        const item = document.createElement('div');
        item.className = `tool-item ${isEnabled ? 'enabled' : 'disabled'}`;
        item.dataset.toolName = tool.name;
        item.dataset.serverName = tool.server;

        item.innerHTML = `
            <div class="tool-info">
                <div class="tool-name">${tool.name}</div>
                <div class="tool-server">${tool.server}</div>
            </div>
            <div class="tool-actions">
                <button class="btn btn-secondary" onclick="mcpManager.toggleTool('${tool.name}')">
                    ${isEnabled ? 'Disable' : 'Enable'}
                </button>
                <button class="btn btn-primary" onclick="mcpManager.showToolDetails(${JSON.stringify(tool).replace(/"/g, '&quot;')})">
                    Details
                </button>
            </div>
        `;

        return item;
    }

    createToolCard(tool) {
        const card = document.createElement('div');
        card.className = 'tool-card';
        card.dataset.toolName = tool.name;
        card.dataset.serverName = tool.server;

        const isEnabled = this.enabledTools.has(tool.name);
        if (isEnabled) card.classList.add('enabled');
        else card.classList.add('disabled');

        card.innerHTML = `
            <div class="tool-header">
                <div class="tool-name">${tool.name}</div>
                <input type="checkbox" class="tool-checkbox" ${isEnabled ? 'checked' : ''}>
            </div>
            <div class="tool-server">Server: ${tool.server}</div>
            <div class="tool-description">${tool.description || 'No description available'}</div>
        `;

        // Add checkbox event listener
        const checkbox = card.querySelector('.tool-checkbox');
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.enabledTools.add(tool.name);
                card.classList.remove('disabled');
                card.classList.add('enabled');
            } else {
                this.enabledTools.delete(tool.name);
                card.classList.remove('enabled');
                card.classList.add('disabled');
            }
            this.updateToolCounts();
        });

        // Add click event for tool details
        card.addEventListener('click', (e) => {
            if (e.target !== checkbox) {
                this.showToolDetails(tool);
            }
        });

        return card;
    }

    async toggleTool(toolName) {
        if (this.enabledTools.has(toolName)) {
            this.enabledTools.delete(toolName);
        } else {
            this.enabledTools.add(toolName);
        }
        
        // Re-render tools to update the lists
        this.renderTools();
        this.updateToolCounts();
        
        // Save the configuration immediately
        await this.saveToolConfig();
    }

    filterTools() {
        const searchTerm = document.getElementById('toolSearch').value.toLowerCase();
        const selectedServer = document.getElementById('serverFilter').value;

        document.querySelectorAll('.tool-item').forEach(item => {
            const toolName = item.dataset.toolName.toLowerCase();
            const serverName = item.dataset.serverName;
            
            const matchesSearch = toolName.includes(searchTerm);
            const matchesServer = !selectedServer || serverName === selectedServer;
            
            item.style.display = matchesSearch && matchesServer ? 'flex' : 'none';
        });
    }

    async enableAllTools() {
        // Enable all tools
        Array.from(this.tools.values()).forEach(tool => {
            this.enabledTools.add(tool.name);
        });
        
        // Re-render tools
        this.renderTools();
        this.updateToolCounts();
        
        // Save the configuration
        await this.saveToolConfig();
        this.showNotification('All tools enabled', 'success');
    }

    async disableAllTools() {
        // Disable all tools
        this.enabledTools.clear();
        
        // Re-render tools
        this.renderTools();
        this.updateToolCounts();
        
        // Save the configuration
        await this.saveToolConfig();
        this.showNotification('All tools disabled', 'success');
    }

    async loadToolConfig() {
        try {
            const response = await fetch(`${this.apiBase}/tools/config`);
            if (!response.ok) throw new Error('Failed to load tool configuration');
            
            const config = await response.json();
            this.enabledTools = new Set(config.enabled_tools || []);
            
            // Update tool checkboxes if tools are already loaded
            this.updateToolCheckboxes();
            
        } catch (error) {
            console.warn('Could not load tool configuration:', error.message);
        }
    }

    updateToolCheckboxes() {
        document.querySelectorAll('.tool-checkbox').forEach(checkbox => {
            const toolName = checkbox.closest('.tool-card').dataset.toolName;
            checkbox.checked = this.enabledTools.has(toolName);
            
            const card = checkbox.closest('.tool-card');
            if (checkbox.checked) {
                card.classList.remove('disabled');
                card.classList.add('enabled');
            } else {
                card.classList.remove('enabled');
                card.classList.add('disabled');
            }
        });
        this.updateToolCounts();
    }

    async saveToolConfig() {
        try {
            const enabledToolsList = Array.from(this.enabledTools);
            
            const response = await fetch(`${this.apiBase}/tools/save-config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled_tools: enabledToolsList })
            });
            
            if (!response.ok) throw new Error('Failed to save tool configuration');
            
            const result = await response.json();
            this.showNotification(`Tool configuration saved: ${result.enabled_tools_count} tools enabled`, 'success');
            
            // Refresh the tools to update the lists
            await this.refreshTools();
            
        } catch (error) {
            this.showNotification(`Error saving tool config: ${error.message}`, 'error');
        }
    }

    async refreshStatus() {
        try {
            const response = await fetch(`${this.apiBase}/servers`);
            if (!response.ok) throw new Error('Failed to fetch server status');
            
            const servers = await response.json();
            
            // Update status dashboard
            const activeServers = servers.filter(s => s.status === 'active').length;
            document.getElementById('activeServers').textContent = activeServers;
            
            const totalTools = servers.reduce((sum, s) => sum + (s.tools_count || 0), 0);
            document.getElementById('totalTools').textContent = totalTools;
            
            document.getElementById('enabledTools').textContent = this.enabledTools.size;
            
            // Update API status
            document.getElementById('apiStatus').textContent = 'Connected';
            document.getElementById('apiStatus').className = 'status-indicator status-active';
            
            // Update server cards
            this.updateServerCards(servers);
            
            // Show success notification for initial load
            if (servers.length > 0) {
                this.showNotification(`Loaded ${servers.length} servers successfully!`, 'success');
            }
            
        } catch (error) {
            document.getElementById('apiStatus').textContent = 'Disconnected';
            document.getElementById('apiStatus').className = 'status-indicator status-inactive';
            this.showNotification(`Error refreshing status: ${error.message}`, 'error');
        }
    }

    updateServerCards(servers) {
        servers.forEach(server => {
            const card = document.querySelector(`[data-server-name="${server.name}"]`);
            if (card) {
                const statusIndicator = card.querySelector('.status-indicator');
                const statusText = card.querySelector('.server-status span:last-child');
                const toolsCount = card.querySelector('.info-item:last-child');
                
                // Update status
                statusIndicator.className = `status-indicator ${server.status === 'active' ? 'status-active' : 'status-inactive'}`;
                statusText.textContent = server.status;
                
                // Update tools count
                toolsCount.innerHTML = `<strong>Tools:</strong> ${server.tools_count || 0}`;
                
                // Update card class
                card.className = `server-card ${server.status === 'active' ? 'active' : 'inactive'}`;
            }
        });
    }

    updateToolCounts() {
        document.getElementById('enabledTools').textContent = this.enabledTools.size;
    }

    async updateConfigurationInfo() {
        try {
            document.getElementById('apiBaseUrl').textContent = this.apiBase;
            
            const response = await fetch(`${this.apiBase}/servers/configured`);
            if (response.ok) {
                const configuredServers = await response.json();
                document.getElementById('configuredServers').textContent = configuredServers.length;
            }
            
            document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
            
        } catch (error) {
            this.showNotification(`Error updating config info: ${error.message}`, 'error');
        }
    }

    async showServerConfig(serverName) {
        try {
            const response = await fetch(`${this.apiBase}/servers/config/${serverName}`);
            if (!response.ok) throw new Error('Failed to fetch server config');
            
            const config = await response.json();
            this.showModal(`Server Configuration: ${serverName}`, `
                <pre>${JSON.stringify(config, null, 2)}</pre>
            `);
            
        } catch (error) {
            this.showNotification(`Error fetching server config: ${error.message}`, 'error');
        }
    }

    async showToolDetails(tool) {
        try {
            const response = await fetch(`${this.apiBase}/tools/info/${tool.name}`);
            if (!response.ok) throw new Error('Failed to fetch tool details');
            
            const toolInfo = await response.json();
            this.showModal(`Tool Details: ${tool.name}`, `
                <div class="tool-details">
                    <p><strong>Name:</strong> ${toolInfo.name}</p>
                    <p><strong>Server:</strong> ${toolInfo.server}</p>
                    <p><strong>Description:</strong> ${toolInfo.description || 'No description'}</p>
                    <p><strong>Input Schema:</strong></p>
                    <pre>${JSON.stringify(toolInfo.input_schema || {}, null, 2)}</pre>
                </div>
            `);
            
        } catch (error) {
            this.showNotification(`Error fetching tool details: ${error.message}`, 'error');
        }
    }

    showModal(title, content) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalContent').innerHTML = content;
        document.getElementById('toolModal').style.display = 'block';
    }

    closeModal() {
        document.getElementById('toolModal').style.display = 'none';
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 3000);
    }
}

// Initialize the MCP Hub Manager when the page loads
let mcpManager;
document.addEventListener('DOMContentLoaded', () => {
    mcpManager = new MCPHubManager();
});

