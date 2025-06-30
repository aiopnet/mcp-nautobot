"""
Unit tests for the MCP Nautobot server.

These tests verify the functionality of the MCP server endpoints
including tools, resources, and prompts.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import AnyUrl

import mcp.types as types
from mcp_nautobot_server.server import (
    get_nautobot_client,
    handle_list_resources,
    handle_read_resource,
    handle_list_prompts,
    handle_get_prompt,
    handle_list_tools,
    handle_call_tool,
)
from mcp_nautobot_server.nautobot_client import (
    NautobotClient,
    NautobotError,
    NautobotConnectionError,
    IPAddress,
    Prefix
)


class TestGetNautobotClient:
    """Test the get_nautobot_client function."""
    
    @pytest.mark.asyncio
    async def test_get_client_first_time(self, mock_nautobot_client):
        """Test getting client for the first time."""
        # Reset global client
        import mcp_nautobot_server.server as server_module
        server_module.nautobot_client = None
        
        with patch('mcp_nautobot_server.server.NautobotConfig') as mock_config:
            with patch('mcp_nautobot_server.server.NautobotClient') as mock_client_class:
                mock_client_class.return_value = mock_nautobot_client
                
                client = await get_nautobot_client()
                
                assert client == mock_nautobot_client
                mock_nautobot_client.test_connection.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_client_cached(self, mock_nautobot_client):
        """Test getting cached client."""
        import mcp_nautobot_server.server as server_module
        server_module.nautobot_client = mock_nautobot_client
        
        client = await get_nautobot_client()
        
        assert client == mock_nautobot_client
    
    @pytest.mark.asyncio
    async def test_get_client_connection_failure(self):
        """Test getting client when connection fails."""
        import mcp_nautobot_server.server as server_module
        server_module.nautobot_client = None
        
        mock_client = AsyncMock()
        mock_client.test_connection.return_value = False
        
        with patch('mcp_nautobot_server.server.NautobotConfig'):
            with patch('mcp_nautobot_server.server.NautobotClient', return_value=mock_client):
                with pytest.raises(NautobotConnectionError):
                    await get_nautobot_client()


class TestResourceHandlers:
    """Test resource-related handlers."""
    
    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test listing available resources."""
        resources = await handle_list_resources()
        
        assert len(resources) == 3
        assert all(isinstance(r, types.Resource) for r in resources)
        
        # Check specific resources
        resource_uris = [str(r.uri) for r in resources]
        assert "nautobot://ip-addresses" in resource_uris
        assert "nautobot://prefixes" in resource_uris
        assert "nautobot://status" in resource_uris
    
    @pytest.mark.asyncio
    async def test_read_resource_status(self, mock_nautobot_client):
        """Test reading status resource."""
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_read_resource(AnyUrl("nautobot://status"))
            
            assert "connected" in result
            assert "base_url" in result
    
    @pytest.mark.asyncio
    async def test_read_resource_ip_addresses(self, mock_nautobot_client):
        """Test reading IP addresses resource."""
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_read_resource(AnyUrl("nautobot://ip-addresses"))
            
            assert "count" in result
            assert "results" in result
            mock_nautobot_client.get_ip_addresses.assert_called_once_with(limit=10)
    
    @pytest.mark.asyncio
    async def test_read_resource_prefixes(self, mock_nautobot_client):
        """Test reading prefixes resource."""
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_read_resource(AnyUrl("nautobot://prefixes"))
            
            assert "count" in result
            assert "results" in result
            mock_nautobot_client.get_prefixes.assert_called_once_with(limit=10)
    
    @pytest.mark.asyncio
    async def test_read_resource_invalid_scheme(self):
        """Test reading resource with invalid scheme."""
        with pytest.raises(ValueError, match="Unsupported URI scheme"):
            await handle_read_resource(AnyUrl("http://example.com"))
    
    @pytest.mark.asyncio
    async def test_read_resource_invalid_path(self, mock_nautobot_client):
        """Test reading resource with invalid path."""
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            with pytest.raises(ValueError, match="Unknown resource path"):
                await handle_read_resource(AnyUrl("nautobot://invalid"))


