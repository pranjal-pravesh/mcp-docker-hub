"""
MCP Hub Server - Centralized API for all MCP tools
Provides a unified HTTP interface for external clients to discover and call tools
from all running MCP servers.
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from datetime import datetime
import time

from .mcp_manager import MCPManager
from .tool_adapter import ToolHub

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class ToolCallRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    timeout: Optional[int] = Field(30, description="Timeout in seconds")

class ToolConfigRequest(BaseModel):
    enabled_tools: List[str] = Field(..., description="List of enabled tool names")

class ToolCallResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float
    timestamp: str

class ToolInfo(BaseModel):
    name: str
    description: str
    server_name: str
    protocol: str
    input_schema: Dict[str, Any]

class ServerInfo(BaseModel):
    name: str
    status: str
    transport: str
    tools_count: int
    last_updated: str

class HubStatus(BaseModel):
    status: str
    servers_count: int
    tools_count: int
    uptime: float
    version: str = "1.0.0"

class MCPHubServer:
    """Centralized hub server for all MCP tools"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.start_time = time.time()
        
        # Initialize MCP manager
        self.mcp_manager = MCPManager()
        self.tool_hub = self.mcp_manager.tool_hub
        
        # Load tool configuration on startup
        self._load_tool_config()
        
    def _load_tool_config(self):
        """Load tool configuration from file on startup"""
        try:
            with open("configs/tool_config.json", "r") as f:
                config_data = json.load(f)
                self.mcp_manager.enabled_tools = set(config_data.get("enabled_tools", []))
                logger.info(f"Loaded tool configuration: {len(self.mcp_manager.enabled_tools)} tools enabled")
        except FileNotFoundError:
            logger.info("No tool configuration file found, starting with all tools disabled")
            self.mcp_manager.enabled_tools = set()
        except Exception as e:
            logger.warning(f"Error loading tool configuration: {e}")
            self.mcp_manager.enabled_tools = set()
        
        # Create FastAPI app
        self.app = FastAPI(
            title="MCP Hub Server",
            description="Centralized API for all MCP tools",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Mount static files with no caching
        self.app.mount("/static", StaticFiles(directory="src/mcp_hub/static", check_dir=False), name="static")
        
        # Register routes
        self._register_routes()
        
    def _register_routes(self):
        """Register all API routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """Serve the web interface"""
            try:
                with open("src/mcp_hub/static/index.html", "r") as f:
                    return HTMLResponse(
                        content=f.read(),
                        headers={
                            "Cache-Control": "no-cache, no-store, must-revalidate",
                            "Pragma": "no-cache",
                            "Expires": "0"
                        }
                    )
            except FileNotFoundError:
                return HTMLResponse(content="""
                <html>
                    <head><title>MCP Hub</title></head>
                    <body>
                        <h1>MCP Hub Server</h1>
                        <p>Server is running! Check the <a href="/docs">API documentation</a>.</p>
                    </body>
                </html>
                """)

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "message": "MCP Hub is running"}

        @self.app.get("/servers", response_model=List[ServerInfo])
        async def list_servers():
            """List all MCP servers and their status"""
            servers = []
            
            for server_name, server in self.mcp_manager.servers.items():
                is_active = server_name in self.mcp_manager.active_connections
                tools_count = len(self.mcp_manager.get_server_tools(server_name))
                
                servers.append(ServerInfo(
                    name=server_name,
                    status="active" if is_active else "inactive",
                    transport=server.transport,
                    tools_count=tools_count,
                    last_updated=datetime.now().isoformat()
                ))
            
            return servers
        
        @self.app.get("/tools", response_model=List[ToolInfo])
        async def list_tools(enabled_only: bool = False):
            """List available tools from all servers"""
            tools = []
            
            for tool_name, metadata in self.tool_hub.tool_registry.items():
                # If enabled_only is True, only return enabled tools
                if enabled_only and tool_name not in self.mcp_manager.enabled_tools:
                    continue
                    
                tools.append(ToolInfo(
                    name=metadata.name,
                    description=metadata.description,
                    server_name=metadata.server_name,
                    protocol=metadata.protocol.value,
                    input_schema=metadata.input_schema
                ))
            
            return tools
        
        @self.app.get("/tools/qwen")
        async def get_tools_qwen_format():
            """
            Get enabled tools in Qwen format (JSON lines without prompt)
            
            Returns:
                Plain text with one JSON object per line, each containing:
                {"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}
                
            This format is ready to be inserted into a Qwen system prompt between <tools></tools> tags.
            """
            qwen_tools = []
            
            for tool_name, metadata in self.tool_hub.tool_registry.items():
                # Only return enabled tools
                if tool_name not in self.mcp_manager.enabled_tools:
                    continue
                
                # Convert input_schema to parameters format for Qwen
                parameters = metadata.input_schema.copy()
                
                # Create Qwen format tool object
                qwen_tool = {
                    "type": "function",
                    "function": {
                        "name": metadata.name,
                        "description": metadata.description,
                        "parameters": parameters
                    }
                }
                
                qwen_tools.append(qwen_tool)
            
            # Return as plain text with one JSON object per line
            content = "\n".join(json.dumps(tool) for tool in qwen_tools)
            return Response(
                content=content,
                media_type="text/plain"
            )
        
        @self.app.get("/tools/config")
        async def get_tool_config():
            """Get current tool configuration"""
            try:
                # Return the current in-memory configuration
                return {
                    "enabled_tools": list(self.mcp_manager.enabled_tools),
                    "last_updated": datetime.now().isoformat()
                }
                    
            except Exception as e:
                logger.error(f"Error getting tool configuration: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tools/{server_name}", response_model=List[ToolInfo])
        async def list_server_tools(server_name: str):
            """List tools from a specific server"""
            tools = []
            
            for tool_name, metadata in self.tool_hub.tool_registry.items():
                if metadata.server_name == server_name:
                    tools.append(ToolInfo(
                        name=metadata.name,
                        description=metadata.description,
                        server_name=metadata.server_name,
                        protocol=metadata.protocol.value,
                        input_schema=metadata.input_schema
                    ))
            
            return tools
        
        @self.app.get("/tools/info/{tool_name}", response_model=ToolInfo)
        async def get_tool_info(tool_name: str):
            """Get detailed information about a specific tool"""
            metadata = self.tool_hub.get_tool_info(tool_name)
            if not metadata:
                raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
            
            return ToolInfo(
                name=metadata["name"],
                description=metadata["description"],
                server_name=metadata["server_name"],
                protocol=metadata["protocol"],
                input_schema=metadata["inputSchema"]
            )
        
        @self.app.post("/tools/call", response_model=ToolCallResponse)
        async def call_tool(request: ToolCallRequest, background_tasks: BackgroundTasks):
            """Call a tool with the given arguments"""
            start_time = time.time()
            
            try:
                # Check if tool exists
                if request.tool_name not in self.tool_hub.tool_registry:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Tool '{request.tool_name}' not found"
                    )
                
                # Call the tool with timeout
                if request.timeout:
                    result = await asyncio.wait_for(
                        self.tool_hub.call_tool(request.tool_name, request.arguments),
                        timeout=request.timeout
                    )
                else:
                    result = await self.tool_hub.call_tool(request.tool_name, request.arguments)
                
                execution_time = time.time() - start_time
                
                if result and result.get("error"):
                    return ToolCallResponse(
                        success=False,
                        error=result["error"],
                        execution_time=execution_time,
                        timestamp=datetime.now().isoformat()
                    )
                
                return ToolCallResponse(
                    success=True,
                    result=result.get("result") if result else None,
                    execution_time=execution_time,
                    timestamp=datetime.now().isoformat()
                )
                
            except asyncio.TimeoutError:
                execution_time = time.time() - start_time
                return ToolCallResponse(
                    success=False,
                    error="Tool execution timed out",
                    execution_time=execution_time,
                    timestamp=datetime.now().isoformat()
                )
            except Exception as e:
                execution_time = time.time() - start_time
                return ToolCallResponse(
                    success=False,
                    error=str(e),
                    execution_time=execution_time,
                    timestamp=datetime.now().isoformat()
                )
        
        @self.app.post("/servers/{server_name}/start")
        async def start_server(server_name: str):
            """Start a specific MCP server"""
            try:
                success = await self.mcp_manager.start_server(server_name)
                if success:
                    return {"message": f"Server '{server_name}' started successfully"}
                else:
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Failed to start server '{server_name}'"
                    )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/servers/{server_name}/stop")
        async def stop_server(server_name: str):
            """Stop a specific MCP server"""
            try:
                await self.mcp_manager.stop_server(server_name)
                return {"message": f"Server '{server_name}' stopped successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/servers/start-all")
        async def start_all_servers():
            """Start all configured MCP servers"""
            try:
                results = await self.mcp_manager.start_all_servers()
                return {
                    "message": "Started all servers",
                    "results": results
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/servers/stop-all")
        async def stop_all_servers():
            """Stop all MCP servers"""
            try:
                await self.mcp_manager.stop_all_servers()
                return {"message": "Stopped all servers"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/servers/add-slack")
        async def add_slack_server(use_docker: bool = True):
            """Add Slack MCP server"""
            try:
                self.mcp_manager.add_slack_server(use_docker=use_docker)
                return {"message": f"Slack server added (using {'Docker' if use_docker else 'NPX'})"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/servers/add-brave")
        async def add_brave_server(use_docker: bool = False):
            """Add Brave Search MCP server"""
            try:
                self.mcp_manager.add_brave_search_server(use_docker=use_docker)
                return {"message": f"Brave Search server added (using {'Docker' if use_docker else 'NPX'})"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/servers/add-wolfram")
        async def add_wolfram_server(use_docker: bool = True):
            """Add Wolfram Alpha MCP server"""
            try:
                self.mcp_manager.add_wolfram_alpha_server(use_docker=use_docker)
                return {"message": f"Wolfram Alpha server added (using {'Docker' if use_docker else 'NPX'})"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # New dynamic Docker MCP server management endpoints
        @self.app.post("/servers/add-docker")
        async def add_docker_server(
            name: str,
            docker_image: str,
            transport: str = "stdio",
            env_vars: Dict[str, str] = None,
            ports: List[str] = None,
            volumes: List[str] = None,
            health_check_url: str = None,
            health_check_timeout: int = 30
        ):
            """Add any Docker MCP server dynamically"""
            try:
                self.mcp_manager.add_docker_mcp_server(
                    name=name,
                    docker_image=docker_image,
                    env_vars=env_vars or {},
                    transport=transport,
                    ports=ports,
                    volumes=volumes,
                    health_check_url=health_check_url,
                    health_check_timeout=health_check_timeout
                )
                return {"message": f"Docker MCP server '{name}' added successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/servers/{server_name}")
        async def remove_server(server_name: str):
            """Remove an MCP server configuration"""
            try:
                # Stop the server if it's running
                if server_name in self.mcp_manager.active_connections:
                    await self.mcp_manager.stop_server(server_name)
                
                # Remove the configuration
                success = self.mcp_manager.remove_server(server_name)
                if success:
                    return {"message": f"Server '{server_name}' removed successfully"}
                else:
                    raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/servers/configured")
        async def list_configured_servers():
            """List all configured server names"""
            try:
                servers = self.mcp_manager.list_configured_servers()
                return {"servers": servers, "count": len(servers)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/servers/config/{server_name}")
        async def get_server_config(server_name: str):
            """Get configuration for a specific server"""
            try:
                config = self.mcp_manager.get_server_config(server_name)
                if config:
                    return {
                        "name": config.name,
                        "docker_image": getattr(config, 'docker_image', None),
                        "transport": config.transport,
                        "env_vars": config.env,
                        "ports": getattr(config, 'docker_ports', None),
                        "volumes": getattr(config, 'docker_volumes', None),
                        "health_check_url": getattr(config, 'health_check_url', None)
                    }
                else:
                    raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/servers/load-config")
        async def load_servers_from_config(config_file: str = "configs/mcp_servers.json"):
            """Load server configurations from JSON file"""
            try:
                results = self.mcp_manager.load_servers_from_config(config_file)
                success_count = sum(1 for success in results.values() if success)
                total_count = len(results)
                
                return {
                    "message": f"Loaded {success_count}/{total_count} servers from config",
                    "results": results
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/servers/save-config")
        async def save_servers_to_config(config_file: str = "configs/mcp_servers.json"):
            """Save current server configurations to JSON file"""
            try:
                success = self.mcp_manager.save_servers_to_config(config_file)
                if success:
                    return {"message": f"Server configurations saved to {config_file}"}
                else:
                    raise HTTPException(status_code=500, detail="Failed to save configuration")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/servers/check-availability")
        async def check_server_availability(config_file: str = "configs/mcp_servers.json"):
            """Check which servers are available based on environment variables"""
            try:
                availability = self.mcp_manager.check_available_servers(config_file)
                
                # Count available and unavailable servers
                available_count = sum(1 for info in availability.values() if info["available"])
                total_count = len(availability)
                
                return {
                    "total_servers": total_count,
                    "available_servers": available_count,
                    "unavailable_servers": total_count - available_count,
                    "servers": availability
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/tools/save-config")
        async def save_tool_config(request: ToolConfigRequest):
            """Save tool configuration (which tools are enabled/disabled)"""
            try:
                # Store the enabled tools configuration
                self.mcp_manager.enabled_tools = set(request.enabled_tools)
                
                # Save to a configuration file for persistence
                config_data = {
                    "enabled_tools": request.enabled_tools,
                    "last_updated": datetime.now().isoformat()
                }
                
                with open("configs/tool_config.json", "w") as f:
                    json.dump(config_data, f, indent=2)
                
                logger.info(f"Saved tool configuration: {len(request.enabled_tools)} tools enabled")
                return {"success": True, "enabled_tools_count": len(request.enabled_tools)}
                
            except Exception as e:
                logger.error(f"Error saving tool configuration: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def start(self):
        """Start the hub server"""
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def run(self):
        """Run the hub server (blocking)"""
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )

async def main():
    """Main entry point for the hub server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Hub Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--add-all-servers", action="store_true", help="Add all available servers on startup")
    parser.add_argument("--load-config", action="store_true", help="Load servers from config file on startup")
    parser.add_argument("--config-file", default="configs/mcp_servers.json", help="Path to server configuration file")
    
    args = parser.parse_args()
    
    # Create and start hub server
    hub = MCPHubServer(host=args.host, port=args.port)
    
    # Load servers from configuration file if requested
    if args.load_config:
        logger.info(f"Loading servers from configuration file: {args.config_file}")
        try:
            results = hub.mcp_manager.load_servers_from_config(args.config_file)
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            logger.info(f"Loaded {success_count}/{total_count} servers from configuration")
            
            # Start all loaded servers
            if results:
                logger.info("Starting all loaded servers...")
                start_results = await hub.mcp_manager.start_all_servers()
                started_count = sum(1 for success in start_results.values() if success)
                logger.info(f"Started {started_count}/{len(start_results)} servers")
                
        except Exception as e:
            logger.warning(f"Failed to load servers from configuration: {e}")
    
    # Add legacy servers if requested
    elif args.add_all_servers:
        logger.info("Adding all available servers...")
        try:
            hub.mcp_manager.add_slack_server()
            hub.mcp_manager.add_brave_search_server()
            hub.mcp_manager.add_wolfram_alpha_server()
            logger.info("All servers added successfully")
        except Exception as e:
            logger.warning(f"Some servers could not be added: {e}")
    
    logger.info(f"Starting MCP Hub Server on {args.host}:{args.port}")
    logger.info("API documentation available at http://localhost:8000/docs")
    
    await hub.start()

if __name__ == "__main__":
    asyncio.run(main()) 