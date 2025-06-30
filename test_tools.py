#!/usr/bin/env python3
"""
Test individual tool functions directly.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_nautobot_server.nautobot_client import NautobotClient, NautobotConfig
from pydantic import HttpUrl

async def test_individual_tools():
    """Test individual tool functions."""
    
    print("🧪 Testing Individual MCP Tool Functions")
    print("=" * 50)
    
    # Setup client
    base_url = os.getenv("NAUTOBOT_URL", "https://nautobot.zt.vpsvc.com/")
    token = os.getenv("NAUTOBOT_TOKEN", "9dd16067076e3d8b5668d3e73a831b0a99220248")
    
    config = NautobotConfig(
        nautobot_url=HttpUrl(base_url),
        nautobot_token=token
    )
    client = NautobotClient(config)
    
    try:
        # Test 1: Connection test
        print("\n🔌 Test 1: Connection Test")
        result = await client.test_connection()
        print(f"✅ Connection: {result}")
        
        # Test 2: Get IP addresses
        print("\n📊 Test 2: Get IP Addresses (limit=3)")
        ip_addresses = await client.get_ip_addresses(limit=3)
        print(f"Found {len(ip_addresses)} IP addresses:")
        for i, ip in enumerate(ip_addresses, 1):
            print(f"  {i}. {ip.address}")
            
        # Test 3: Get prefixes
        print("\n🌐 Test 3: Get Prefixes (limit=3)")
        prefixes = await client.get_prefixes(limit=3)
        print(f"Found {len(prefixes)} prefixes:")
        for i, prefix in enumerate(prefixes, 1):
            print(f"  {i}. {prefix.prefix}")
            
        # Test 4: Search IP addresses
        print("\n🔍 Test 4: Search IP Addresses (query='10.')")
        search_results = await client.search_ip_addresses(query="10.")
        print(f"Found {len(search_results)} matching IP addresses:")
        for i, ip in enumerate(search_results[:3], 1):
            print(f"  {i}. {ip.address}")
            
        # Test 5: Get specific IP address (if we have one)
        if ip_addresses:
            print("\n🎯 Test 5: Get Specific IP Address")
            ip_id = ip_addresses[0].id
            specific_ip = await client.get_ip_address_by_id(ip_id)
            if specific_ip:
                print(f"✅ Retrieved IP: {specific_ip.address}")
            else:
                print("❌ Failed to retrieve specific IP")
        
        print("\n🎉 All tool tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close()
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_individual_tools())
