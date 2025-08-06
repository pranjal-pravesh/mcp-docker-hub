#!/usr/bin/env python3
"""
Standalone Server Availability Checker
Checks which MCP servers are available based on environment variables
"""

import json
import os
import sys
from pathlib import Path

def load_env_file(env_file=".env"):
    """Load environment variables from .env file"""
    if not os.path.exists(env_file):
        return
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove any trailing comments
                    value = value.split('#')[0].strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key.strip()] = value
    except Exception as e:
        print(f"⚠️  Warning: Could not load .env file: {e}")

def check_server_availability(config_file="configs/mcp_servers.json"):
    """Check which servers are available based on environment variables"""
    
    # Load environment variables from .env file
    load_env_file()
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file {config_file} not found")
        return
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error reading configuration file: {e}")
        return
    
    servers_config = config.get('servers', {})
    
    if not servers_config:
        print("❌ No servers found in configuration")
        return
    
    # Check each server
    available_count = 0
    total_count = len(servers_config)
    
    print(f"📋 Server Availability Check")
    print(f"   Total servers: {total_count}")
    print()
    
    for server_name, server_config in servers_config.items():
        env_vars = server_config.get('env_vars', {})
        missing_vars = []
        available_vars = []
        
        # Check environment variables
        for key, value in env_vars.items():
            if value.startswith('${') and value.endswith('}'):
                env_var_name = value[2:-1]  # Remove ${ and }
                # Try environment variable first
                env_value = os.getenv(env_var_name)
                if env_value:
                    available_vars.append(env_var_name)
                # Try shell variables for common ones
                elif env_var_name == "PWD":
                    available_vars.append(env_var_name)
                else:
                    missing_vars.append(env_var_name)
            else:
                available_vars.append(key)
        
        is_available = len(missing_vars) == 0
        if is_available:
            available_count += 1
        
        status = "✅" if is_available else "❌"
        print(f"{status} {server_name}")
        print(f"   Description: {server_config.get('description', 'No description')}")
        print(f"   Transport: {server_config.get('transport', 'stdio')}")
        print(f"   Image: {server_config.get('docker_image', 'N/A')}")
        
        if is_available:
            if available_vars:
                print(f"   Environment: {', '.join(available_vars)}")
        else:
            if missing_vars:
                print(f"   Missing: {', '.join(missing_vars)}")
        
        print()
    
    print(f"📊 Summary:")
    print(f"   Available: {available_count}")
    print(f"   Unavailable: {total_count - available_count}")
    
    if available_count == 0:
        print(f"\n💡 To set up environment variables, run:")
        print(f"   python scripts/setup_env.py")
    else:
        print(f"\n💡 To start the hub with available servers:")
        print(f"   python -m mcp_hub.mcp_hub_server --load-config")

def main():
    parser = argparse.ArgumentParser(description="Check MCP server availability")
    parser.add_argument(
        "--config-file",
        default="configs/mcp_servers.json",
        help="Path to server configuration file"
    )
    
    args = parser.parse_args()
    check_server_availability(args.config_file)

if __name__ == "__main__":
    import argparse
    main() 