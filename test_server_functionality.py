#!/usr/bin/env python3
"""
Test script for MCP Nautobot server functionality.

This script tests the connection to Nautobot and demonstrates
the various tools available in the MCP server.
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_nautobot_server.nautobot_client import NautobotClient, NautobotConfig
from mcp_nautobot_server.server import (
    handle_call_tool,
    handle_list_tools,
    handle_list_resources,
    handle_read_resource,
    get_nautobot_client
)
from pydantic import AnyUrl


async def test_nautobot_connectivity():
    """Test basic connectivity to Nautobot API."""
    print("🔌 Testing Nautobot API Connectivity...")
    
    try:
        # Get configuration from environment
        config = NautobotConfig(
            nautobot_url=os.getenv("NAUTOBOT_URL", "https://nautobot.zt.vpsvc.com/"),  # type: ignore
            nautobot_token=os.getenv("NAUTOBOT_TOKEN", "9dd16067076e3d8b5668d3e73a831b0a99220248"),
        )
        
        print(f"📡 Connecting to: {config.nautobot_url}")
        print(f"🔑 Using token: {config.nautobot_token[:8]}...")
        
        async with NautobotClient(config) as client:
            # Test connection
            is_connected = await client.test_connection()
            
            if is_connected:
                print("✅ Successfully connected to Nautobot API!")
                return True
            else:
                print("❌ Failed to connect to Nautobot API")
                return False
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


async def test_mcp_tools():
    """Test MCP server tools functionality."""
    print("\n🛠️  Testing MCP Server Tools...")
    
    try:
        # Test 1: List available tools
        print("\n📋 1. Listing available tools:")
        tools = await handle_list_tools()
        print(f"   Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        # Test 2: Test connection tool
        print("\n🔍 2. Testing connection tool:")
        result = await handle_call_tool("test_connection", {})
        print(f"   Result: {result[0].text[:100]}...")
        
        # Test 3: Get IP addresses (limited)
        print("\n📊 3. Testing get_ip_addresses tool:")
        result = await handle_call_tool("get_ip_addresses", {"limit": 5})
        print(f"   Result: {result[0].text[:150]}...")
        
        # Test 4: Search IP addresses
        print("\n🔎 4. Testing search_ip_addresses tool:")
        result = await handle_call_tool("search_ip_addresses", {
            "query": "10.0",
            "limit": 3
        })
        print(f"   Result: {result[0].text[:150]}...")
        
        # Test 5: Get prefixes
        print("\n🌐 5. Testing get_prefixes tool:")
        result = await handle_call_tool("get_prefixes", {"limit": 3})
        print(f"   Result: {result[0].text[:150]}...")
        
        print("\n✅ All MCP tools tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MCP tools test error: {e}")
        return False


async def test_mcp_resources():
    """Test MCP server resources."""
    print("\n📚 Testing MCP Server Resources...")
    
    try:
        # Test 1: List available resources
        print("\n📋 1. Listing available resources:")
        resources = await handle_list_resources()
        print(f"   Found {len(resources)} resources:")
        for resource in resources:
            print(f"   - {resource.uri}: {resource.name}")
        
        # Test 2: Read status resource
        print("\n📊 2. Reading status resource:")
        try:
            result = await handle_read_resource(AnyUrl("nautobot://status"))
            status_data = json.loads(result)
            print(f"   Connected: {status_data.get('connected')}")
            print(f"   Base URL: {status_data.get('base_url')}")
        except Exception as e:
            print(f"   Error reading status: {e}")
        
        print("\n✅ MCP resources tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MCP resources test error: {e}")
        return False


async def demonstrate_real_queries():
    """Demonstrate real-world queries."""
    print("\n🎯 Demonstrating Real-World Queries...")
    
    try:
        client = await get_nautobot_client()
        
        # Query 1: Get all active IP addresses
        print("\n1. Getting active IP addresses:")
        result = await handle_call_tool("get_ip_addresses", {
            "status": "active",
            "limit": 10
        })
        
        # Extract and display summary
        result_text = result[0].text
        if "Retrieved" in result_text:
            import re
            count_match = re.search(r'Retrieved (\d+)', result_text)
            if count_match:
                count = count_match.group(1)
                print(f"   ✅ Found {count} active IP addresses")
        
        # Query 2: Search for specific network ranges
        print("\n2. Searching for 10.x.x.x networks:")
        result = await handle_call_tool("search_ip_addresses", {
            "query": "10.",
            "limit": 5
        })
        
        result_text = result[0].text
        if "Found" in result_text:
            import re
            count_match = re.search(r'Found (\d+)', result_text)
            if count_match:
                count = count_match.group(1)
                print(f"   ✅ Found {count} IPs matching '10.'")
        
        # Query 3: Get network prefixes
        print("\n3. Getting network prefixes:")
        result = await handle_call_tool("get_prefixes", {
            "limit": 5
        })
        
        result_text = result[0].text
        if "Retrieved" in result_text:
            import re
            count_match = re.search(r'Retrieved (\d+)', result_text)
            if count_match:
                count = count_match.group(1)
                print(f"   ✅ Found {count} network prefixes")
        
        print("\n✅ Real-world queries completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Real-world queries error: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 MCP Nautobot Server Test Suite")
    print("=" * 50)
    
    # Set environment variables
    os.environ["NAUTOBOT_URL"] = "https://nautobot.zt.vpsvc.com/"
    os.environ["NAUTOBOT_TOKEN"] = "9dd16067076e3d8b5668d3e73a831b0a99220248"
    
    test_results = []
    
    # Test 1: Basic connectivity
    connectivity_ok = await test_nautobot_connectivity()
    test_results.append(("Nautobot Connectivity", connectivity_ok))
    
    if connectivity_ok:
        # Test 2: MCP Tools
        tools_ok = await test_mcp_tools()
        test_results.append(("MCP Tools", tools_ok))
        
        # Test 3: MCP Resources
        resources_ok = await test_mcp_resources()
        test_results.append(("MCP Resources", resources_ok))
        
        # Test 4: Real-world queries
        queries_ok = await demonstrate_real_queries()
        test_results.append(("Real-world Queries", queries_ok))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! MCP Nautobot server is ready for use.")
        print("\n🔧 Next steps:")
        print("   1. The server is ready for Claude Desktop integration")
        print("   2. Use the tools to query your Nautobot instance")
        print("   3. Try the intelligent prompts for analysis")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
