#!/usr/bin/env python3
"""
Simple test script for the MCP Hub Server
"""
import asyncio
import aiohttp
import json
import sys
import os

# Add the mcps directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_hub_server():
    """Test the MCP Hub Server functionality"""
    print("🧪 Testing MCP Hub Server...")
    
    # Test server URL
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Test server status
            print("\n1. Testing server status...")
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    status = await response.json()
                    print(f"✅ Server is running: {status}")
                else:
                    print(f"❌ Server status failed: {response.status}")
                    return
            
            # 2. Test servers endpoint
            print("\n2. Testing servers endpoint...")
            async with session.get(f"{base_url}/servers") as response:
                if response.status == 200:
                    servers = await response.json()
                    print(f"✅ Found {len(servers)} servers: {[s['name'] for s in servers]}")
                else:
                    print(f"❌ Servers endpoint failed: {response.status}")
            
            # 3. Test tools endpoint
            print("\n3. Testing tools endpoint...")
            async with session.get(f"{base_url}/tools") as response:
                if response.status == 200:
                    tools = await response.json()
                    print(f"✅ Found {len(tools)} tools")
                    for tool in tools[:3]:  # Show first 3 tools
                        print(f"   - {tool['name']} ({tool['server_name']})")
                else:
                    print(f"❌ Tools endpoint failed: {response.status}")
            
            # 4. Test start all servers
            print("\n4. Testing start all servers...")
            async with session.post(f"{base_url}/servers/start-all") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Start all servers: {result}")
                else:
                    print(f"❌ Start all servers failed: {response.status}")
            
            # Wait a moment for servers to start
            await asyncio.sleep(3)
            
            # 5. Test tools again after starting servers
            print("\n5. Testing tools after starting servers...")
            async with session.get(f"{base_url}/tools") as response:
                if response.status == 200:
                    tools = await response.json()
                    print(f"✅ Found {len(tools)} tools after starting servers")
                    if tools:
                        # Test tool info endpoint
                        tool_name = tools[0]['name']
                        print(f"   Testing tool info for: {tool_name}")
                        async with session.get(f"{base_url}/tools/info/{tool_name}") as info_response:
                            if info_response.status == 200:
                                tool_info = await info_response.json()
                                print(f"✅ Tool info: {tool_info['description']}")
                            else:
                                print(f"❌ Tool info failed: {info_response.status}")
                else:
                    print(f"❌ Tools endpoint failed: {response.status}")
            
            # 6. Test tool call (if tools are available)
            print("\n6. Testing tool call...")
            async with session.get(f"{base_url}/tools") as response:
                if response.status == 200:
                    tools = await response.json()
                    if tools:
                        tool_name = tools[0]['name']
                        print(f"   Testing call to: {tool_name}")
                        
                        # Try calling with empty arguments
                        payload = {
                            "tool_name": tool_name,
                            "arguments": {},
                            "timeout": 10
                        }
                        
                        async with session.post(f"{base_url}/tools/call", json=payload) as call_response:
                            if call_response.status == 200:
                                result = await call_response.json()
                                if result['success']:
                                    print(f"✅ Tool call successful: {result['result']}")
                                else:
                                    print(f"⚠️  Tool call failed: {result['error']}")
                            else:
                                print(f"❌ Tool call failed: {call_response.status}")
                    else:
                        print("⚠️  No tools available to test")
                else:
                    print(f"❌ Could not get tools for testing: {response.status}")
            
            # 7. Final status check
            print("\n7. Final status check...")
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    final_status = await response.json()
                    print(f"✅ Final status: {final_status['servers_count']} servers, {final_status['tools_count']} tools")
                else:
                    print(f"❌ Final status failed: {response.status}")
            
            print("\n🎉 All tests completed!")
            
        except aiohttp.ClientError as e:
            print(f"❌ Connection error: {e}")
            print("Make sure the MCP Hub Server is running on http://localhost:8000")
        except Exception as e:
            print(f"❌ Test error: {e}")

async def test_hub_server_offline():
    """Test the hub server without requiring it to be running"""
    print("🧪 Testing MCP Hub Server (offline mode)...")
    
    try:
        from mcp_hub_server import MCPHubServer
        
        # Create hub server instance
        hub = MCPHubServer(host="127.0.0.1", port=8000)
        
        # Test adding servers
        print("\n1. Testing server configuration...")
        try:
            hub.mcp_manager.add_slack_server()
            print("✅ Slack server configuration added")
        except Exception as e:
            print(f"⚠️  Slack server configuration failed: {e}")
        
        try:
            hub.mcp_manager.add_brave_search_server()
            print("✅ Brave Search server configuration added")
        except Exception as e:
            print(f"⚠️  Brave Search server configuration failed: {e}")
        
        try:
            hub.mcp_manager.add_wolfram_alpha_server()
            print("✅ Wolfram Alpha server configuration added")
        except Exception as e:
            print(f"⚠️  Wolfram Alpha server configuration failed: {e}")
        
        # Test server listing
        print("\n2. Testing server listing...")
        servers = hub.mcp_manager.servers
        print(f"✅ Configured servers: {list(servers.keys())}")
        
        # Test tool hub
        print("\n3. Testing tool hub...")
        tools = hub.tool_hub.get_all_tools()
        print(f"✅ Tool hub initialized, {len(tools)} server groups")
        
        print("\n🎉 Offline tests completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
    except Exception as e:
        print(f"❌ Test error: {e}")

async def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MCP Hub Server")
    parser.add_argument("--offline", action="store_true", help="Run offline tests only")
    parser.add_argument("--url", default="http://localhost:8000", help="Hub server URL")
    
    args = parser.parse_args()
    
    if args.offline:
        await test_hub_server_offline()
    else:
        await test_hub_server()

if __name__ == "__main__":
    asyncio.run(main()) 