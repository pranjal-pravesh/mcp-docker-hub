#!/usr/bin/env python3
"""
MCP Server Management CLI
A simple command-line interface for managing Docker MCP servers
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Try to import MCPManager, but handle missing dependencies gracefully
try:
    from mcp_hub.mcp_manager import MCPManager
    MCP_MANAGER_AVAILABLE = True
except ImportError as e:
    MCP_MANAGER_AVAILABLE = False
    print(f"⚠️  Warning: Could not import MCPManager: {e}")
    print("   Some commands may not work without installing dependencies.")
    print("   Run: pip install -r requirements.txt")

def add_server(args):
    """Add a new Docker MCP server"""
    manager = MCPManager()
    
    # Load existing configuration
    config_file = args.config_file
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {"servers": {}, "metadata": {"version": "1.0.0"}}
    
    # Create server configuration
    server_config = {
        "docker_image": args.docker_image,
        "transport": args.transport,
        "env_vars": {},
        "description": args.description or f"MCP server: {args.name}"
    }
    
    # Add environment variables
    if args.env_vars:
        for env_var in args.env_vars:
            if '=' in env_var:
                key, value = env_var.split('=', 1)
                server_config["env_vars"][key] = value
            else:
                # Treat as environment variable reference
                server_config["env_vars"][env_var] = f"${{{env_var}}}"
    
    # Add ports
    if args.ports:
        server_config["ports"] = args.ports
    
    # Add volumes
    if args.volumes:
        server_config["volumes"] = args.volumes
    
    # Add health check URL
    if args.health_check_url:
        server_config["health_check_url"] = args.health_check_url
    
    # Add to configuration
    config["servers"][args.name] = server_config
    
    # Save configuration
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Added server '{args.name}' to configuration")
    print(f"   Image: {args.docker_image}")
    print(f"   Transport: {args.transport}")
    if server_config["env_vars"]:
        print(f"   Environment variables: {list(server_config['env_vars'].keys())}")

def remove_server(args):
    """Remove a Docker MCP server"""
    config_file = args.config_file
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file {config_file} not found")
        return
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    if args.name in config["servers"]:
        del config["servers"][args.name]
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Removed server '{args.name}' from configuration")
    else:
        print(f"❌ Server '{args.name}' not found in configuration")

def list_servers(args):
    """List all configured servers"""
    config_file = args.config_file
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file {config_file} not found")
        return
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    servers = config.get("servers", {})
    
    if not servers:
        print("No servers configured")
        return
    
    print(f"📋 Configured servers ({len(servers)}):")
    print()
    
    for name, server_config in servers.items():
        print(f"🔧 {name}")
        print(f"   Image: {server_config.get('docker_image', 'N/A')}")
        print(f"   Transport: {server_config.get('transport', 'stdio')}")
        print(f"   Description: {server_config.get('description', 'No description')}")
        
        env_vars = server_config.get('env_vars', {})
        if env_vars:
            print(f"   Environment: {list(env_vars.keys())}")
        
        ports = server_config.get('ports')
        if ports:
            print(f"   Ports: {ports}")
        
        print()

def show_server(args):
    """Show detailed configuration for a specific server"""
    config_file = args.config_file
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file {config_file} not found")
        return
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    servers = config.get("servers", {})
    
    if args.name not in servers:
        print(f"❌ Server '{args.name}' not found")
        return
    
    server_config = servers[args.name]
    
    print(f"🔧 Server: {args.name}")
    print(f"   Image: {server_config.get('docker_image', 'N/A')}")
    print(f"   Transport: {server_config.get('transport', 'stdio')}")
    print(f"   Description: {server_config.get('description', 'No description')}")
    
    env_vars = server_config.get('env_vars', {})
    if env_vars:
        print(f"   Environment Variables:")
        for key, value in env_vars.items():
            print(f"     {key}: {value}")
    
    ports = server_config.get('ports')
    if ports:
        print(f"   Ports: {ports}")
    
    volumes = server_config.get('volumes')
    if volumes:
        print(f"   Volumes: {volumes}")
    
    health_check = server_config.get('health_check_url')
    if health_check:
        print(f"   Health Check: {health_check}")

def check_availability(args):
    """Check which servers are available based on environment variables"""
    if not MCP_MANAGER_AVAILABLE:
        print("❌ MCPManager not available. Please install dependencies first:")
        print("   pip install -r requirements.txt")
        return
    
    manager = MCPManager()
    availability = manager.check_available_servers(args.config_file)
    
    if not availability:
        print("❌ No servers found in configuration")
        return
    
    # Count available and unavailable servers
    available_count = sum(1 for info in availability.values() if info["available"])
    total_count = len(availability)
    
    print(f"📋 Server Availability Check")
    print(f"   Total servers: {total_count}")
    print(f"   Available: {available_count}")
    print(f"   Unavailable: {total_count - available_count}")
    print()
    
    for server_name, info in availability.items():
        status = "✅" if info["available"] else "❌"
        print(f"{status} {server_name}")
        print(f"   Description: {info['description']}")
        print(f"   Transport: {info['transport']}")
        print(f"   Image: {info['docker_image']}")
        
        if info["available"]:
            if info["available_vars"]:
                print(f"   Environment: {', '.join(info['available_vars'])}")
        else:
            if info["missing_vars"]:
                print(f"   Missing: {', '.join(info['missing_vars'])}")
        
        print()

def main():
    parser = argparse.ArgumentParser(
        description="Manage Docker MCP servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a new server
  python manage_mcp_servers.py add my-server mcp/slack --env-vars SLACK_BOT_TOKEN SLACK_TEAM_ID
  
  # Add a server with ports
  python manage_mcp_servers.py add brave mcp/brave-search --transport http --ports 8080:8080 --health-check-url http://localhost:8080/
  
  # Remove a server
  python manage_mcp_servers.py remove my-server
  
  # List all servers
  python manage_mcp_servers.py list
  
  # Show server details
  python manage_mcp_servers.py show my-server
        """
    )
    
    parser.add_argument(
        "--config-file",
        default="configs/mcp_servers.json",
        help="Path to server configuration file"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new server")
    add_parser.add_argument("name", help="Server name")
    add_parser.add_argument("docker_image", help="Docker image name")
    add_parser.add_argument("--transport", default="stdio", choices=["stdio", "http", "sse"], help="Transport type")
    add_parser.add_argument("--env-vars", nargs="*", help="Environment variables (KEY or KEY=value)")
    add_parser.add_argument("--ports", nargs="*", help="Port mappings (host:container)")
    add_parser.add_argument("--volumes", nargs="*", help="Volume mappings (host:container)")
    add_parser.add_argument("--health-check-url", help="Health check URL for HTTP transport")
    add_parser.add_argument("--description", help="Server description")
    add_parser.set_defaults(func=add_server)
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a server")
    remove_parser.add_argument("name", help="Server name")
    remove_parser.set_defaults(func=remove_server)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all servers")
    list_parser.set_defaults(func=list_servers)
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show server details")
    show_parser.add_argument("name", help="Server name")
    show_parser.set_defaults(func=show_server)

    # Check availability command
    check_parser = subparsers.add_parser("check-availability", help="Check which servers are available based on environment variables")
    check_parser.set_defaults(func=check_availability)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 