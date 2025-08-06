#!/usr/bin/env python3
"""
MCP CLI - Interactive command-line interface for MCP Hub Server
"""
import asyncio
import argparse
import json
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

from .mcp_manager import MCPManager, MCPServer

class MCPCLIInterface:
    """Command-line interface for MCP server management"""
    
    def __init__(self):
        self.console = Console()
        self.manager = MCPManager()
        
        # Set up logging to show in console
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def add_slack_server(self, use_docker: bool = True):
        """Add and configure Slack MCP server"""
        try:
            self.console.print("[bold blue]Adding Slack MCP Server...[/bold blue]")
            
            # Check if .env file exists and has required variables
            import os
            if not os.path.exists('.env'):
                self.console.print("[bold red]No .env file found![/bold red]")
                self.console.print("Please create a .env file with the following variables:")
                self.console.print("SLACK_BOT_TOKEN=xoxb-your-bot-token")
                self.console.print("SLACK_TEAM_ID=T01234567")
                self.console.print("SLACK_CHANNEL_IDS=C01234567,C76543210 (optional)")
                return
            
            self.manager.add_slack_server(use_docker=use_docker)
            self.console.print(f"[green]✅ Slack server added (using {'Docker' if use_docker else 'NPX'})[/green]")
            
        except ValueError as e:
            self.console.print(f"[bold red]❌ Configuration Error: {e}[/bold red]")
            self.console.print("\nPlease ensure your .env file contains:")
            self.console.print("SLACK_BOT_TOKEN=xoxb-your-bot-token")
            self.console.print("SLACK_TEAM_ID=T01234567")
            
        except Exception as e:
            self.console.print(f"[bold red]❌ Error adding Slack server: {e}[/bold red]")
    
    async def add_brave_search_server(self, use_docker: bool = True):
        """Add and configure Brave Search MCP server"""
        try:
            self.console.print("[bold blue]Adding Brave Search MCP Server...[/bold blue]")
            
            # Check if .env file exists and has required variables
            import os
            if not os.path.exists('.env'):
                self.console.print("[bold red]No .env file found![/bold red]")
                self.console.print("Please create a .env file with the following variables:")
                self.console.print("BRAVE_API_KEY=your-brave-api-key-here")
                return
            
            self.manager.add_brave_search_server(use_docker=use_docker)
            self.console.print(f"[green]✅ Brave Search server added (using {'Docker' if use_docker else 'NPX'})[/green]")
            
        except ValueError as e:
            self.console.print(f"[bold red]❌ Configuration Error: {e}[/bold red]")
            self.console.print("\nPlease ensure your .env file contains:")
            self.console.print("BRAVE_API_KEY=your-brave-api-key-here")
            
        except Exception as e:
            self.console.print(f"[bold red]❌ Error adding Brave Search server: {e}[/bold red]")
    
    async def add_wolfram_alpha_server(self, use_docker: bool = True):
        """Add and configure Wolfram Alpha MCP server"""
        try:
            self.console.print("[bold blue]Adding Wolfram Alpha MCP Server...[/bold blue]")
            
            # Check if .env file exists and has required variables
            import os
            if not os.path.exists('.env'):
                self.console.print("[bold red]No .env file found![/bold red]")
                self.console.print("Please create a .env file with the following variables:")
                self.console.print("WOLFRAM_API_KEY=your-wolfram-api-key-here")
                return
            
            self.manager.add_wolfram_alpha_server(use_docker=use_docker)
            self.console.print(f"[green]✅ Wolfram Alpha server added (using {'Docker' if use_docker else 'NPX'})[/green]")
            
        except ValueError as e:
            self.console.print(f"[bold red]❌ Configuration Error: {e}[/bold red]")
            self.console.print("\nPlease ensure your .env file contains:")
            self.console.print("WOLFRAM_API_KEY=your-wolfram-api-key-here")
            
        except Exception as e:
            self.console.print(f"[bold red]❌ Error adding Wolfram Alpha server: {e}[/bold red]")
    
    async def start_all_servers(self):
        """Start all configured servers"""
        if not self.manager.servers:
            self.console.print("[yellow]No servers configured[/yellow]")
            return
        
        self.console.print("[bold blue]Starting all configured servers...[/bold blue]")
        results = await self.manager.start_all_servers()
        
        # Display results
        table = Table(title="Server Startup Results")
        table.add_column("Server", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Tools Count", style="green")
        
        for server_name, success in results.items():
            status = "🟢 Started" if success else "🔴 Failed"
            tools_count = len(self.manager.get_server_tools(server_name))
            table.add_row(server_name, status, str(tools_count))
        
        self.console.print(table)
        
        # Show all tools
        if any(results.values()):
            await self.list_tools()
    
    async def start_server(self, server_name: str):
        """Start an MCP server"""
        self.console.print(f"[bold blue]Starting MCP server: {server_name}...[/bold blue]")
        
        success = await self.manager.start_server(server_name)
        
        if success:
            self.console.print(f"[green]✅ Server '{server_name}' started successfully[/green]")
            await self.list_tools(server_name)
        else:
            self.console.print(f"[bold red]❌ Failed to start server '{server_name}'[/bold red]")
    
    async def list_servers(self):
        """List all configured servers"""
        servers = self.manager.servers
        active_connections = self.manager.active_connections
        
        if not servers:
            self.console.print("[yellow]No MCP servers configured[/yellow]")
            return
        
        table = Table(title="MCP Servers")
        table.add_column("Name", style="cyan")
        table.add_column("Command", style="blue")
        table.add_column("Transport", style="green")
        table.add_column("Status", style="bold")
        
        for name, server in servers.items():
            status = "🟢 Active" if name in active_connections else "🔴 Inactive"
            command_short = f"{server.command} {' '.join(server.args[:2])}..."
            
            table.add_row(
                name,
                command_short,
                server.transport,
                status
            )
        
        self.console.print(table)
    
    async def list_tools(self, server_name: str = None):
        """List tools from MCP servers"""
        if server_name:
            tools = self.manager.get_server_tools(server_name)
            if not tools:
                self.console.print(f"[yellow]No tools available for server '{server_name}' or server not started[/yellow]")
                return
            
            self._display_tools_table(f"Tools for {server_name}", {server_name: tools})
        else:
            all_tools = self.manager.get_all_tools()
            if not all_tools:
                self.console.print("[yellow]No tools available from any server[/yellow]")
                return
            
            self._display_tools_table("All Available Tools", all_tools)
    
    def _display_tools_table(self, title: str, tools_dict: dict):
        """Display tools in a formatted table"""
        table = Table(title=title)
        table.add_column("Server", style="cyan")
        table.add_column("Tool Name", style="bold blue")
        table.add_column("Description", style="green")
        table.add_column("Input Schema", style="yellow")
        
        for server_name, tools in tools_dict.items():
            for tool in tools:
                # Extract input schema info
                input_schema = tool.get("inputSchema", {})
                properties = input_schema.get("properties", {})
                required = input_schema.get("required", [])
                
                schema_info = []
                for prop, details in properties.items():
                    prop_type = details.get("type", "unknown")
                    is_required = " (required)" if prop in required else ""
                    schema_info.append(f"{prop}: {prop_type}{is_required}")
                
                table.add_row(
                    server_name,
                    tool.get("name", "Unknown"),
                    tool.get("description", "No description"),
                    "\n".join(schema_info) if schema_info else "No parameters"
                )
        
        self.console.print(table)
    
    async def call_tool(self, server_name: str, tool_name: str):
        """Interactively call a tool"""
        # Get tool information
        tools = self.manager.get_server_tools(server_name)
        tool_info = None
        
        for tool in tools:
            if tool.get("name") == tool_name:
                tool_info = tool
                break
        
        if not tool_info:
            self.console.print(f"[bold red]Tool '{tool_name}' not found on server '{server_name}'[/bold red]")
            return
        
        # Display tool information
        self.console.print(Panel(
            f"[bold]{tool_info.get('name', 'Unknown')}[/bold]\n"
            f"{tool_info.get('description', 'No description')}",
            title="Tool Information"
        ))
        
        # Get input parameters
        input_schema = tool_info.get("inputSchema", {})
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])
        
        arguments = {}
        
        if properties:
            self.console.print("\n[bold blue]Please provide the following parameters:[/bold blue]")
            
            for prop, details in properties.items():
                prop_type = details.get("type", "string")
                description = details.get("description", "")
                is_required = prop in required
                
                prompt_text = f"{prop} ({prop_type})"
                if description:
                    prompt_text += f" - {description}"
                if is_required:
                    prompt_text += " [required]"
                
                value = Prompt.ask(prompt_text, default="" if not is_required else None)
                
                if value or is_required:
                    # Convert type if needed
                    if prop_type == "integer":
                        try:
                            arguments[prop] = int(value)
                        except ValueError:
                            self.console.print(f"[bold red]Invalid integer value for {prop}[/bold red]")
                            return
                    elif prop_type == "number":
                        try:
                            arguments[prop] = float(value)
                        except ValueError:
                            self.console.print(f"[bold red]Invalid number value for {prop}[/bold red]")
                            return
                    elif prop_type == "boolean":
                        arguments[prop] = value.lower() in ("true", "yes", "1", "on")
                    else:
                        arguments[prop] = value
        
        # Call the tool
        self.console.print(f"\n[bold blue]Calling tool '{tool_name}' with arguments: {arguments}[/bold blue]")
        
        try:
            result = await self.manager.call_tool(server_name, tool_name, arguments)
            
            if result:
                if result.get("error"):
                    self.console.print(f"[bold red]Tool Error: {result['error']}[/bold red]")
                else:
                    self.console.print(Panel(
                        json.dumps(result.get("result", {}), indent=2),
                        title="Tool Result",
                        border_style="green"
                    ))
            else:
                self.console.print("[bold red]Failed to call tool[/bold red]")
                
        except Exception as e:
            self.console.print(f"[bold red]Error calling tool: {e}[/bold red]")
    
    async def stop_server(self, server_name: str):
        """Stop an MCP server"""
        self.console.print(f"[bold blue]Stopping server '{server_name}'...[/bold blue]")
        await self.manager.stop_server(server_name)
        self.console.print(f"[green]✅ Server '{server_name}' stopped[/green]")
    
    async def interactive_mode(self):
        """Interactive mode for managing MCP servers"""
        self.console.print(Panel(
            "[bold blue]MCP Server Manager - Interactive Mode[/bold blue]\n"
            "Available commands:\n"
            "1. add-slack [npx] - Add Slack MCP server\n"
            "2. add-brave [npx] - Add Brave Search MCP server\n"
            "3. add-wolfram [npx] - Add Wolfram Alpha MCP server\n"
            "4. add-all [npx] - Add all available servers\n"
            "5. list-servers - List all servers\n"
            "6. start <server> - Start a specific server\n"
            "7. start-all - Start all configured servers\n"
            "8. stop <server> - Stop a server\n"
            "9. list-tools [server] - List tools\n"
            "10. call-tool <server> <tool> - Call a tool\n"
            "11. quit - Exit",
            title="Welcome"
        ))
        
        while True:
            command = Prompt.ask("\n[bold cyan]MCP>[/bold cyan]").strip().split()
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            try:
                if cmd == "quit" or cmd == "exit":
                    break
                elif cmd == "add-slack":
                    use_docker = len(command) < 2 or command[1].lower() != "npx"
                    await self.add_slack_server(use_docker)
                elif cmd == "add-brave":
                    use_docker = len(command) < 2 or command[1].lower() != "npx"
                    await self.add_brave_search_server(use_docker)
                elif cmd == "add-wolfram":
                    use_docker = len(command) < 2 or command[1].lower() != "npx"
                    await self.add_wolfram_alpha_server(use_docker)
                elif cmd == "add-all":
                    use_docker = len(command) < 2 or command[1].lower() != "npx"
                    await self.add_slack_server(use_docker)
                    await self.add_brave_search_server(use_docker)
                    await self.add_wolfram_alpha_server(use_docker)
                elif cmd == "list-servers":
                    await self.list_servers()
                elif cmd == "start" and len(command) > 1:
                    await self.start_server(command[1])
                elif cmd == "start-all":
                    await self.start_all_servers()
                elif cmd == "stop" and len(command) > 1:
                    await self.stop_server(command[1])
                elif cmd == "list-tools":
                    server_name = command[1] if len(command) > 1 else None
                    await self.list_tools(server_name)
                elif cmd == "call-tool" and len(command) > 2:
                    await self.call_tool(command[1], command[2])
                else:
                    self.console.print("[yellow]Unknown command or missing arguments[/yellow]")
                    
            except Exception as e:
                self.console.print(f"[bold red]Error: {e}[/bold red]")
        
        # Cleanup
        await self.manager.stop_all_servers()
        self.console.print("[green]Goodbye![/green]")

