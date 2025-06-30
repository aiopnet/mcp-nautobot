"""
Nautobot API client for MCP server integration.

This module provides a client for interacting with Nautobot's REST API,
specifically focused on IP address data retrieval and management.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, Field, HttpUrl
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class NautobotConfig(BaseSettings):
    """Configuration for Nautobot API connection."""
    
    nautobot_url: HttpUrl = Field(
        description="Base URL for the Nautobot instance"
    )
    nautobot_token: str = Field(
        description="API token for Nautobot authentication"
    )
    nautobot_verify_ssl: bool = Field(
        default=True,
        description="Whether to verify SSL certificates"
    )
    nautobot_timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    nautobot_rate_limit: int = Field(
        default=100,
        description="Maximum requests per minute"
    )
    
    class Config:
        env_file = ".env"
        env_prefix = ""


class IPAddress(BaseModel):
    """Pydantic model for Nautobot IP address data."""
    
    id: str
    url: HttpUrl
    address: str
    status: Dict[str, Any]
    role: Optional[Dict[str, Any]] = None
    tenant: Optional[Dict[str, Any]] = None
    vrf: Optional[Dict[str, Any]] = None
    nat_inside: Optional[Dict[str, Any]] = None
    nat_outside: Optional[Dict[str, Any]] = None
    dns_name: Optional[str] = None
    description: Optional[str] = None
    comments: Optional[str] = None
    tags: List[Dict[str, Any]] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    created: str
    last_updated: str


class Prefix(BaseModel):
    """Pydantic model for Nautobot prefix data."""
    
    id: str
    url: HttpUrl
    prefix: str
    status: Dict[str, Any]
    site: Optional[Dict[str, Any]] = None
    vrf: Optional[Dict[str, Any]] = None
    tenant: Optional[Dict[str, Any]] = None
    vlan: Optional[Dict[str, Any]] = None
    role: Optional[Dict[str, Any]] = None
    is_pool: bool = False
    description: Optional[str] = None
    comments: Optional[str] = None
    tags: List[Dict[str, Any]] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    created: str
    last_updated: str


class NautobotError(Exception):
    """Base exception for Nautobot client errors."""
    pass


class NautobotAuthenticationError(NautobotError):
    """Exception raised for authentication failures."""
    pass


class NautobotConnectionError(NautobotError):
    """Exception raised for connection failures."""
    pass


class NautobotAPIError(NautobotError):
    """Exception raised for API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            # Remove old requests outside the time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            if len(self.requests) >= self.max_requests:
                # Calculate sleep time
                oldest_request = min(self.requests)
                sleep_time = self.time_window - (now - oldest_request)
                if sleep_time > 0:
                    logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                    await asyncio.sleep(sleep_time)
            
            self.requests.append(now)