class TestPromptHandlers:
    """Test prompt-related handlers."""
    
    @pytest.mark.asyncio
    async def test_list_prompts(self):
        """Test listing available prompts."""
        prompts = await handle_list_prompts()
        
        assert len(prompts) == 2
        assert all(isinstance(p, types.Prompt) for p in prompts)
        
        prompt_names = [p.name for p in prompts]
        assert "ip-summary-report" in prompt_names
        assert "network-utilization" in prompt_names
    
    @pytest.mark.asyncio
    async def test_get_prompt_ip_summary_report(self, mock_nautobot_client):
        """Test getting IP summary report prompt."""
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_get_prompt(
                "ip-summary-report",
                {"network": "192.168.1.0/24", "status": "active"}
            )
            
            assert isinstance(result, types.GetPromptResult)
            assert "IP Address Summary Report" in result.description
            assert len(result.messages) == 1
            
            mock_nautobot_client.get_ip_addresses.assert_called_once_with(
                prefix="192.168.1.0/24",
                status="active",
                limit=100
            )
    
    @pytest.mark.asyncio
    async def test_get_prompt_network_utilization(self, mock_nautobot_client):
        """Test getting network utilization prompt."""
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_get_prompt(
                "network-utilization",
                {"prefix": "10.0.0.0/8", "depth": "detailed"}
            )
            
            assert isinstance(result, types.GetPromptResult)
            assert "Network Utilization Analysis" in result.description
            
            mock_nautobot_client.get_ip_addresses.assert_called_once_with(
                prefix="10.0.0.0/8",
                limit=1000
            )
            mock_nautobot_client.get_prefixes.assert_called_once_with(
                prefix="10.0.0.0/8",
                limit=100
            )
    
    @pytest.mark.asyncio
    async def test_get_prompt_network_utilization_missing_prefix(self):
        """Test getting network utilization prompt without required prefix."""
        with pytest.raises(ValueError, match="Network prefix is required"):
            await handle_get_prompt("network-utilization", {})
    
    @pytest.mark.asyncio
    async def test_get_prompt_invalid_name(self):
        """Test getting prompt with invalid name."""
        with pytest.raises(ValueError, match="Unknown prompt"):
            await handle_get_prompt("invalid-prompt", {})


