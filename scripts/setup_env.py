#!/usr/bin/env python3
"""
Interactive environment setup script for MCP Hub.
This script helps users configure their .env file with the necessary API keys.
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("🚀 MCP Hub Environment Setup")
    print("=" * 60)
    print("This script will help you configure your .env file with the")
    print("necessary API keys for your MCP servers.")
    print()

def get_env_file_path():
    """Get the path to the .env file."""
    project_root = Path(__file__).parent.parent
    return project_root / ".env"

def load_existing_env():
    """Load existing environment variables from .env file."""
    env_file = get_env_file_path()
    existing_vars = {}
    
    if env_file.exists():
        print(f"📁 Found existing .env file: {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_vars[key] = value
        print(f"✅ Loaded {len(existing_vars)} existing variables")
    else:
        print("📁 No existing .env file found. Creating new one.")
    
    return existing_vars

def get_user_input(prompt, default="", is_secret=False):
    """Get user input with optional default value."""
    if default:
        if is_secret:
            display_value = "*" * len(default) if default else ""
            prompt = f"{prompt} (current: {display_value}): "
        else:
            prompt = f"{prompt} (current: {default}): "
    else:
        prompt = f"{prompt}: "
    
    value = input(prompt).strip()
    return value if value else default

def setup_slack_config(existing_vars):
    """Setup Slack configuration."""
    print("\n🔵 Slack Configuration")
    print("-" * 30)
    print("Slack integration allows you to send messages and interact with Slack channels.")
    print("Get your tokens from: https://api.slack.com/apps")
    print()
    
    slack_bot_token = get_user_input(
        "Slack Bot Token (xoxb-...)", 
        existing_vars.get('SLACK_BOT_TOKEN', ''),
        is_secret=True
    )
    
    slack_team_id = get_user_input(
        "Slack Team ID (T...)", 
        existing_vars.get('SLACK_TEAM_ID', '')
    )
    
    slack_channel_ids = get_user_input(
        "Slack Channel IDs (comma-separated, optional)", 
        existing_vars.get('SLACK_CHANNEL_IDS', '')
    )
    
    return {
        'SLACK_BOT_TOKEN': slack_bot_token,
        'SLACK_TEAM_ID': slack_team_id,
        'SLACK_CHANNEL_IDS': slack_channel_ids
    }

def setup_brave_config(existing_vars):
    """Setup Brave Search configuration."""
    print("\n🔵 Brave Search Configuration")
    print("-" * 30)
    print("Brave Search provides web search capabilities.")
    print("Get your API key from: https://api.search.brave.com/")
    print()
    
    brave_api_key = get_user_input(
        "Brave API Key", 
        existing_vars.get('BRAVE_API_KEY', ''),
        is_secret=True
    )
    
    return {'BRAVE_API_KEY': brave_api_key}

def setup_wolfram_config(existing_vars):
    """Setup Wolfram Alpha configuration."""
    print("\n🔵 Wolfram Alpha Configuration")
    print("-" * 30)
    print("Wolfram Alpha provides computational knowledge and answers.")
    print("Get your API key from: https://developer.wolframalpha.com/")
    print()
    
    wolfram_api_key = get_user_input(
        "Wolfram Alpha API Key", 
        existing_vars.get('WOLFRAM_API_KEY', ''),
        is_secret=True
    )
    
    return {'WOLFRAM_API_KEY': wolfram_api_key}

def setup_openweather_config(existing_vars):
    """Setup OpenWeather configuration."""
    print("\n🔵 OpenWeather Configuration")
    print("-" * 30)
    print("OpenWeather provides weather information and forecasts.")
    print("Get your API key from: https://openweathermap.org/api")
    print()
    
    openweather_api_key = get_user_input(
        "OpenWeather API Key", 
        existing_vars.get('OPENWEATHER_API_KEY', ''),
        is_secret=True
    )
    
    return {'OPENWEATHER_API_KEY': openweather_api_key}

def setup_github_config(existing_vars):
    """Setup GitHub configuration."""
    print("\n🔵 GitHub Configuration")
    print("-" * 30)
    print("GitHub integration allows repository management and operations.")
    print("Get your token from: https://github.com/settings/tokens")
    print()
    
    github_token = get_user_input(
        "GitHub Personal Access Token", 
        existing_vars.get('GITHUB_TOKEN', ''),
        is_secret=True
    )
    
    return {'GITHUB_TOKEN': github_token}

def setup_database_config(existing_vars):
    """Setup database configuration."""
    print("\n🔵 Database Configuration")
    print("-" * 30)
    print("Database integrations for PostgreSQL and Redis.")
    print()
    
    postgres_connection = get_user_input(
        "PostgreSQL Connection String (postgresql://...)", 
        existing_vars.get('POSTGRES_CONNECTION_STRING', '')
    )
    
    redis_url = get_user_input(
        "Redis URL (redis://...)", 
        existing_vars.get('REDIS_URL', '')
    )
    
    return {
        'POSTGRES_CONNECTION_STRING': postgres_connection,
        'REDIS_URL': redis_url
    }

def setup_news_config(existing_vars):
    """Setup News API configuration."""
    print("\n🔵 News API Configuration")
    print("-" * 30)
    print("News API provides current news and articles.")
    print("Get your API key from: https://newsapi.org/")
    print()
    
    news_api_key = get_user_input(
        "News API Key", 
        existing_vars.get('NEWS_API_KEY', ''),
        is_secret=True
    )
    
    return {'NEWS_API_KEY': news_api_key}

def setup_google_calendar_config(existing_vars):
    """Setup Google Calendar configuration."""
    print("\n🔵 Google Calendar Configuration")
    print("-" * 30)
    print("Google Calendar integration for calendar management.")
    print("This requires OAuth2 setup. See: https://developers.google.com/calendar")
    print()
    
    google_calendar_credentials = get_user_input(
        "Google Calendar Credentials (JSON content or file path)", 
        existing_vars.get('GOOGLE_CALENDAR_CREDENTIALS', '')
    )
    
    google_calendar_token = get_user_input(
        "Google Calendar Token (JSON content or file path)", 
        existing_vars.get('GOOGLE_CALENDAR_TOKEN', '')
    )
    
    return {
        'GOOGLE_CALENDAR_CREDENTIALS': google_calendar_credentials,
        'GOOGLE_CALENDAR_TOKEN': google_calendar_token
    }

def write_env_file(config):
    """Write configuration to .env file."""
    env_file = get_env_file_path()
    
    # Create backup if file exists
    if env_file.exists():
        backup_file = env_file.with_suffix('.env.backup')
        env_file.rename(backup_file)
        print(f"📋 Created backup: {backup_file}")
    
    # Write new .env file
    with open(env_file, 'w') as f:
        f.write("# MCP Hub Environment Configuration\n")
        f.write("# Generated by setup_env.py\n\n")
        
        for key, value in config.items():
            if value:  # Only write non-empty values
                f.write(f"{key}={value}\n")
            else:
                f.write(f"# {key}=\n")
    
    print(f"✅ Environment file written: {env_file}")

def main():
    """Main setup function."""
    print_banner()
    
    # Load existing configuration
    existing_vars = load_existing_env()
    
    # Setup each service
    config = {}
    
    # Core services
    config.update(setup_slack_config(existing_vars))
    config.update(setup_brave_config(existing_vars))
    config.update(setup_wolfram_config(existing_vars))
    config.update(setup_openweather_config(existing_vars))
    
    # Optional services
    print("\n🔵 Optional Services")
    print("-" * 30)
    print("The following services are optional. Press Enter to skip.")
    print()
    
    if input("Setup GitHub integration? (y/N): ").lower().startswith('y'):
        config.update(setup_github_config(existing_vars))
    
    if input("Setup database connections? (y/N): ").lower().startswith('y'):
        config.update(setup_database_config(existing_vars))
    
    if input("Setup News API? (y/N): ").lower().startswith('y'):
        config.update(setup_news_config(existing_vars))
    
    if input("Setup Google Calendar? (y/N): ").lower().startswith('y'):
        config.update(setup_google_calendar_config(existing_vars))
    
    # Write configuration
    print("\n" + "=" * 60)
    print("📝 Writing Configuration")
    print("=" * 60)
    
    write_env_file(config)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    
    configured_services = [k for k, v in config.items() if v]
    print(f"📊 Configured {len(configured_services)} environment variables")
    
    if configured_services:
        print("\n🔧 Next Steps:")
        print("1. Start the MCP Hub: python -m mcp_hub.mcp_hub_server --load-config")
        print("2. Check server availability: python scripts/check_servers.py")
        print("3. Access the API: http://localhost:8000/docs")
    
    print("\n📚 For more information, see:")
    print("- README.md")
    print("- docs/DYNAMIC_MCP_SERVERS.md")
    print("- GOOGLE_CLOUD_SETUP.md")

if __name__ == "__main__":
    main() 