class NautobotClient:
    """
    Asynchronous client for interacting with Nautobot REST API.
    
    This client provides methods for retrieving IP address and network data
    from a Nautobot instance with proper authentication, error handling,
    and rate limiting.
    """
    
    def __init__(self, config: NautobotConfig):
        self.config = config
        self.base_url = str(config.nautobot_url).rstrip('/')
        self.api_base = f"{self.base_url}/api"
        
        # Set up HTTP client
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Token {config.nautobot_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=config.nautobot_timeout,
            verify=config.nautobot_verify_ssl,
        )
        
        # Set up rate limiter
        self.rate_limiter = RateLimiter(config.nautobot_rate_limit)
        
        logger.info(f"Initialized Nautobot client for {self.base_url}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Nautobot API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            NautobotAuthenticationError: For 401/403 responses
            NautobotAPIError: For other HTTP errors
            NautobotConnectionError: For connection issues
        """
        await self.rate_limiter.acquire()
        
        url = urljoin(f"{self.api_base}/", endpoint.lstrip('/'))
        
        try:
            logger.debug(f"Making {method} request to {url} with params: {params}")
            
            response = await self.client.request(
                method=method,
                url=url,
                params=params
            )
            
            # Handle authentication errors
            if response.status_code in (401, 403):
                raise NautobotAuthenticationError(
                    f"Authentication failed: {response.status_code} {response.text}"
                )
            
            # Handle other HTTP errors
            if not response.is_success:
                raise NautobotAPIError(
                    f"API request failed: {response.status_code} {response.text}",
                    status_code=response.status_code
                )
            
            return response.json()
            
        except httpx.ConnectError as e:
            raise NautobotConnectionError(f"Failed to connect to Nautobot: {e}")
        except httpx.TimeoutException as e:
            raise NautobotConnectionError(f"Request timeout: {e}")
        except httpx.HTTPError as e:
            raise NautobotConnectionError(f"HTTP error: {e}")
    
    async def test_connection(self) -> bool:
        """
        Test the connection to Nautobot API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            await self._make_request("GET", "/status/")
            logger.info("Successfully connected to Nautobot API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Nautobot API: {e}")
            return False
    
    async def get_ip_addresses(
        self,
        address: Optional[str] = None,
        prefix: Optional[str] = None,
        status: Optional[str] = None,
        role: Optional[str] = None,
        tenant: Optional[str] = None,
        vrf: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[IPAddress]:
        """
        Retrieve IP addresses from Nautobot.
        
        Args:
            address: Filter by specific IP address
            prefix: Filter by network prefix
            status: Filter by status slug
            role: Filter by role slug
            tenant: Filter by tenant slug
            vrf: Filter by VRF name
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of IPAddress objects
            
        Raises:
            NautobotError: For API or connection errors
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        
        # Add optional filters
        if address:
            params["address"] = address
        if prefix:
            params["parent"] = prefix
        if status:
            params["status"] = status
        if role:
            params["role"] = role
        if tenant:
            params["tenant"] = tenant
        if vrf:
            params["vrf"] = vrf
        
        try:
            response = await self._make_request("GET", "/ipam/ip-addresses/", params)
            
            # Parse results
            ip_addresses = []
            for item in response.get("results", []):
                try:
                    ip_addresses.append(IPAddress(**item))
                except Exception as e:
                    logger.warning(f"Failed to parse IP address data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(ip_addresses)} IP addresses")
            return ip_addresses
            
        except Exception as e:
            logger.error(f"Failed to retrieve IP addresses: {e}")
            raise
    
    async def get_prefixes(
        self,
        prefix: Optional[str] = None,
        status: Optional[str] = None,
        site: Optional[str] = None,
        role: Optional[str] = None,
        tenant: Optional[str] = None,
        vrf: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Prefix]:
        """
        Retrieve network prefixes from Nautobot.
        
        Args:
            prefix: Filter by network prefix
            status: Filter by status slug
            site: Filter by site slug
            role: Filter by role slug
            tenant: Filter by tenant slug
            vrf: Filter by VRF name
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of Prefix objects
            
        Raises:
            NautobotError: For API or connection errors
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        
        # Add optional filters
        if prefix:
            params["prefix"] = prefix
        if status:
            params["status"] = status
        if site:
            params["site"] = site
        if role:
            params["role"] = role
        if tenant:
            params["tenant"] = tenant
        if vrf:
            params["vrf"] = vrf
        
        try:
            response = await self._make_request("GET", "/ipam/prefixes/", params)
            
            # Parse results
            prefixes = []
            for item in response.get("results", []):
                try:
                    prefixes.append(Prefix(**item))
                except Exception as e:
                    logger.warning(f"Failed to parse prefix data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(prefixes)} prefixes")
            return prefixes
            
        except Exception as e:
            logger.error(f"Failed to retrieve prefixes: {e}")
            raise
    
    async def get_ip_address_by_id(self, ip_id: str) -> Optional[IPAddress]:
        """
        Retrieve a specific IP address by its ID.
        
        Args:
            ip_id: The IP address ID
            
        Returns:
            IPAddress object or None if not found
            
        Raises:
            NautobotError: For API or connection errors
        """
        try:
            response = await self._make_request("GET", f"/ipam/ip-addresses/{ip_id}/")
            return IPAddress(**response)
        except NautobotAPIError as e:
            if e.status_code == 404:
                return None
            raise
    
    async def search_ip_addresses(
        self, 
        query: str, 
        limit: int = 50
    ) -> List[IPAddress]:
        """
        Search IP addresses using a general query.
        
        Args:
            query: Search query (can be IP, description, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching IPAddress objects
        """
        params: Dict[str, Any] = {
            "q": query,
            "limit": limit,
        }
        
        try:
            response = await self._make_request("GET", "/ipam/ip-addresses/", params)
            
            ip_addresses = []
            for item in response.get("results", []):
                try:
                    ip_addresses.append(IPAddress(**item))
                except Exception as e:
                    logger.warning(f"Failed to parse IP address data: {e}")
                    continue
            
            logger.info(f"Found {len(ip_addresses)} IP addresses matching '{query}'")
            return ip_addresses
            
        except Exception as e:
            logger.error(f"Failed to search IP addresses: {e}")
            raise
