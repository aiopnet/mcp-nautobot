"""
Test configuration and fixtures for the MCP Nautobot server.

This module provides common test fixtures and configuration
for testing the Nautobot MCP server integration.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from mcp_nautobot_server.nautobot_client import (
    NautobotClient, 
    NautobotConfig, 
    IPAddress, 
    Prefix
)


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def nautobot_config():
    """Provide test configuration for Nautobot client."""
    return NautobotConfig(
        nautobot_url="http://localhost:8000",  # type: ignore
        nautobot_token="test-token-123",
        nautobot_verify_ssl=False,
        nautobot_timeout=30,
        nautobot_rate_limit=100
    )


@pytest.fixture
def sample_ip_address_data():
    """Provide sample IP address data for testing."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "url": "http://localhost:8000/api/ipam/ip-addresses/123e4567-e89b-12d3-a456-426614174000/",
        "address": "192.168.1.100/24",
        "status": {
            "value": "active",
            "label": "Active"
        },
        "role": {
            "value": "host",
            "label": "Host"
        },
        "tenant": None,
        "vrf": None,
        "nat_inside": None,
        "nat_outside": None,
        "dns_name": "test.example.com",
        "description": "Test server IP address",
        "comments": "Used for testing",
        "tags": [],
        "custom_fields": {},
        "created": "2024-01-01T12:00:00Z",
        "last_updated": "2024-01-01T12:00:00Z"
    }


@pytest.fixture
def sample_prefix_data():
    """Provide sample prefix data for testing."""
    return {
        "id": "456e7890-e89b-12d3-a456-426614174000",
        "url": "http://localhost:8000/api/ipam/prefixes/456e7890-e89b-12d3-a456-426614174000/",
        "prefix": "192.168.1.0/24",
        "status": {
            "value": "active",
            "label": "Active"
        },
        "site": {
            "value": "site1",
            "label": "Site 1"
        },
        "vrf": None,
        "tenant": None,
        "vlan": None,
        "role": {
            "value": "lan",
            "label": "LAN"
        },
        "is_pool": False,
        "description": "Test network prefix",
        "comments": "Used for testing",
        "tags": [],
        "custom_fields": {},
        "created": "2024-01-01T12:00:00Z",
        "last_updated": "2024-01-01T12:00:00Z"
    }


@pytest.fixture
def mock_httpx_response():
    """Provide a mock httpx response."""
    response = MagicMock()
    response.status_code = 200
    response.is_success = True
    response.json.return_value = {"results": []}
    return response


@pytest.fixture
def mock_nautobot_client(nautobot_config, sample_ip_address_data, sample_prefix_data):
    """Provide a mock Nautobot client for testing."""
    client = AsyncMock(spec=NautobotClient)
    client.config = nautobot_config
    client.base_url = str(nautobot_config.nautobot_url).rstrip('/')
    client.api_base = f"{client.base_url}/api"
    
    # Mock IP address methods
    sample_ip = IPAddress(**sample_ip_address_data)
    client.get_ip_addresses.return_value = [sample_ip]
    client.get_ip_address_by_id.return_value = sample_ip
    client.search_ip_addresses.return_value = [sample_ip]
    
    # Mock prefix methods
    sample_prefix = Prefix(**sample_prefix_data)
    client.get_prefixes.return_value = [sample_prefix]
    
    # Mock connection test
    client.test_connection.return_value = True
    
    # Mock context manager
    client.__aenter__.return_value = client
    client.__aexit__.return_value = None
    client.close.return_value = None
    
    return client


@pytest.fixture
def nautobot_api_responses():
    """Provide sample API response data for different endpoints."""
    return {
        "status": {
            "status": "ok",
            "version": "2.0.0"
        },
        "ip_addresses": {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "url": "http://localhost:8000/api/ipam/ip-addresses/123e4567-e89b-12d3-a456-426614174000/",
                    "address": "192.168.1.100/24",
                    "status": {"value": "active", "label": "Active"},
                    "role": {"value": "host", "label": "Host"},
                    "tenant": None,
                    "vrf": None,
                    "nat_inside": None,
                    "nat_outside": None,
                    "dns_name": "test.example.com",
                    "description": "Test server IP address",
                    "comments": "Used for testing",
                    "tags": [],
                    "custom_fields": {},
                    "created": "2024-01-01T12:00:00Z",
                    "last_updated": "2024-01-01T12:00:00Z"
                }
            ]
        },
        "prefixes": {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": "456e7890-e89b-12d3-a456-426614174000",
                    "url": "http://localhost:8000/api/ipam/prefixes/456e7890-e89b-12d3-a456-426614174000/",
                    "prefix": "192.168.1.0/24",
                    "status": {"value": "active", "label": "Active"},
                    "site": {"value": "site1", "label": "Site 1"},
                    "vrf": None,
                    "tenant": None,
                    "vlan": None,
                    "role": {"value": "lan", "label": "LAN"},
                    "is_pool": False,
                    "description": "Test network prefix",
                    "comments": "Used for testing",
                    "tags": [],
                    "custom_fields": {},
                    "created": "2024-01-01T12:00:00Z",
                    "last_updated": "2024-01-01T12:00:00Z"
                }
            ]
        }
    }
