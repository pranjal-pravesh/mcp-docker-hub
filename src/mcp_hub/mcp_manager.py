"""
MCP Manager for handling Model Context Protocol servers
"""
import asyncio
import json
import logging
import subprocess
import time
from typing import Dict, List, Any, Optional
import httpx
from dataclasses import dataclass
import os
from dotenv import load_dotenv
from .tool_adapter import ToolHub, ProtocolType
import re

# Load environment variables
load_dotenv()

@dataclass
class MCPServer:
    """Configuration for an MCP server"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    transport: str = "stdio"  # stdio, sse, or http
    host: Optional[str] = None
    port: Optional[int] = None
    url: Optional[str] = None
    docker_image: Optional[str] = None
    docker_ports: Optional[List[str]] = None
    docker_volumes: Optional[List[str]] = None
    health_check_url: Optional[str] = None
    health_check_timeout: int = 30

class MCPManager:
    """Manages MCP server connections and tool discovery"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.servers: Dict[str, MCPServer] = {}
        self.active_connections: Dict[str, Any] = {}
        self.available_tools: Dict[str, List[Dict]] = {}
        self.tool_hub = ToolHub()  # Unified tool interface
        
    def add_server(self, server: MCPServer):
        """Add an MCP server configuration"""
        self.servers[server.name] = server
        self.logger.info(f"Added MCP server: {server.name}")
        
    def add_docker_mcp_server(self, 
                            name: str,
                            docker_image: str,
                            env_vars: Dict[str, str] = None,
                            transport: str = "stdio",
                            ports: List[str] = None,
                            volumes: List[str] = None,
                            health_check_url: str = None,
                            health_check_timeout: int = 30,
                            additional_args: List[str] = None):
        """
        Dynamically add any Docker MCP server with minimal configuration
        
        Args:
            name: Unique name for the server
            docker_image: Docker image name (e.g., "mcp/slack", "mcp/brave-search")
            env_vars: Environment variables to pass to the container
            transport: Transport type ("stdio", "http", "sse")
            ports: Port mappings (e.g., ["8080:8080"])
            volumes: Volume mappings (e.g., ["/host/path:/container/path"])
            health_check_url: URL for health checks (for HTTP transport)
            health_check_timeout: Timeout for health checks in seconds
            additional_args: Additional Docker run arguments
        """
        if env_vars is None:
            env_vars = {}
        if additional_args is None:
            additional_args = []
            
        # Build Docker arguments
        docker_args = ["run"]
        
        # Add interactive flag for stdio transport
        if transport == "stdio":
            docker_args.extend(["-i", "--rm"])
        else:
            docker_args.extend(["-d", "--rm"])
            
        # Add environment variables
        for key, value in env_vars.items():
            docker_args.extend(["-e", key])
            
        # Add port mappings
        if ports:
            for port_mapping in ports:
                docker_args.extend(["-p", port_mapping])
                
        # Add volume mappings
        if volumes:
            for volume_mapping in volumes:
                docker_args.extend(["-v", volume_mapping])
                
        # Add the image name
        docker_args.append(docker_image)
        
        # Add additional arguments after the image name
        if additional_args:
            docker_args.extend(additional_args)
            
        # Determine URL for HTTP transport
        url = None
        if transport == "http" and ports:
            # Extract the host port from the first port mapping
            host_port = ports[0].split(":")[0] if ":" in ports[0] else ports[0]
            url = f"http://localhost:{host_port}"
        elif health_check_url:
            url = health_check_url
            
        server = MCPServer(
            name=name,
            command="docker",
            args=docker_args,
            env=env_vars,
            transport=transport,
            docker_image=docker_image,
            docker_ports=ports,
            docker_volumes=volumes,
            health_check_url=health_check_url,
            health_check_timeout=health_check_timeout,
            url=url
        )
        
        self.add_server(server)
        self.logger.info(f"Added Docker MCP server: {name} using image {docker_image}")
        
    def add_slack_server(self, name: str = "slack", use_docker: bool = True):
        """Add Slack MCP server with Docker or NPX"""
        # Get environment variables
        slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        slack_team_id = os.getenv("SLACK_TEAM_ID")
        slack_channel_ids = os.getenv("SLACK_CHANNEL_IDS", "")
        
        if not slack_bot_token or not slack_team_id:
            raise ValueError("SLACK_BOT_TOKEN and SLACK_TEAM_ID must be set in .env file")
        
        env_vars = {
            "SLACK_BOT_TOKEN": slack_bot_token,
            "SLACK_TEAM_ID": slack_team_id
        }
        
        if slack_channel_ids:
            env_vars["SLACK_CHANNEL_IDS"] = slack_channel_ids
        
        if use_docker:
            docker_args = [
                "run", "-i", "--rm",
                "-e", "SLACK_BOT_TOKEN",
                "-e", "SLACK_TEAM_ID"
            ]
            
            # Only add SLACK_CHANNEL_IDS if it's actually set
            if slack_channel_ids:
                docker_args.extend(["-e", "SLACK_CHANNEL_IDS"])
            
            docker_args.append("mcp/slack")
            
            server = MCPServer(
                name=name,
                command="docker",
                args=docker_args,
                env=env_vars,
                transport="stdio"
            )
        else:
            server = MCPServer(
                name=name,
                command="npx",
                args=["-y", "@modelcontextprotocol/server-slack"],
                env=env_vars,
                transport="stdio"
            )
        
        self.add_server(server)
        
    def add_brave_search_server(self, name: str = "brave-search", use_docker: bool = False):
        """Add Brave Search MCP server with NPX (Docker version has transport issues)"""
        # Get environment variable
        brave_api_key = os.getenv("BRAVE_API_KEY")
        
        if not brave_api_key:
            raise ValueError("BRAVE_API_KEY must be set in .env file")
        
        env_vars = {
            "BRAVE_API_KEY": brave_api_key
        }
        
        if use_docker:
            # Docker version runs HTTP server on port 8080
            server = MCPServer(
                name=name,
                command="docker",
                args=[
                    "run", "-d", "--rm",
                    "-p", "8080:8080",
                    "-e", "BRAVE_API_KEY",
                    "mcp/brave-search"
                ],
                env=env_vars,
                transport="http",  # Mark as HTTP transport
                host="localhost",
                port=8080,
                url="http://localhost:8080"
            )
        else:
            # Use NPX version which supports stdio transport
            server = MCPServer(
                name=name,
                command="npx",
                args=["-y", "@modelcontextprotocol/server-brave-search"],
                env=env_vars,
                transport="stdio"
            )
        
        self.add_server(server)
        
    def add_wolfram_alpha_server(self, name: str = "wolfram-alpha", use_docker: bool = True):
        """Add Wolfram Alpha MCP server with Docker or NPX"""
        # Get environment variable
        wolfram_api_key = os.getenv("WOLFRAM_API_KEY")
        
        if not wolfram_api_key:
            raise ValueError("WOLFRAM_API_KEY must be set in .env file")
        
        env_vars = {
            "WOLFRAM_API_KEY": wolfram_api_key
        }
        
        if use_docker:
            # Docker version
            server = MCPServer(
                name=name,
                command="docker",
                args=[
                    "run", "-i", "--rm",
                    "-e", "WOLFRAM_API_KEY",
                    "mcp/wolfram-alpha"
                ],
                env=env_vars,
                transport="stdio"
            )
        else:
            # Use NPX version if available
            server = MCPServer(
                name=name,
                command="npx",
                args=["-y", "@modelcontextprotocol/server-wolfram-alpha"],
                env=env_vars,
                transport="stdio"
            )
        
        self.add_server(server)
        
    async def start_server(self, server_name: str) -> bool:
        """Start an MCP server"""
        if server_name not in self.servers:
            self.logger.error(f"Server {server_name} not found")
            return False
            
        server = self.servers[server_name]
        
        try:
            if server.transport == "stdio":
                return await self._start_stdio_server(server)
            elif server.transport == "sse":
                return await self._start_sse_server(server)
            elif server.transport == "http":
                return await self._start_http_server(server)
            else:
                self.logger.error(f"Unsupported transport: {server.transport}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start server {server_name}: {e}")
            return False
    
    async def start_all_servers(self) -> Dict[str, bool]:
        """Start all configured servers"""
        results = {}
        for server_name in self.servers.keys():
            if server_name not in self.active_connections:
                self.logger.info(f"Starting server: {server_name}")
                results[server_name] = await self.start_server(server_name)
            else:
                self.logger.info(f"Server {server_name} already running")
                results[server_name] = True
        return results
    
    async def _start_stdio_server(self, server: MCPServer) -> bool:
        """Start an MCP server using stdio transport"""
        try:
            # Create environment for subprocess
            env = os.environ.copy()
            env.update(server.env)
            
            # Start the process
            process = await asyncio.create_subprocess_exec(
                server.command,
                *server.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            self.active_connections[server.name] = {
                "process": process,
                "transport": "stdio"
            }
            
            # Check if process started properly
            await asyncio.sleep(0.5)  # Give process time to start
            if process.returncode is not None:
                stderr_output = await process.stderr.read()
                self.logger.error(f"Process failed to start: {stderr_output.decode()}")
                return False
            
            # Initialize MCP protocol
            await self._initialize_mcp_connection(server.name)
            
            self.logger.info(f"Started MCP server: {server.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start stdio server {server.name}: {e}")
            return False
    
    async def _start_sse_server(self, server: MCPServer) -> bool:
        """Start an MCP server using SSE transport"""
        try:
            # For SSE, we assume the server is already running
            # We just need to connect to it
            if not server.url:
                server.url = f"http://{server.host or 'localhost'}:{server.port or 8080}/sse"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{server.url}/health")
                if response.status_code == 200:
                    self.active_connections[server.name] = {
                        "url": server.url,
                        "transport": "sse"
                    }
                    
                    await self._initialize_mcp_connection(server.name)
                    self.logger.info(f"Connected to SSE MCP server: {server.name}")
                    return True
                else:
                    self.logger.error(f"SSE server {server.name} health check failed")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to connect to SSE server {server.name}: {e}")
            return False
    
    async def _start_http_server(self, server: MCPServer) -> bool:
        """Start an HTTP MCP server (like Brave Search Docker)"""
        try:
            # Create environment for subprocess
            env = os.environ.copy()
            env.update(server.env)
            
            # Start the Docker container in detached mode
            process = await asyncio.create_subprocess_exec(
                server.command,
                *server.args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            self.active_connections[server.name] = {
                "process": process,
                "transport": "http",
                "url": server.url
            }
            
            # Wait for the HTTP server to be ready
            base_url = server.url
            max_retries = 30
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{base_url}/", timeout=5.0)
                        if response.status_code in [200, 404]:  # Server is responding
                            self.logger.info(f"HTTP server {server.name} is ready")
                            
                            # Discover tools using the ToolHub
                            tools = await self.tool_hub.discover_http_tools(server.name, base_url)
                            if tools:
                                self.available_tools[server.name] = tools
                                self.logger.info(f"Discovered {len(tools)} tools from HTTP server {server.name}")
                            else:
                                self.logger.warning(f"No tools discovered from HTTP server {server.name}")
                            
                            return True
                            
                except Exception as e:
                    if attempt < max_retries - 1:
                        self.logger.debug(f"Attempt {attempt + 1}: HTTP server not ready yet: {e}")
                        await asyncio.sleep(retry_delay)
                    else:
                        self.logger.error(f"HTTP server {server.name} failed to start: {e}")
                        return False
            
            self.logger.error(f"HTTP server {server.name} did not become ready in time")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to start HTTP server {server.name}: {e}")
            return False
    
    async def _initialize_mcp_connection(self, server_name: str):
        """Initialize MCP protocol connection and discover tools"""
        try:
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "proactive-agent",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await self._send_request(server_name, init_request)
            
            if response and response.get("result"):
                # Send initialized notification
                initialized_notif = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                await self._send_notification(server_name, initialized_notif)
                
                # Discover tools
                await self._discover_tools(server_name)
                
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP connection for {server_name}: {e}")
    
    async def _discover_tools(self, server_name: str):
        """Discover available tools from the MCP server"""
        try:
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            response = await self._send_request(server_name, tools_request)
            
            if response and response.get("result"):
                tools = response["result"].get("tools", [])
                self.available_tools[server_name] = tools
                self.logger.info(f"Discovered {len(tools)} tools for {server_name}")
                
                # Register tools with ToolHub for unified access
                connection = self.active_connections.get(server_name)
                if connection and connection.get("transport") == "stdio":
                    process = connection.get("process")
                    self.tool_hub.register_stdio_tools(server_name, tools, process)
                
                # Log tool names
                for tool in tools:
                    self.logger.info(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                    
        except Exception as e:
            self.logger.error(f"Failed to discover tools for {server_name}: {e}")
    
    async def _send_request(self, server_name: str, request: Dict) -> Optional[Dict]:
        """Send a request to an MCP server"""
        connection = self.active_connections.get(server_name)
        if not connection:
            return None
            
        try:
            if connection["transport"] == "stdio":
                return await self._send_stdio_request(connection, request)
            elif connection["transport"] == "sse":
                return await self._send_sse_request(connection, request)
            else:
                self.logger.error(f"Unsupported transport for request")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to send request to {server_name}: {e}")
            return None
    
    async def _send_notification(self, server_name: str, notification: Dict):
        """Send a notification to an MCP server"""
        connection = self.active_connections.get(server_name)
        if not connection:
            return
            
        try:
            if connection["transport"] == "stdio":
                await self._send_stdio_notification(connection, notification)
            elif connection["transport"] == "sse":
                await self._send_sse_notification(connection, notification)
                
        except Exception as e:
            self.logger.error(f"Failed to send notification to {server_name}: {e}")
    
    async def _send_stdio_request(self, connection: Dict, request: Dict) -> Optional[Dict]:
        """Send request via stdio transport"""
        process = connection["process"]
        
        try:
            # Check if process is still alive
            if process.returncode is not None:
                self.logger.error(f"Process has terminated with code {process.returncode}")
                return None
            
            # Send request
            request_data = json.dumps(request) + "\n"
            self.logger.debug(f"Sending request: {request_data.strip()}")
            
            process.stdin.write(request_data.encode())
            await process.stdin.drain()
            
            # Read response with timeout
            try:
                response_line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
            except asyncio.TimeoutError:
                self.logger.error("Timeout waiting for response")
                return None
            
            if response_line:
                response_text = response_line.decode().strip()
                self.logger.debug(f"Received response: {response_text}")
                
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON response: {e}")
                    self.logger.error(f"Raw response: {response_text}")
                    return None
            else:
                self.logger.error("No response received")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in stdio communication: {e}")
            return None
    
    async def _send_stdio_notification(self, connection: Dict, notification: Dict):
        """Send notification via stdio transport"""
        process = connection["process"]
        
        # Send notification
        notif_data = json.dumps(notification) + "\n"
        process.stdin.write(notif_data.encode())
        await process.stdin.drain()
    
    async def _send_sse_request(self, connection: Dict, request: Dict) -> Optional[Dict]:
        """Send request via SSE transport"""
        # For SSE, we would typically use HTTP POST to send requests
        # This is a simplified implementation
        url = connection["url"].replace("/sse", "/request")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=request)
            if response.status_code == 200:
                return response.json()
        
        return None
    
    async def _send_sse_notification(self, connection: Dict, notification: Dict):
        """Send notification via SSE transport"""
        # Similar to request but for notifications
        url = connection["url"].replace("/sse", "/notify")
        
        async with httpx.AsyncClient() as client:
            await client.post(url, json=notification)
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict) -> Optional[Dict]:
        """Call a tool on an MCP server using the unified ToolHub interface"""
        # Use ToolHub for unified tool calling across all protocols
        return await self.tool_hub.call_tool(tool_name, arguments)
    
    def get_all_tools(self) -> Dict[str, List[Dict]]:
        """Get all available tools from all servers"""
        # Merge tools from both the legacy interface and ToolHub
        all_tools = self.available_tools.copy()
        hub_tools = self.tool_hub.get_all_tools()
        
        # Merge ToolHub tools (these will include protocol info)
        for server_name, tools in hub_tools.items():
            if server_name in all_tools:
                # Update existing tools with protocol info
                for tool in tools:
                    for existing_tool in all_tools[server_name]:
                        if existing_tool.get('name') == tool.get('name'):
                            existing_tool['protocol'] = tool.get('protocol')
            else:
                all_tools[server_name] = tools
        
        return all_tools
    
    def get_server_tools(self, server_name: str) -> List[Dict]:
        """Get tools for a specific server"""
        return self.available_tools.get(server_name, [])
    
    async def stop_server(self, server_name: str):
        """Stop an MCP server"""
        connection = self.active_connections.get(server_name)
        if not connection:
            return
        
        try:
            transport = connection.get("transport", "stdio")
            
            if transport == "stdio":
                # Check if this is a Docker container
                server_config = self.servers.get(server_name)
                if server_config and server_config.docker_image:
                    # This is a Docker container, stop it using docker stop
                    await self._stop_docker_container(server_name)
                else:
                    # This is a regular process, terminate it
                    process = connection["process"]
                    process.terminate()
                    await process.wait()
            elif transport == "http":
                # For HTTP servers, we might need to stop Docker containers too
                server_config = self.servers.get(server_name)
                if server_config and server_config.docker_image:
                    await self._stop_docker_container(server_name)
            
            del self.active_connections[server_name]
            if server_name in self.available_tools:
                del self.available_tools[server_name]
            
            # Remove tools from the tool hub registry
            self.tool_hub.remove_server_tools(server_name)
                
            self.logger.info(f"Stopped MCP server: {server_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to stop server {server_name}: {e}")
    
    async def _stop_docker_container(self, server_name: str):
        """Stop a Docker container for a given server"""
        try:
            # Find the container by looking for containers with the server name in their command
            # or by using a naming convention
            server_config = self.servers.get(server_name)
            if not server_config or not server_config.docker_image:
                return
            
            # Use docker ps to find containers running the specific image
            process = await asyncio.create_subprocess_exec(
                "docker", "ps", "--filter", f"ancestor={server_config.docker_image}", 
                "--format", "{{.Names}}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            if process.returncode == 0 and stdout.strip():
                container_names = stdout.decode().strip().split('\n')
                for container_name in container_names:
                    if container_name.strip():
                        # Stop the container
                        stop_process = await asyncio.create_subprocess_exec(
                            "docker", "stop", container_name.strip(),
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        try:
                            await asyncio.wait_for(stop_process.communicate(), timeout=10.0)
                            self.logger.info(f"Stopped Docker container: {container_name.strip()}")
                        except asyncio.TimeoutError:
                            self.logger.warning(f"Timeout stopping Docker container: {container_name.strip()}")
                            # Force kill the container
                            kill_process = await asyncio.create_subprocess_exec(
                                "docker", "kill", container_name.strip(),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                            )
                            await kill_process.communicate()
                            self.logger.info(f"Force killed Docker container: {container_name.strip()}")
            else:
                self.logger.warning(f"No Docker container found for server: {server_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to stop Docker container for {server_name}: {e}")
    
    async def stop_all_servers(self):
        """Stop all MCP servers"""
        server_names = list(self.active_connections.keys())
        for server_name in server_names:
            try:
                await asyncio.wait_for(self.stop_server(server_name), timeout=10.0)
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout stopping server {server_name}")
            except Exception as e:
                self.logger.error(f"Error stopping server {server_name}: {e}")

    def remove_server(self, server_name: str) -> bool:
        """Remove an MCP server configuration"""
        if server_name in self.servers:
            del self.servers[server_name]
            self.logger.info(f"Removed MCP server configuration: {server_name}")
            return True
        else:
            self.logger.warning(f"Server {server_name} not found in configuration")
            return False
            
    def get_server_config(self, server_name: str) -> Optional[MCPServer]:
        """Get server configuration"""
        return self.servers.get(server_name)
        
    def list_configured_servers(self) -> List[str]:
        """List all configured server names"""
        return list(self.servers.keys())
        
    def load_servers_from_config(self, config_file: str = "configs/mcp_servers.json") -> Dict[str, bool]:
        """
        Load server configurations from a JSON file
        
        Args:
            config_file: Path to the JSON configuration file
            
        Returns:
            Dict mapping server names to success status
        """
        results = {}
        
        try:
            if not os.path.exists(config_file):
                self.logger.warning(f"Configuration file {config_file} not found")
                return results
                
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            servers_config = config.get('servers', {})
            
            for server_name, server_config in servers_config.items():
                try:
                    # Substitute environment variables
                    processed_config = self._substitute_env_vars(server_config)
                    
                    # Check if required environment variables are set
                    env_vars = processed_config.get('env_vars', {})
                    missing_vars = []
                    
                    for key, value in env_vars.items():
                        if value.startswith('${') and value.endswith('}'):
                            env_var_name = value[2:-1]  # Remove ${ and }
                            if not os.getenv(env_var_name):
                                missing_vars.append(env_var_name)
                    
                    if missing_vars:
                        self.logger.warning(f"Skipping server '{server_name}' - missing environment variables: {missing_vars}")
                        results[server_name] = False
                        continue
                    
                    # Add the server using the dynamic method
                    self.add_docker_mcp_server(
                        name=server_name,
                        docker_image=processed_config['docker_image'],
                        env_vars=processed_config.get('env_vars', {}),
                        transport=processed_config.get('transport', 'stdio'),
                        ports=processed_config.get('ports'),
                        volumes=processed_config.get('volumes'),
                        health_check_url=processed_config.get('health_check_url'),
                        health_check_timeout=processed_config.get('health_check_timeout', 30),
                        additional_args=processed_config.get('additional_args')
                    )
                    
                    results[server_name] = True
                    self.logger.info(f"Loaded server configuration: {server_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to load server {server_name}: {e}")
                    results[server_name] = False
                    
        except Exception as e:
            self.logger.error(f"Failed to load configuration file {config_file}: {e}")
            
        return results
        
    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Substitute environment variables in configuration values
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration with environment variables substituted
        """
        processed_config = {}
        
        for key, value in config.items():
            if isinstance(value, dict):
                processed_config[key] = self._substitute_env_vars(value)
            elif isinstance(value, list):
                processed_config[key] = [
                    self._substitute_env_vars(item) if isinstance(item, dict) else item
                    for item in value
                ]
            elif isinstance(value, str):
                # Replace ${VAR_NAME} patterns with environment variable values
                def substitute_var(match):
                    var_name = match.group(1)
                    # Try environment variable first
                    env_value = os.getenv(var_name)
                    if env_value:
                        return env_value
                    # Try shell variables for common ones
                    if var_name == "PWD":
                        return os.getcwd()
                    # Return original if not found
                    return match.group(0)
                
                processed_config[key] = re.sub(
                    r'\$\{([^}]+)\}',
                    substitute_var,
                    value
                )
            else:
                processed_config[key] = value
                
        return processed_config
        
    def save_servers_to_config(self, config_file: str = "configs/mcp_servers.json") -> bool:
        """
        Save current server configurations to a JSON file
        
        Args:
            config_file: Path to the JSON configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config = {
                "servers": {},
                "metadata": {
                    "version": "1.0.0",
                    "description": "Configuration for Docker MCP servers",
                    "instructions": "Add or remove server configurations here. Environment variables with ${VAR_NAME} will be automatically replaced with values from .env file."
                }
            }
            
            for server_name, server in self.servers.items():
                if hasattr(server, 'docker_image') and server.docker_image:
                    # Convert MCPServer to config format
                    server_config = {
                        "docker_image": server.docker_image,
                        "transport": server.transport,
                        "env_vars": server.env,
                        "description": f"MCP server: {server_name}"
                    }
                    
                    if server.docker_ports:
                        server_config["ports"] = server.docker_ports
                    if server.docker_volumes:
                        server_config["volumes"] = server.docker_volumes
                    if server.health_check_url:
                        server_config["health_check_url"] = server.health_check_url
                    if server.health_check_timeout != 30:
                        server_config["health_check_timeout"] = server.health_check_timeout
                        
                    config["servers"][server_name] = server_config
                    
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            self.logger.info(f"Saved server configurations to {config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration file {config_file}: {e}")
            return False
            
    def check_available_servers(self, config_file: str = "configs/mcp_servers.json") -> Dict[str, Dict[str, Any]]:
        """
        Check which servers are available based on environment variables
        
        Args:
            config_file: Path to the JSON configuration file
            
        Returns:
            Dict mapping server names to availability info
        """
        results = {}
        
        try:
            if not os.path.exists(config_file):
                self.logger.warning(f"Configuration file {config_file} not found")
                return results
                
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            servers_config = config.get('servers', {})
            
            for server_name, server_config in servers_config.items():
                env_vars = server_config.get('env_vars', {})
                missing_vars = []
                available_vars = []
                
                for key, value in env_vars.items():
                    if value.startswith('${') and value.endswith('}'):
                        env_var_name = value[2:-1]  # Remove ${ and }
                        if os.getenv(env_var_name):
                            available_vars.append(env_var_name)
                        else:
                            missing_vars.append(env_var_name)
                    else:
                        available_vars.append(key)
                
                results[server_name] = {
                    "available": len(missing_vars) == 0,
                    "missing_vars": missing_vars,
                    "available_vars": available_vars,
                    "description": server_config.get('description', ''),
                    "transport": server_config.get('transport', 'stdio'),
                    "docker_image": server_config.get('docker_image', '')
                }
                
        except Exception as e:
            self.logger.error(f"Failed to check available servers: {e}")
            
        return results 