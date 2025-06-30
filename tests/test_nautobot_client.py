"""
Unit tests for the Nautobot API client.

These tests verify the functionality of the NautobotClient class
including authentication, error handling, and data retrieval.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch

from mcp_nautobot_server.nautobot_client import (
    NautobotClient,
    NautobotConfig,
    NautobotAuthenticationError,
    NautobotConnectionError,
    NautobotAPIError,
    IPAddress,
    Prefix,
    RateLimiter
)


class TestNautobotConfig:
    """Test the NautobotConfig class."""
    
    def test_config_creation_with_valid_data(self):
        """Test creating config with valid data."""
        config = NautobotConfig(
            nautobot_url="http://localhost:8000",  # type: ignore
            nautobot_token="test-token"
        )
        assert str(config.nautobot_url) == "http://localhost:8000/"
        assert config.nautobot_token == "test-token"
        assert config.nautobot_verify_ssl is True
        assert config.nautobot_timeout == 30
        assert config.nautobot_rate_limit == 100
    
    def test_config_with_custom_values(self):
        """Test creating config with custom values."""
        config = NautobotConfig(
            nautobot_url="https://nautobot.example.com",  # type: ignore
            nautobot_token="custom-token",
            nautobot_verify_ssl=False,
            nautobot_timeout=60,
            nautobot_rate_limit=50
        )
        assert "nautobot.example.com" in str(config.nautobot_url)
        assert config.nautobot_verify_ssl is False
        assert config.nautobot_timeout == 60
        assert config.nautobot_rate_limit == 50


class TestRateLimiter:
    """Test the RateLimiter class."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_allows_requests_within_limit(self):
        """Test that rate limiter allows requests within the limit."""
        limiter = RateLimiter(max_requests=5, time_window=60)
        
        # Should allow first 5 requests without delay
        for _ in range(5):
            await limiter.acquire()
        
        assert len(limiter.requests) == 5
    
    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_excess_requests(self):
        """Test that rate limiter blocks requests exceeding the limit."""
        limiter = RateLimiter(max_requests=2, time_window=1)
        
        # First two requests should be immediate
        await limiter.acquire()
        await limiter.acquire()
        
        # Third request should be delayed (we'll patch sleep to avoid waiting)
        with patch('asyncio.sleep') as mock_sleep:
            await limiter.acquire()
            mock_sleep.assert_called_once()


