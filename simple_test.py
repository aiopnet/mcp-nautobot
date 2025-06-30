#!/usr/bin/env python3
"""
Simple connectivity test for Nautobot API.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_nautobot_server.nautobot_client import NautobotClient, NautobotConfig
from pydantic import HttpUrl

async def test_nautobot_connectivity():
    """Test basic connectivity to Nautobot API."""
    base_url = os.getenv("NAUTOBOT_URL", "https://nautobot.zt.vpsvc.com/")
    token = os.getenv("NAUTOBOT_TOKEN", "9dd16067076e3d8b5668d3e73a831b0a99220248")
    
    print(f"🔌 Testing connectivity to: {base_url}")
    print(f"🔑 Using token: {token[:12]}...")
    
    config = NautobotConfig(
        nautobot_url=HttpUrl(base_url),
        nautobot_token=token
    )
    client = NautobotClient(config)
    
    try:
        # Test connection
        print("\n📡 Testing API connection...")
        result = await client.test_connection()
        print(f"✅ Connection successful: {result}")
        
        # Test getting IP addresses
        print("\n📊 Fetching IP addresses...")
        ip_addresses = await client.get_ip_addresses(limit=5)
        print(f"Found {len(ip_addresses)} IP addresses:")
        
        for i, ip in enumerate(ip_addresses[:3], 1):
            print(f"  {i}. {ip.address} - Status: {ip.status}")
            if hasattr(ip, 'description') and ip.description:
                print(f"     Description: {ip.description}")
        
        # Test getting prefixes
        print("\n🌐 Fetching IP prefixes...")
        prefixes = await client.get_prefixes(limit=3)
        print(f"Found {len(prefixes)} prefixes:")
        
        for i, prefix in enumerate(prefixes[:3], 1):
            print(f"  {i}. {prefix.prefix} - Status: {prefix.status}")
            if hasattr(prefix, 'description') and prefix.description:
                print(f"     Description: {prefix.description}")
        
        print("\n🎉 All tests passed! Nautobot API is accessible and working.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await client.close()
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_nautobot_connectivity())
