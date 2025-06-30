"""
MCP Server for Nautobot IP Address Data Integration.

This server provides Model Context Protocol (MCP) tools for retrieving
IP address and network data from a Nautobot instance. It includes
comprehensive error handling, rate limiting, and logging.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl, ValidationError
import mcp.server.stdio

from .nautobot_client import (
    NautobotClient, 
    NautobotConfig, 
    NautobotError,
    NautobotAuthenticationError,
    NautobotConnectionError,
    NautobotAPIError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
server = Server("mcp-nautobot-server")
nautobot_client: Optional[NautobotClient] = None


async def get_nautobot_client() -> NautobotClient:
    """
    Get or create a Nautobot client instance.
    
    Returns:
        Configured NautobotClient instance
        
    Raises:
        NautobotError: If configuration is invalid or connection fails
    """
    global nautobot_client
    
    if nautobot_client is None:
        try:
            # Load configuration from environment
            import os
            config = NautobotConfig(
                nautobot_url=os.getenv("NAUTOBOT_URL", "http://localhost:8000"),  # type: ignore
                nautobot_token=os.getenv("NAUTOBOT_TOKEN", ""),
            )
            nautobot_client = NautobotClient(config)
            
            # Test the connection
            if not await nautobot_client.test_connection():
                raise NautobotConnectionError("Failed to connect to Nautobot API")
                
            logger.info("Successfully initialized Nautobot client")
            
        except ValidationError as e:
            error_msg = f"Invalid Nautobot configuration: {e}"
            logger.error(error_msg)
            raise NautobotError(error_msg)
        except Exception as e:
            error_msg = f"Failed to initialize Nautobot client: {e}"
            logger.error(error_msg)
            raise NautobotError(error_msg)
    
    return nautobot_client


@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """
    List available Nautobot resources.
    
    This endpoint provides metadata about available Nautobot data sources
    that can be accessed through the MCP server.
    """
    return [
        types.Resource(
            uri=AnyUrl("nautobot://ip-addresses"),
            name="IP Addresses",
            description="Nautobot IP address data with filtering capabilities",
            mimeType="application/json",
        ),
        types.Resource(
            uri=AnyUrl("nautobot://prefixes"),
            name="Network Prefixes", 
            description="Nautobot network prefix data with filtering capabilities",
            mimeType="application/json",
        ),
        types.Resource(
            uri=AnyUrl("nautobot://status"),
            name="Nautobot Connection Status",
            description="Current status of the Nautobot API connection",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific Nautobot resource.
    
    Args:
        uri: Resource URI (e.g., nautobot://status)
        
    Returns:
        JSON string with resource data
        
    Raises:
        ValueError: For unsupported URI schemes or paths
        NautobotError: For API connection issues
    """
    if uri.scheme != "nautobot":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")
    
    path = uri.path or ""
    
    try:
        client = await get_nautobot_client()
        
        if path == "status":
            # Return connection status
            is_connected = await client.test_connection()
            import json
            return json.dumps({
                "connected": is_connected,
                "base_url": client.base_url,
                "api_version": "2.0"  # Nautobot API version
            })
        
        elif path == "ip-addresses":
            # Return sample IP addresses (limited for resource view)
            ip_addresses = await client.get_ip_addresses(limit=10)
            import json
            return json.dumps({
                "count": len(ip_addresses),
                "results": [ip.model_dump() for ip in ip_addresses]
            })
        
        elif path == "prefixes":
            # Return sample prefixes (limited for resource view)
            prefixes = await client.get_prefixes(limit=10)
            import json
            return json.dumps({
                "count": len(prefixes),
                "results": [prefix.model_dump() for prefix in prefixes]
            })
        
        else:
            raise ValueError(f"Unknown resource path: {path}")
            
    except Exception as e:
        logger.error(f"Failed to read resource {uri}: {e}")
        raise