class TestNautobotClient:
    """Test the NautobotClient class."""
    
    def test_client_initialization(self, nautobot_config):
        """Test client initialization with config."""
        client = NautobotClient(nautobot_config)
        
        assert client.config == nautobot_config
        assert client.base_url == "http://localhost:8000"
        assert client.api_base == "http://localhost:8000/api"
        assert client.client is not None
        assert client.rate_limiter is not None
    
    @pytest.mark.asyncio
    async def test_close_method(self, nautobot_config):
        """Test that close method properly closes the HTTP client."""
        client = NautobotClient(nautobot_config)
        
        with patch.object(client.client, 'aclose') as mock_close:
            await client.close()
            mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_context_manager(self, nautobot_config):
        """Test client as async context manager."""
        async with NautobotClient(nautobot_config) as client:
            assert isinstance(client, NautobotClient)
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, nautobot_config, mock_httpx_response):
        """Test successful API request."""
        client = NautobotClient(nautobot_config)
        
        mock_httpx_response.json.return_value = {"status": "ok"}
        
        with patch.object(client.client, 'request', return_value=mock_httpx_response):
            with patch.object(client.rate_limiter, 'acquire'):
                result = await client._make_request("GET", "/status/")
                
                assert result == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_make_request_authentication_error(self, nautobot_config):
        """Test API request with authentication error."""
        client = NautobotClient(nautobot_config)
        
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch.object(client.client, 'request', return_value=mock_response):
            with patch.object(client.rate_limiter, 'acquire'):
                with pytest.raises(NautobotAuthenticationError):
                    await client._make_request("GET", "/status/")
    
    @pytest.mark.asyncio
    async def test_make_request_api_error(self, nautobot_config):
        """Test API request with API error."""
        client = NautobotClient(nautobot_config)
        
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.is_success = False
        mock_response.text = "Internal Server Error"
        
        with patch.object(client.client, 'request', return_value=mock_response):
            with patch.object(client.rate_limiter, 'acquire'):
                with pytest.raises(NautobotAPIError) as exc_info:
                    await client._make_request("GET", "/status/")
                
                assert exc_info.value.status_code == 500
    
    @pytest.mark.asyncio
    async def test_make_request_connection_error(self, nautobot_config):
        """Test API request with connection error."""
        client = NautobotClient(nautobot_config)
        
        with patch.object(client.client, 'request', side_effect=httpx.ConnectError("Connection failed")):
            with patch.object(client.rate_limiter, 'acquire'):
                with pytest.raises(NautobotConnectionError):
                    await client._make_request("GET", "/status/")
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, nautobot_config):
        """Test successful connection test."""
        client = NautobotClient(nautobot_config)
        
        with patch.object(client, '_make_request', return_value={"status": "ok"}):
            result = await client.test_connection()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, nautobot_config):
        """Test failed connection test."""
        client = NautobotClient(nautobot_config)
        
        with patch.object(client, '_make_request', side_effect=NautobotConnectionError("Failed")):
            result = await client.test_connection()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_ip_addresses(self, nautobot_config, nautobot_api_responses, sample_ip_address_data):
        """Test retrieving IP addresses."""
        client = NautobotClient(nautobot_config)
        
        with patch.object(client, '_make_request', return_value=nautobot_api_responses["ip_addresses"]):
            ip_addresses = await client.get_ip_addresses(limit=10)
            
            assert len(ip_addresses) == 1
            assert isinstance(ip_addresses[0], IPAddress)
            assert ip_addresses[0].address == "192.168.1.100/24"
    
    @pytest.mark.asyncio
    async def test_get_ip_addresses_with_filters(self, nautobot_config, nautobot_api_responses):
        """Test retrieving IP addresses with filters."""
        client = NautobotClient(nautobot_config)
        
        with patch.object(client, '_make_request', return_value=nautobot_api_responses["ip_addresses"]) as mock_request:
            await client.get_ip_addresses(
                address="192.168.1.100",
                prefix="192.168.1.0/24",
                status="active",
                role="host",
                tenant="test-tenant",
                vrf="test-vrf",
                limit=50,
                offset=10
            )
            
            # Verify the request was made with correct parameters
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            params = kwargs.get('params', {})
            
            assert params['address'] == "192.168.1.100"
            assert params['parent'] == "192.168.1.0/24"
            assert params['status'] == "active"
            assert params['role'] == "host"
            assert params['tenant'] == "test-tenant"
            assert params['vrf'] == "test-vrf"
            assert params['limit'] == 50
            assert params['offset'] == 10
    
    @pytest.mark.asyncio
    async def test_get_prefixes(self, nautobot_config, nautobot_api_responses):
        """Test retrieving prefixes."""
        client = NautobotClient(nautobot_config)
        
        with patch.object(client, '_make_request', return_value=nautobot_api_responses["prefixes"]):
            prefixes = await client.get_prefixes(limit=10)
            
            assert len(prefixes) == 1
            assert isinstance(prefixes[0], Prefix)
            assert prefixes[0].prefix == "192.168.1.0/24"
    
    @pytest.mark.asyncio
    async def test_get_ip_address_by_id_found(self, nautobot_config, sample_ip_address_data):
        """Test retrieving IP address by ID when found."""
        client = NautobotClient(nautobot_config)
        
        with patch.object(client, '_make_request', return_value=sample_ip_address_data):
            ip_address = await client.get_ip_address_by_id("123e4567-e89b-12d3-a456-426614174000")
            
            assert ip_address is not None
            assert isinstance(ip_address, IPAddress)
            assert ip_address.id == "123e4567-e89b-12d3-a456-426614174000"
    
    @pytest.mark.asyncio
    async def test_get_ip_address_by_id_not_found(self, nautobot_config):
        """Test retrieving IP address by ID when not found."""
        client = NautobotClient(nautobot_config)
        
        with patch.object(client, '_make_request', side_effect=NautobotAPIError("Not found", 404)):
            ip_address = await client.get_ip_address_by_id("nonexistent-id")
            
            assert ip_address is None
    
    @pytest.mark.asyncio
    async def test_search_ip_addresses(self, nautobot_config, nautobot_api_responses):
        """Test searching IP addresses."""
        client = NautobotClient(nautobot_config)
        
        with patch.object(client, '_make_request', return_value=nautobot_api_responses["ip_addresses"]) as mock_request:
            ip_addresses = await client.search_ip_addresses("192.168", limit=25)
            
            assert len(ip_addresses) == 1
            
            # Verify search parameters
            args, kwargs = mock_request.call_args
            params = kwargs.get('params', {})
            assert params['q'] == "192.168"
            assert params['limit'] == 25
    
    @pytest.mark.asyncio
    async def test_error_handling_with_invalid_data(self, nautobot_config):
        """Test error handling when API returns invalid data."""
        client = NautobotClient(nautobot_config)
        
        # Return invalid IP address data
        invalid_response = {
            "results": [
                {
                    "id": "invalid-id",
                    # Missing required fields
                }
            ]
        }
        
        with patch.object(client, '_make_request', return_value=invalid_response):
            # Should handle invalid data gracefully
            ip_addresses = await client.get_ip_addresses()
            assert len(ip_addresses) == 0  # Invalid entries should be skipped