class TestToolHandlers:
    """Test tool-related handlers."""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available tools."""
        tools = await handle_list_tools()
        
        assert len(tools) == 5
        assert all(isinstance(t, types.Tool) for t in tools)
        
        tool_names = [t.name for t in tools]
        expected_tools = [
            "get_ip_addresses",
            "get_prefixes",
            "get_ip_address_by_id",
            "search_ip_addresses",
            "test_connection"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tool_names
    
    @pytest.mark.asyncio
    async def test_call_tool_get_ip_addresses(self, mock_nautobot_client):
        """Test calling get_ip_addresses tool."""
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_call_tool(
                "get_ip_addresses",
                {
                    "prefix": "192.168.1.0/24",
                    "status": "active",
                    "limit": 50
                }
            )
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Retrieved" in result[0].text
            
            mock_nautobot_client.get_ip_addresses.assert_called_once_with(
                address=None,
                prefix="192.168.1.0/24",
                status="active",
                role=None,
                tenant=None,
                vrf=None,
                limit=50,
                offset=0
            )
    
    @pytest.mark.asyncio
    async def test_call_tool_get_prefixes(self, mock_nautobot_client):
        """Test calling get_prefixes tool."""
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_call_tool(
                "get_prefixes",
                {"site": "main-site", "limit": 25}
            )
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            
            mock_nautobot_client.get_prefixes.assert_called_once_with(
                prefix=None,
                status=None,
                site="main-site",
                role=None,
                tenant=None,
                vrf=None,
                limit=25,
                offset=0
            )
    
    @pytest.mark.asyncio
    async def test_call_tool_get_ip_address_by_id(self, mock_nautobot_client, sample_ip_address_data):
        """Test calling get_ip_address_by_id tool."""
        ip_address = IPAddress(**sample_ip_address_data)
        mock_nautobot_client.get_ip_address_by_id.return_value = ip_address
        
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_call_tool(
                "get_ip_address_by_id",
                {"ip_id": "123e4567-e89b-12d3-a456-426614174000"}
            )
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Retrieved IP address" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_get_ip_address_by_id_not_found(self, mock_nautobot_client):
        """Test calling get_ip_address_by_id tool when IP not found."""
        mock_nautobot_client.get_ip_address_by_id.return_value = None
        
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_call_tool(
                "get_ip_address_by_id",
                {"ip_id": "nonexistent"}
            )
            
            assert len(result) == 1
            assert "not found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_get_ip_address_by_id_missing_argument(self):
        """Test calling get_ip_address_by_id tool without required argument."""
        with pytest.raises(ValueError, match="ip_id is required"):
            await handle_call_tool("get_ip_address_by_id", {})
    
    @pytest.mark.asyncio
    async def test_call_tool_search_ip_addresses(self, mock_nautobot_client):
        """Test calling search_ip_addresses tool."""
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_call_tool(
                "search_ip_addresses",
                {"query": "192.168", "limit": 30}
            )
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            
            mock_nautobot_client.search_ip_addresses.assert_called_once_with(
                "192.168",
                30
            )
    
    @pytest.mark.asyncio
    async def test_call_tool_search_ip_addresses_missing_query(self):
        """Test calling search_ip_addresses tool without query."""
        with pytest.raises(ValueError, match="query is required"):
            await handle_call_tool("search_ip_addresses", {})
    
    @pytest.mark.asyncio
    async def test_call_tool_test_connection(self, mock_nautobot_client):
        """Test calling test_connection tool."""
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_call_tool("test_connection", {})
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Connected" in result[0].text
            
            mock_nautobot_client.test_connection.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_call_tool_invalid_tool(self):
        """Test calling invalid tool."""
        with pytest.raises(ValueError, match="Unknown tool"):
            await handle_call_tool("invalid_tool", {})
    
    @pytest.mark.asyncio
    async def test_call_tool_limit_capping(self, mock_nautobot_client):
        """Test that tool limits are properly capped."""
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            # Test IP addresses limit capping
            await handle_call_tool(
                "get_ip_addresses",
                {"limit": 5000}  # Should be capped to 1000
            )
            
            mock_nautobot_client.get_ip_addresses.assert_called_once()
            args, kwargs = mock_nautobot_client.get_ip_addresses.call_args
            # The limit should be capped to 1000
            assert kwargs.get('limit') == 1000
    
    @pytest.mark.asyncio
    async def test_call_tool_authentication_error(self, mock_nautobot_client):
        """Test tool call with authentication error."""
        from mcp_nautobot_server.nautobot_client import NautobotAuthenticationError
        
        mock_nautobot_client.test_connection.side_effect = NautobotAuthenticationError("Auth failed")
        
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_call_tool("test_connection", {})
            
            assert len(result) == 1
            assert "Authentication failed" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_connection_error(self, mock_nautobot_client):
        """Test tool call with connection error."""
        mock_nautobot_client.test_connection.side_effect = NautobotConnectionError("Connection failed")
        
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_call_tool("test_connection", {})
            
            assert len(result) == 1
            assert "Connection error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_generic_error(self, mock_nautobot_client):
        """Test tool call with generic error."""
        mock_nautobot_client.test_connection.side_effect = Exception("Unexpected error")
        
        with patch('mcp_nautobot_server.server.get_nautobot_client', return_value=mock_nautobot_client):
            result = await handle_call_tool("test_connection", {})
            
            assert len(result) == 1
            assert "Unexpected error" in result[0].text
