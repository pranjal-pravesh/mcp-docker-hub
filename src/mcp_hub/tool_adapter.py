"""
Unified Tool Adapter Layer for MCP Servers
Handles both HTTP and stdio protocols transparently
"""
import asyncio
import json
import logging
import subprocess
import time
from typing import Dict, List, Any, Optional, Union
import httpx
from dataclasses import dataclass
from enum import Enum

class ProtocolType(Enum):
    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"

@dataclass
class ToolMetadata:
    """Metadata for a tool including protocol and connection details"""
    name: str
    description: str
    protocol: ProtocolType
    server_name: str
    input_schema: Dict[str, Any]
    # Protocol-specific details
    endpoint: Optional[str] = None  # For HTTP/SSE
    process: Optional[Any] = None   # For stdio
    base_url: Optional[str] = None  # For HTTP/SSE

class ToolHub:
    """
    Unified Tool Hub that provides a consistent interface for all MCP tools
    regardless of their underlying protocol (stdio, HTTP, SSE)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tool_registry: Dict[str, ToolMetadata] = {}
        self.active_connections: Dict[str, Any] = {}
        
    def register_stdio_tools(self, server_name: str, tools: List[Dict], process: Any):
        """Register tools from a stdio MCP server"""
        for tool in tools:
            tool_name = tool.get('name')
            if tool_name:
                metadata = ToolMetadata(
                    name=tool_name,
                    description=tool.get('description', ''),
                    protocol=ProtocolType.STDIO,
                    server_name=server_name,
                    input_schema=tool.get('inputSchema', {}),
                    process=process
                )
                self.tool_registry[tool_name] = metadata
                self.logger.info(f"Registered stdio tool: {tool_name}")
    
    def register_http_tools(self, server_name: str, base_url: str, tools: List[Dict]):
        """Register tools from an HTTP MCP server"""
        for tool in tools:
            tool_name = tool.get('name')
            if tool_name:
                metadata = ToolMetadata(
                    name=tool_name,
                    description=tool.get('description', ''),
                    protocol=ProtocolType.HTTP,
                    server_name=server_name,
                    input_schema=tool.get('inputSchema', {}),
                    base_url=base_url,
                    endpoint=f"/tools/{tool_name}"
                )
                self.tool_registry[tool_name] = metadata
                self.logger.info(f"Registered HTTP tool: {tool_name}")
    
    async def discover_http_tools(self, server_name: str, base_url: str) -> List[Dict]:
        """Discover tools from an HTTP MCP server"""
        try:
            async with httpx.AsyncClient() as client:
                # Check if this is an SSE server first
                try:
                    headers = {"Accept": "application/json, text/event-stream"}
                    async with client.stream("GET", f"{base_url}/mcp", headers=headers) as response:
                        if response.status_code == 200:
                            # This is an SSE server, handle it differently
                            return await self._discover_sse_tools(server_name, base_url)
                except Exception:
                    pass
                
                # Try different common endpoints for tool discovery
                endpoints_to_try = [
                    f"{base_url}/tools/list",
                    f"{base_url}/mcp/tools",
                    f"{base_url}/api/tools",
                    f"{base_url}/tools"
                ]
                
                for endpoint in endpoints_to_try:
                    try:
                        response = await client.post(endpoint, json={
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "tools/list"
                        })
                        
                        if response.status_code == 200:
                            data = response.json()
                            if "result" in data and "tools" in data["result"]:
                                tools = data["result"]["tools"]
                                self.register_http_tools(server_name, base_url, tools)
                                return tools
                    except Exception as e:
                        self.logger.debug(f"Failed to discover tools at {endpoint}: {e}")
                        continue
                        
                # Try a simple GET request to see if it's a REST API
                try:
                    response = await client.get(f"{base_url}/tools")
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            self.register_http_tools(server_name, base_url, data)
                            return data
                except Exception:
                    pass
                    
                self.logger.warning(f"Could not discover tools from HTTP server at {base_url}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to discover HTTP tools: {e}")
            return []
    
    async def _discover_sse_tools(self, server_name: str, base_url: str) -> List[Dict]:
        """Discover tools from an SSE MCP server"""
        try:
            import json
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json"
                }
                
                # Initialize MCP connection
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
                
                # Send initialization via SSE
                async with client.stream("POST", f"{base_url}/mcp", 
                                       headers=headers, 
                                       json=init_request) as response:
                    
                    if response.status_code == 200:
                        # Read the SSE response
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                try:
                                    init_response = json.loads(data)
                                    if init_response.get("result"):
                                        # Initialization successful, now list tools
                                        break
                                except json.JSONDecodeError:
                                    continue
                
                # Now request tools list
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
                
                async with client.stream("POST", f"{base_url}/mcp", 
                                       headers=headers, 
                                       json=tools_request) as response:
                    
                    if response.status_code == 200:
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                try:
                                    tools_response = json.loads(data)
                                    if "result" in tools_response and "tools" in tools_response["result"]:
                                        tools = tools_response["result"]["tools"]
                                        self.register_sse_tools(server_name, base_url, tools)
                                        return tools
                                except json.JSONDecodeError:
                                    continue
                
                self.logger.warning(f"Could not discover tools from SSE server at {base_url}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to discover SSE tools: {e}")
            return []
    
    def register_sse_tools(self, server_name: str, base_url: str, tools: List[Dict]):
        """Register tools from an SSE MCP server"""
        for tool in tools:
            tool_name = tool.get('name')
            if tool_name:
                metadata = ToolMetadata(
                    name=tool_name,
                    description=tool.get('description', ''),
                    protocol=ProtocolType.SSE,
                    server_name=server_name,
                    input_schema=tool.get('inputSchema', {}),
                    base_url=base_url,
                    endpoint="/mcp"
                )
                self.tool_registry[tool_name] = metadata
                self.logger.info(f"Registered SSE tool: {tool_name}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict]:
        """
        Unified tool calling interface - handles any protocol transparently
        """
        if tool_name not in self.tool_registry:
            self.logger.error(f"Tool {tool_name} not found in registry")
            return None
        
        metadata = self.tool_registry[tool_name]
        
        try:
            if metadata.protocol == ProtocolType.STDIO:
                return await self._call_stdio_tool(metadata, arguments)
            elif metadata.protocol == ProtocolType.HTTP:
                return await self._call_http_tool(metadata, arguments)
            elif metadata.protocol == ProtocolType.SSE:
                return await self._call_sse_tool(metadata, arguments)
            else:
                self.logger.error(f"Unsupported protocol: {metadata.protocol}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to call tool {tool_name}: {e}")
            return None
    
    async def _call_stdio_tool(self, metadata: ToolMetadata, arguments: Dict) -> Optional[Dict]:
        """Call a tool via stdio protocol"""
        if not metadata.process:
            self.logger.error(f"No process available for stdio tool {metadata.name}")
            return None
        
        # Check if process is still alive
        if metadata.process.returncode is not None:
            self.logger.error(f"Process for {metadata.name} has terminated")
            return None
        
        # Prepare MCP tool call request
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "tools/call",
            "params": {
                "name": metadata.name,
                "arguments": arguments
            }
        }
        
        # Send request via stdin
        request_data = json.dumps(request) + "\n"
        metadata.process.stdin.write(request_data.encode())
        await metadata.process.stdin.drain()
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(
                metadata.process.stdout.readline(), 
                timeout=30.0
            )
            
            if response_line:
                response_text = response_line.decode().strip()
                return json.loads(response_text)
            else:
                self.logger.error(f"No response from stdio tool {metadata.name}")
                return None
                
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout calling stdio tool {metadata.name}")
            return None
    
    async def _call_http_tool(self, metadata: ToolMetadata, arguments: Dict) -> Optional[Dict]:
        """Call a tool via HTTP protocol"""
        if not metadata.base_url:
            self.logger.error(f"No base URL for HTTP tool {metadata.name}")
            return None
        
        async with httpx.AsyncClient() as client:
            # Try MCP-style request first
            mcp_request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": "tools/call",
                "params": {
                    "name": metadata.name,
                    "arguments": arguments
                }
            }
            
            endpoints_to_try = [
                f"{metadata.base_url}/mcp",
                f"{metadata.base_url}/tools/call",
                f"{metadata.base_url}/api/tools/{metadata.name}",
                f"{metadata.base_url}/tools/{metadata.name}"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    # Try POST with MCP format
                    response = await client.post(endpoint, json=mcp_request)
                    if response.status_code == 200:
                        return response.json()
                    
                    # Try POST with direct arguments
                    response = await client.post(endpoint, json=arguments)
                    if response.status_code == 200:
                        return {"result": response.json()}
                        
                except Exception as e:
                    self.logger.debug(f"Failed to call {endpoint}: {e}")
                    continue
            
            self.logger.error(f"Could not call HTTP tool {metadata.name}")
            return None
    
    async def _call_sse_tool(self, metadata: ToolMetadata, arguments: Dict) -> Optional[Dict]:
        """Call a tool via SSE protocol"""
        if not metadata.base_url:
            self.logger.error(f"No base URL for SSE tool {metadata.name}")
            return None
        
        try:
            import json
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json"
                }
                
                # Prepare tool call request
                request = {
                    "jsonrpc": "2.0",
                    "id": int(time.time()),
                    "method": "tools/call",
                    "params": {
                        "name": metadata.name,
                        "arguments": arguments
                    }
                }
                
                async with client.stream("POST", f"{metadata.base_url}/mcp", 
                                       headers=headers, 
                                       json=request,
                                       timeout=30.0) as response:
                    
                    if response.status_code == 200:
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                try:
                                    result = json.loads(data)
                                    if "result" in result or "error" in result:
                                        return result
                                except json.JSONDecodeError:
                                    continue
                    
                    self.logger.error(f"SSE tool {metadata.name} returned status {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Failed to call SSE tool {metadata.name}: {e}")
            return None
    
    def get_all_tools(self) -> Dict[str, List[Dict]]:
        """Get all registered tools grouped by server"""
        tools_by_server = {}
        
        for tool_name, metadata in self.tool_registry.items():
            server_name = metadata.server_name
            if server_name not in tools_by_server:
                tools_by_server[server_name] = []
            
            tools_by_server[server_name].append({
                "name": metadata.name,
                "description": metadata.description,
                "inputSchema": metadata.input_schema,
                "protocol": metadata.protocol.value
            })
        
        return tools_by_server
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get detailed info about a specific tool"""
        if tool_name not in self.tool_registry:
            return None
            
        metadata = self.tool_registry[tool_name]
        return {
            "name": metadata.name,
            "description": metadata.description,
            "protocol": metadata.protocol.value,
            "server_name": metadata.server_name,
            "inputSchema": metadata.input_schema
        }
    
    def list_tools(self) -> List[str]:
        """Get a simple list of all available tool names"""
        return list(self.tool_registry.keys()) 