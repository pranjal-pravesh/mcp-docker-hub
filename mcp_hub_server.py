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
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from datetime import datetime
import time

from mcp_manager import MCPManager
from tool_adapter import ToolHub

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class ToolCallRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    timeout: Optional[int] = Field(30, description="Timeout in seconds")

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
        
        # Register routes
        self._register_routes()
        
    def _register_routes(self):
        """Register all API routes"""
        
        @self.app.get("/", response_model=HubStatus)
        async def get_status():
            """Get hub server status"""
            uptime = time.time() - self.start_time
            servers_count = len(self.mcp_manager.active_connections)
            tools_count = len(self.tool_hub.tool_registry)
            
            return HubStatus(
                status="running",
                servers_count=servers_count,
                tools_count=tools_count,
                uptime=uptime
            )
        
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
        async def list_tools():
            """List all available tools from all servers"""
            tools = []
            
            for tool_name, metadata in self.tool_hub.tool_registry.items():
                tools.append(ToolInfo(
                    name=metadata.name,
                    description=metadata.description,
                    server_name=metadata.server_name,
                    protocol=metadata.protocol.value,
                    input_schema=metadata.input_schema
                ))
            
            return tools
        
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
    
    args = parser.parse_args()
    
    # Create and start hub server
    hub = MCPHubServer(host=args.host, port=args.port)
    
    # Add servers if requested
    if args.add_all_servers:
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