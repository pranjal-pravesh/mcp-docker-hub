#!/usr/bin/env python3
"""
MCP Hub Server Runner
Runs the MCP Hub Server from the mcps directory
"""
import asyncio
import argparse
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_hub import MCPHubServer

async def main():
    parser = argparse.ArgumentParser(
        description="MCP Hub Server - Centralized API for all MCP tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start hub server with default settings
  python run_hub.py

  # Start with custom host and port
  python run_hub.py --host 127.0.0.1 --port 9000

  # Start and automatically add all available servers
  python run_hub.py --add-all-servers

  # Start with specific servers only
  python run_hub.py --add-slack --add-brave

  # Start in development mode (localhost only)
  python run_hub.py --dev
        """
    )
    
    parser.add_argument("--host", default="0.0.0.0", 
                       help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, 
                       help="Port to bind to (default: 8000)")
    parser.add_argument("--dev", action="store_true", 
                       help="Development mode (bind to localhost only)")
    parser.add_argument("--add-all-servers", action="store_true", 
                       help="Add all available servers on startup")
    parser.add_argument("--add-slack", action="store_true", 
                       help="Add Slack MCP server")
    parser.add_argument("--add-brave", action="store_true", 
                       help="Add Brave Search MCP server")
    parser.add_argument("--add-wolfram", action="store_true", 
                       help="Add Wolfram Alpha MCP server")
    parser.add_argument("--use-npx", action="store_true", 
                       help="Use NPX instead of Docker for servers")
    
    args = parser.parse_args()
    
    # Set host to localhost in dev mode
    if args.dev:
        args.host = "127.0.0.1"
    
    print(f"🚀 Starting MCP Hub Server on {args.host}:{args.port}")
    print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔍 Interactive API: http://{args.host}:{args.port}/redoc")
    
    # Create hub server
    hub = MCPHubServer(host=args.host, port=args.port)
    
    # Add servers based on arguments
    servers_added = []
    
    if args.add_all_servers:
        print("➕ Adding all available servers...")
        try:
            hub.mcp_manager.add_slack_server(use_docker=not args.use_npx)
            hub.mcp_manager.add_brave_search_server(use_docker=not args.use_npx)
            hub.mcp_manager.add_wolfram_alpha_server(use_docker=not args.use_npx)
            servers_added = ["slack", "brave-search", "wolfram-alpha"]
            print("✅ All servers added successfully")
        except Exception as e:
            print(f"⚠️  Some servers could not be added: {e}")
    else:
        # Add individual servers
        if args.add_slack:
            try:
                hub.mcp_manager.add_slack_server(use_docker=not args.use_npx)
                servers_added.append("slack")
                print("✅ Slack server added")
            except Exception as e:
                print(f"❌ Failed to add Slack server: {e}")
        
        if args.add_brave:
            try:
                hub.mcp_manager.add_brave_search_server(use_docker=not args.use_npx)
                servers_added.append("brave-search")
                print("✅ Brave Search server added")
            except Exception as e:
                print(f"❌ Failed to add Brave Search server: {e}")
        
        if args.add_wolfram:
            try:
                hub.mcp_manager.add_wolfram_alpha_server(use_docker=not args.use_npx)
                servers_added.append("wolfram-alpha")
                print("✅ Wolfram Alpha server added")
            except Exception as e:
                print(f"❌ Failed to add Wolfram Alpha server: {e}")
    
    if servers_added:
        print(f"📋 Configured servers: {', '.join(servers_added)}")
        print("💡 Use the API to start servers: POST /servers/start-all")
    
    print("\n" + "="*50)
    print("🎯 Available API Endpoints:")
    print("  GET  /                    - Server status")
    print("  GET  /servers             - List all servers")
    print("  GET  /tools               - List all tools")
    print("  GET  /tools/qwen          - Get tools in Qwen format")
    print("  GET  /tools/qwen?required_only=true - Get tools with required params only")
    print("  GET  /tools/{server}      - List tools from server")
    print("  GET  /tools/info/{tool}   - Get tool details")
    print("  POST /tools/call          - Call a tool")
    print("  POST /servers/{name}/start - Start a server")
    print("  POST /servers/{name}/stop  - Stop a server")
    print("  POST /servers/start-all   - Start all servers")
    print("  POST /servers/stop-all    - Stop all servers")
    print("="*50)
    
    try:
        await hub.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down MCP Hub Server...")
        await hub.mcp_manager.stop_all_servers()
        print("✅ Server stopped")

if __name__ == "__main__":
    asyncio.run(main()) 