async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="MCP Server Manager")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start in interactive mode")
    parser.add_argument("--add-slack", action="store_true", help="Add Slack MCP server")
    parser.add_argument("--add-brave", action="store_true", help="Add Brave Search MCP server")
    parser.add_argument("--add-wolfram", action="store_true", help="Add Wolfram Alpha MCP server")
    parser.add_argument("--add-all", action="store_true", help="Add all available MCP servers")
    parser.add_argument("--use-npx", action="store_true", help="Use NPX instead of Docker")
    parser.add_argument("--start", metavar="SERVER", help="Start a specific server")
    parser.add_argument("--start-all", action="store_true", help="Start all configured servers")
    parser.add_argument("--list-servers", action="store_true", help="List all servers")
    parser.add_argument("--list-tools", metavar="SERVER", nargs="?", const="", help="List tools (optionally for a specific server)")
    parser.add_argument("--call-tool", nargs=2, metavar=("SERVER", "TOOL"), help="Call a specific tool")
    
    args = parser.parse_args()
    
    cli = MCPCLIInterface()
    
    try:
        if args.interactive:
            await cli.interactive_mode()
        elif args.add_slack:
            await cli.add_slack_server(use_docker=not args.use_npx)
        elif args.add_brave:
            await cli.add_brave_search_server(use_docker=not args.use_npx)
        elif args.add_wolfram:
            await cli.add_wolfram_alpha_server(use_docker=not args.use_npx)
        elif args.add_all:
            await cli.add_slack_server(use_docker=not args.use_npx)
            await cli.add_brave_search_server(use_docker=not args.use_npx)
            await cli.add_wolfram_alpha_server(use_docker=not args.use_npx)
        elif args.start:
            await cli.start_server(args.start)
        elif args.start_all:
            await cli.start_all_servers()
        elif args.list_servers:
            await cli.list_servers()
        elif args.list_tools is not None:
            await cli.list_tools(args.list_tools if args.list_tools else None)
        elif args.call_tool:
            await cli.call_tool(args.call_tool[0], args.call_tool[1])
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        cli.console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        cli.console.print(f"[bold red]Error: {e}[/bold red]")
    finally:
        await cli.manager.stop_all_servers()

if __name__ == "__main__":
    asyncio.run(main()) 