@server.list_prompts()
async def handle_list_prompts() -> List[types.Prompt]:
    """
    List available prompts for Nautobot data analysis.
    
    These prompts help users generate useful queries and reports
    based on Nautobot IP address data.
    """
    return [
        types.Prompt(
            name="ip-summary-report",
            description="Generate a comprehensive IP address summary report",
            arguments=[
                types.PromptArgument(
                    name="network",
                    description="Network prefix to analyze (e.g., 10.0.0.0/8)",
                    required=False,
                ),
                types.PromptArgument(
                    name="status",
                    description="Filter by IP status (active, reserved, deprecated)",
                    required=False,
                ),
                types.PromptArgument(
                    name="include_details",
                    description="Include detailed information (true/false)",
                    required=False,
                ),
            ],
        ),
        types.Prompt(
            name="network-utilization",
            description="Analyze network prefix utilization and capacity",
            arguments=[
                types.PromptArgument(
                    name="prefix",
                    description="Network prefix to analyze",
                    required=True,
                ),
                types.PromptArgument(
                    name="depth",
                    description="Analysis depth (summary/detailed)",
                    required=False,
                ),
            ],
        ),
    ]


@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: Dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt with Nautobot data for analysis.
    
    Args:
        name: Prompt name
        arguments: Prompt arguments
        
    Returns:
        Generated prompt with current Nautobot data
        
    Raises:
        ValueError: For unknown prompts
        NautobotError: For API connection issues
    """
    args = arguments or {}
    
    try:
        client = await get_nautobot_client()
        
        if name == "ip-summary-report":
            # Get IP addresses based on filters
            network = args.get("network")
            status = args.get("status")
            include_details = args.get("include_details", "false").lower() == "true"
            
            ip_addresses = await client.get_ip_addresses(
                prefix=network,
                status=status,
                limit=100
            )
            
            # Build prompt content
            content_parts = [
                "IP Address Summary Report for Nautobot",
                f"Generated from {client.base_url}",
                "",
            ]
            
            if network:
                content_parts.append(f"Network: {network}")
            if status:
                content_parts.append(f"Status Filter: {status}")
            
            content_parts.extend([
                f"Total IP Addresses Found: {len(ip_addresses)}",
                "",
                "IP Address Data:",
            ])
            
            for ip in ip_addresses[:20]:  # Limit to first 20 for prompt
                if include_details:
                    content_parts.append(
                        f"- {ip.address} | Status: {ip.status.get('label', 'Unknown')} | "
                        f"Description: {ip.description or 'N/A'}"
                    )
                else:
                    content_parts.append(f"- {ip.address}")
            
            if len(ip_addresses) > 20:
                content_parts.append(f"... and {len(ip_addresses) - 20} more")
            
            content_parts.extend([
                "",
                "Please analyze this IP address data and provide insights about:",
                "1. Address utilization patterns",
                "2. Status distribution",
                "3. Any potential issues or recommendations",
            ])
            
            return types.GetPromptResult(
                description=f"IP Summary Report for {network or 'all networks'}",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text="\n".join(content_parts),
                        ),
                    )
                ],
            )
        
        elif name == "network-utilization":
            prefix = args.get("prefix")
            if not prefix:
                raise ValueError("Network prefix is required for utilization analysis")
            
            depth = args.get("depth", "summary")
            
            # Get IP addresses and prefixes for the network
            ip_addresses = await client.get_ip_addresses(prefix=prefix, limit=1000)
            prefixes = await client.get_prefixes(prefix=prefix, limit=100)
            
            content_parts = [
                f"Network Utilization Analysis for {prefix}",
                f"Generated from {client.base_url}",
                "",
                f"Analysis Depth: {depth}",
                "",
                f"IP Addresses in Network: {len(ip_addresses)}",
                f"Sub-prefixes Found: {len(prefixes)}",
                "",
            ]
            
            if depth == "detailed":
                # Group by status
                status_counts = {}
                for ip in ip_addresses:
                    status_label = ip.status.get('label', 'Unknown')
                    status_counts[status_label] = status_counts.get(status_label, 0) + 1
                
                content_parts.append("Status Distribution:")
                for status, count in status_counts.items():
                    content_parts.append(f"- {status}: {count}")
                content_parts.append("")
                
                if prefixes:
                    content_parts.append("Sub-prefixes:")
                    for prefix_obj in prefixes[:10]:
                        content_parts.append(
                            f"- {prefix_obj.prefix} | Status: {prefix_obj.status.get('label', 'Unknown')}"
                        )
                    if len(prefixes) > 10:
                        content_parts.append(f"... and {len(prefixes) - 10} more")
                    content_parts.append("")
            
            content_parts.extend([
                "Please analyze this network utilization data and provide:",
                "1. Capacity assessment",
                "2. Utilization efficiency",
                "3. Growth recommendations",
                "4. Any potential optimization opportunities",
            ])
            
            return types.GetPromptResult(
                description=f"Network Utilization Analysis for {prefix}",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text="\n".join(content_parts),
                        ),
                    )
                ],
            )
        
        else:
            raise ValueError(f"Unknown prompt: {name}")
            
    except Exception as e:
        logger.error(f"Failed to generate prompt '{name}': {e}")
        raise


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available Nautobot tools.
    
    These tools provide comprehensive IP address and network data
    retrieval capabilities with various filtering options.
    """
    return [
        types.Tool(
            name="get_ip_addresses",
            description="Retrieve IP addresses from Nautobot with filtering options",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Specific IP address to search for"
                    },
                    "prefix": {
                        "type": "string", 
                        "description": "Network prefix to filter by (e.g., 10.0.0.0/24)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Status to filter by (e.g., active, reserved, deprecated)"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role to filter by (e.g., loopback, secondary, anycast)"
                    },
                    "tenant": {
                        "type": "string",
                        "description": "Tenant to filter by"
                    },
                    "vrf": {
                        "type": "string",
                        "description": "VRF to filter by"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 100, max: 1000)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 1000
                    },
                    "offset": {
                        "type": "integer", 
                        "description": "Number of results to skip for pagination (default: 0)",
                        "default": 0,
                        "minimum": 0
                    }
                },
                "additionalProperties": False
            },
        ),
        types.Tool(
            name="get_prefixes",
            description="Retrieve network prefixes from Nautobot with filtering options",
            inputSchema={
                "type": "object",
                "properties": {
                    "prefix": {
                        "type": "string",
                        "description": "Specific network prefix to search for"
                    },
                    "status": {
                        "type": "string",
                        "description": "Status to filter by"
                    },
                    "site": {
                        "type": "string",
                        "description": "Site to filter by"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role to filter by"
                    },
                    "tenant": {
                        "type": "string",
                        "description": "Tenant to filter by"
                    },
                    "vrf": {
                        "type": "string",
                        "description": "VRF to filter by"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 100, max: 1000)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 1000
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination (default: 0)", 
                        "default": 0,
                        "minimum": 0
                    }
                },
                "additionalProperties": False
            },
        ),
        types.Tool(
            name="get_ip_address_by_id",
            description="Retrieve a specific IP address by its Nautobot ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "ip_id": {
                        "type": "string",
                        "description": "The Nautobot ID of the IP address"
                    }
                },
                "required": ["ip_id"],
                "additionalProperties": False
            },
        ),
        types.Tool(
            name="search_ip_addresses",
            description="Search IP addresses using a general query string",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (can match IP address, description, etc.)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 50, max: 500)",
                        "default": 50,
                        "minimum": 1,
                        "maximum": 500
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            },
        ),
        types.Tool(
            name="test_connection",
            description="Test the connection to the Nautobot API",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any] | None
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests for Nautobot operations.
    
    Args:
        name: Tool name to execute
        arguments: Tool arguments
        
    Returns:
        List of content objects with results
        
    Raises:
        ValueError: For unknown tools or invalid arguments
        NautobotError: For API or connection errors
    """
    args = arguments or {}
    
    try:
        client = await get_nautobot_client()
        
        if name == "get_ip_addresses":
            # Extract and validate arguments
            address = args.get("address")
            prefix = args.get("prefix") 
            status = args.get("status")
            role = args.get("role")
            tenant = args.get("tenant")
            vrf = args.get("vrf")
            limit = min(args.get("limit", 100), 1000)  # Cap at 1000
            offset = args.get("offset", 0)
            
            logger.info(f"Retrieving IP addresses with filters: {args}")
            
            # Get IP addresses from Nautobot
            ip_addresses = await client.get_ip_addresses(
                address=address,
                prefix=prefix,
                status=status,
                role=role,
                tenant=tenant,
                vrf=vrf,
                limit=limit,
                offset=offset
            )
            
            # Format results
            result = {
                "count": len(ip_addresses),
                "filters_applied": {k: v for k, v in args.items() if v is not None},
                "results": [ip.model_dump() for ip in ip_addresses]
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Retrieved {len(ip_addresses)} IP addresses from Nautobot:\n\n"
                         f"```json\n{result}\n```"
                )
            ]
        
        elif name == "get_prefixes":
            # Extract and validate arguments
            prefix = args.get("prefix")
            status = args.get("status")
            site = args.get("site")
            role = args.get("role")
            tenant = args.get("tenant")
            vrf = args.get("vrf")
            limit = min(args.get("limit", 100), 1000)  # Cap at 1000
            offset = args.get("offset", 0)
            
            logger.info(f"Retrieving prefixes with filters: {args}")
            
            # Get prefixes from Nautobot
            prefixes = await client.get_prefixes(
                prefix=prefix,
                status=status,
                site=site,
                role=role,
                tenant=tenant,
                vrf=vrf,
                limit=limit,
                offset=offset
            )
            
            # Format results
            result = {
                "count": len(prefixes),
                "filters_applied": {k: v for k, v in args.items() if v is not None},
                "results": [prefix_obj.model_dump() for prefix_obj in prefixes]
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Retrieved {len(prefixes)} network prefixes from Nautobot:\n\n"
                         f"```json\n{result}\n```"
                )
            ]
        
        elif name == "get_ip_address_by_id":
            ip_id = args.get("ip_id")
            if not ip_id:
                raise ValueError("ip_id is required")
            
            logger.info(f"Retrieving IP address by ID: {ip_id}")
            
            # Get specific IP address
            ip_address = await client.get_ip_address_by_id(ip_id)
            
            if ip_address is None:
                return [
                    types.TextContent(
                        type="text",
                        text=f"IP address with ID '{ip_id}' not found in Nautobot."
                    )
                ]
            
            result = ip_address.model_dump()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Retrieved IP address from Nautobot:\n\n"
                         f"```json\n{result}\n```"
                )
            ]
        
        elif name == "search_ip_addresses":
            query = args.get("query")
            if not query:
                raise ValueError("query is required")
            
            limit = min(args.get("limit", 50), 500)  # Cap at 500 for search
            
            logger.info(f"Searching IP addresses with query: {query}")
            
            # Search IP addresses
            ip_addresses = await client.search_ip_addresses(query, limit)
            
            # Format results
            result = {
                "query": query,
                "count": len(ip_addresses),
                "results": [ip.model_dump() for ip in ip_addresses]
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Found {len(ip_addresses)} IP addresses matching '{query}':\n\n"
                         f"```json\n{result}\n```"
                )
            ]
        
        elif name == "test_connection":
            logger.info("Testing Nautobot API connection")
            
            # Test connection
            is_connected = await client.test_connection()
            
            result = {
                "connected": is_connected,
                "nautobot_url": client.base_url,
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
            status_text = "✅ Connected" if is_connected else "❌ Connection Failed"
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Nautobot API Connection Test: {status_text}\n\n"
                         f"```json\n{result}\n```"
                )
            ]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except NautobotAuthenticationError as e:
        logger.error(f"Authentication error in tool '{name}': {e}")
        return [
            types.TextContent(
                type="text",
                text=f"❌ Authentication failed: {e}\n\n"
                     "Please check your Nautobot API token and permissions."
            )
        ]
    
    except NautobotConnectionError as e:
        logger.error(f"Connection error in tool '{name}': {e}")
        return [
            types.TextContent(
                type="text",
                text=f"❌ Connection error: {e}\n\n"
                     "Please check your Nautobot URL and network connectivity."
            )
        ]
    
    except NautobotAPIError as e:
        logger.error(f"API error in tool '{name}': {e}")
        return [
            types.TextContent(
                type="text",
                text=f"❌ API error: {e}\n\n"
                     "Please check your request parameters and try again."
            )
        ]
    
    except Exception as e:
        logger.error(f"Unexpected error in tool '{name}': {e}")
        return [
            types.TextContent(
                type="text",
                text=f"❌ Unexpected error: {e}\n\n"
                     "Please check the server logs for more details."
            )
        ]


async def main():
    """
    Main entry point for the MCP Nautobot server.
    
    This function sets up the server with stdio transport and runs
    the main event loop with proper error handling and cleanup.
    """
    logger.info("Starting MCP Nautobot Server")
    
    try:
        # Run the server using stdin/stdout streams
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-nautobot-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        # Cleanup
        if nautobot_client:
            await nautobot_client.close()
        logger.info("MCP Nautobot Server shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())