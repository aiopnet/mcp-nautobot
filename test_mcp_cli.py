#!/usr/bin/env python3
"""
Test MCP server tool calls using mcp.cli.
"""
import subprocess
import json
import os
import tempfile

def test_mcp_server():
    """Test the MCP server using the mcp CLI tool."""
    
    # Set environment variables
    env = os.environ.copy()
    env["NAUTOBOT_URL"] = "https://nautobot.zt.vpsvc.com/"
    env["NAUTOBOT_TOKEN"] = "9dd16067076e3d8b5668d3e73a831b0a99220248"
    
    print("🧪 Testing MCP Nautobot Server using mcp CLI")
    print("=" * 50)
    
    # Create a temporary MCP config for testing
    config = {
        "servers": {
            "nautobot": {
                "command": "uv",
                "args": ["run", "python", "-m", "mcp_nautobot_server"],
                "env": {
                    "NAUTOBOT_URL": "https://nautobot.zt.vpsvc.com/",
                    "NAUTOBOT_TOKEN": "9dd16067076e3d8b5668d3e73a831b0a99220248"
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        config_path = f.name
    
    try:
        # Test 1: List tools
        print("\n📋 Test 1: Listing available tools...")
        result = subprocess.run([
            "mcp", "list", "tools", "nautobot", "--config", config_path
        ], capture_output=True, text=True, cwd="/Users/admin/Documents/projects/mcp-nautobot")
        
        if result.returncode == 0:
            print("✅ Tools listed successfully:")
            print(result.stdout)
        else:
            print(f"❌ Failed to list tools: {result.stderr}")
        
        # Test 2: Test connection
        print("\n🔌 Test 2: Testing Nautobot connection...")
        result = subprocess.run([
            "mcp", "call", "nautobot", "test_connection", "--config", config_path
        ], capture_output=True, text=True, cwd="/Users/admin/Documents/projects/mcp-nautobot")
        
        if result.returncode == 0:
            print("✅ Connection test successful:")
            print(result.stdout)
        else:
            print(f"❌ Connection test failed: {result.stderr}")
        
        # Test 3: Get IP addresses
        print("\n📊 Test 3: Getting IP addresses...")
        result = subprocess.run([
            "mcp", "call", "nautobot", "get_ip_addresses", 
            "--config", config_path,
            '{"limit": 3}'
        ], capture_output=True, text=True, cwd="/Users/admin/Documents/projects/mcp-nautobot")
        
        if result.returncode == 0:
            print("✅ IP addresses retrieved successfully:")
            print(result.stdout)
        else:
            print(f"❌ Failed to get IP addresses: {result.stderr}")
            
    except FileNotFoundError:
        print("❌ MCP CLI not found. Please install with: pip install mcp")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        # Clean up
        os.unlink(config_path)
    
    return True

if __name__ == "__main__":
    success = test_mcp_server()
    if success:
        print("\n🎉 MCP server testing completed!")
    else:
        print("\n💥 MCP server testing failed!")
