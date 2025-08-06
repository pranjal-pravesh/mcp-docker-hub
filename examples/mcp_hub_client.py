#!/usr/bin/env python3
"""
Example MCP Hub Client
Demonstrates how to use the MCP Hub Server API from a client application.
"""
import asyncio
import aiohttp
import json
import sys
import os

# Add the mcps directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class MCPHubClient:
    """Client for interacting with the MCP Hub Server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_status(self):
        """Get hub server status"""
        async with self.session.get(f"{self.base_url}/") as response:
            return await response.json()
    
    async def list_servers(self):
        """List all MCP servers"""
        async with self.session.get(f"{self.base_url}/servers") as response:
            return await response.json()
    
    async def list_tools(self, server_name: str = None):
        """List all tools or tools from a specific server"""
        url = f"{self.base_url}/tools"
        if server_name:
            url = f"{self.base_url}/tools/{server_name}"
        
        async with self.session.get(url) as response:
            return await response.json()
    
    async def get_tool_info(self, tool_name: str):
        """Get detailed information about a tool"""
        async with self.session.get(f"{self.base_url}/tools/info/{tool_name}") as response:
            return await response.json()
    
    async def call_tool(self, tool_name: str, arguments: dict, timeout: int = 30):
        """Call a tool with arguments"""
        payload = {
            "tool_name": tool_name,
            "arguments": arguments,
            "timeout": timeout
        }
        
        async with self.session.post(f"{self.base_url}/tools/call", json=payload) as response:
            return await response.json()
    
    async def start_server(self, server_name: str):
        """Start a specific MCP server"""
        async with self.session.post(f"{self.base_url}/servers/{server_name}/start") as response:
            return await response.json()
    
    async def stop_server(self, server_name: str):
        """Stop a specific MCP server"""
        async with self.session.post(f"{self.base_url}/servers/{server_name}/stop") as response:
            return await response.json()
    
    async def start_all_servers(self):
        """Start all configured servers"""
        async with self.session.post(f"{self.base_url}/servers/start-all") as response:
            return await response.json()
    
    async def stop_all_servers(self):
        """Stop all servers"""
        async with self.session.post(f"{self.base_url}/servers/stop-all") as response:
            return await response.json()

async def demo_hub_client():
    """Demonstrate the MCP Hub Client functionality"""
    print("🚀 MCP Hub Client Demo")
    print("=" * 50)
    
    async with MCPHubClient() as client:
        try:
            # 1. Check server status
            print("\n1. 📊 Checking hub server status...")
            status = await client.get_status()
            print(f"   Status: {status['status']}")
            print(f"   Servers: {status['servers_count']}")
            print(f"   Tools: {status['tools_count']}")
            print(f"   Uptime: {status['uptime']:.2f}s")
            
            # 2. List servers
            print("\n2. 📋 Listing servers...")
            servers = await client.list_servers()
            for server in servers:
                print(f"   {server['name']}: {server['status']} ({server['tools_count']} tools)")
            
            # 3. Start all servers
            print("\n3. 🚀 Starting all servers...")
            start_result = await client.start_all_servers()
            print(f"   Result: {start_result}")
            
            # Wait a moment for servers to start
            await asyncio.sleep(2)
            
            # 4. List all tools
            print("\n4. 🛠️  Listing all tools...")
            tools = await client.list_tools()
            for tool in tools:
                print(f"   {tool['name']} ({tool['server_name']}): {tool['description']}")
            
            # 5. Get tool details
            if tools:
                print(f"\n5. 📖 Getting details for '{tools[0]['name']}'...")
                tool_info = await client.get_tool_info(tools[0]['name'])
                print(f"   Name: {tool_info['name']}")
                print(f"   Description: {tool_info['description']}")
                print(f"   Server: {tool_info['server_name']}")
                print(f"   Protocol: {tool_info['protocol']}")
            
            # 6. Try calling a tool (if available)
            if tools:
                print(f"\n6. ⚡ Calling tool '{tools[0]['name']}'...")
                try:
                    # Try with empty arguments first
                    result = await client.call_tool(tools[0]['name'], {})
                    if result['success']:
                        print(f"   ✅ Success! Result: {result['result']}")
                    else:
                        print(f"   ❌ Error: {result['error']}")
                except Exception as e:
                    print(f"   ❌ Failed to call tool: {e}")
            
            # 7. Check status again
            print("\n7. 📊 Final status check...")
            final_status = await client.get_status()
            print(f"   Active servers: {final_status['servers_count']}")
            print(f"   Available tools: {final_status['tools_count']}")
            
        except aiohttp.ClientError as e:
            print(f"❌ Connection error: {e}")
            print("Make sure the MCP Hub Server is running on http://localhost:8000")
        except Exception as e:
            print(f"❌ Error: {e}")

async def interactive_client():
    """Interactive client for testing the hub server"""
    print("🎮 Interactive MCP Hub Client")
    print("=" * 50)
    
    async with MCPHubClient() as client:
        while True:
            print("\nAvailable commands:")
            print("1. status - Check server status")
            print("2. servers - List all servers")
            print("3. tools [server] - List tools (optionally from specific server)")
            print("4. info <tool> - Get tool information")
            print("5. call <tool> <args> - Call a tool")
            print("6. start <server> - Start a server")
            print("7. stop <server> - Stop a server")
            print("8. start-all - Start all servers")
            print("9. stop-all - Stop all servers")
            print("10. quit - Exit")
            
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == "quit" or cmd == "exit":
                    break
                elif cmd == "status":
                    status = await client.get_status()
                    print(json.dumps(status, indent=2))
                elif cmd == "servers":
                    servers = await client.list_servers()
                    print(json.dumps(servers, indent=2))
                elif cmd == "tools":
                    server_name = command[1] if len(command) > 1 else None
                    tools = await client.list_tools(server_name)
                    print(json.dumps(tools, indent=2))
                elif cmd == "info" and len(command) > 1:
                    tool_info = await client.get_tool_info(command[1])
                    print(json.dumps(tool_info, indent=2))
                elif cmd == "call" and len(command) > 2:
                    tool_name = command[1]
                    try:
                        args = json.loads(command[2])
                        result = await client.call_tool(tool_name, args)
                        print(json.dumps(result, indent=2))
                    except json.JSONDecodeError:
                        print("❌ Invalid JSON arguments")
                elif cmd == "start" and len(command) > 1:
                    result = await client.start_server(command[1])
                    print(json.dumps(result, indent=2))
                elif cmd == "stop" and len(command) > 1:
                    result = await client.stop_server(command[1])
                    print(json.dumps(result, indent=2))
                elif cmd == "start-all":
                    result = await client.start_all_servers()
                    print(json.dumps(result, indent=2))
                elif cmd == "stop-all":
                    result = await client.stop_all_servers()
                    print(json.dumps(result, indent=2))
                else:
                    print("❌ Unknown command or missing arguments")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("👋 Goodbye!")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Hub Client")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--url", default="http://localhost:8000", help="Hub server URL")
    
    args = parser.parse_args()
    
    if args.demo:
        await demo_hub_client()
    elif args.interactive:
        await interactive_client()
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main()) 