"""
Example optimized implementation for Nautobot MCP server.
Demonstrates key optimizations for AI agent use cases.
"""

import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import mcp.types as types
from mcp.server import Server

# Example of optimized tool definition
OPTIMIZED_TOOLS = [
    types.Tool(
        name="get_devices",
        description="Retrieve network devices optimized for AI agents - supports site filtering, depth control, and warranty info",
        inputSchema={
            "type": "object",
            "properties": {
                "site": {
                    "type": "string",
                    "description": "Site name or slug (e.g., 'reno', 'ber-berlin', 'mnl-manila')"
                },
                "sites": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Multiple sites to query"
                },
                "device_type": {
                    "type": "string",
                    "description": "Device type slug (e.g., 'router', 'switch', 'firewall', 'wireless-ap')"
                },
                "manufacturer": {
                    "type": "string",
                    "description": "Manufacturer name (e.g., 'Cisco', 'Juniper', 'Palo Alto Networks')"
                },
                "model": {
                    "type": "string",
                    "description": "Device model (supports wildcards with *)"
                },
                "status": {
                    "type": "string",
                    "description": "Device status (active, planned, offline, decommissioned)"
                },
                "role": {
                    "type": "string",
                    "description": "Device role (e.g., 'edge-router', 'core-switch', 'access-switch')"
                },
                "include_warranty": {
                    "type": "boolean",
                    "description": "Include warranty and EOL/EOS data from custom fields",
                    "default": false
                },
                "depth": {
                    "type": "integer",
                    "description": "Response detail level: 0=minimal (name,status), 1=standard, 2=full details",
                    "default": 0,
                    "minimum": 0,
                    "maximum": 2
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to include (e.g., ['name', 'serial_number', 'primary_ip'])"
                },
                "query": {
                    "type": "string",
                    "description": "General search query across device fields"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results (optimized default for AI agents)",
                    "default": 25,
                    "minimum": 1,
                    "maximum": 100
                },
                "offset": {
                    "type": "integer",
                    "description": "Pagination offset",
                    "default": 0
                }
            },
            "additionalProperties": False
        }
    ),
    types.Tool(
        name="get_device_lifecycle_info",
        description="Get warranty, EOL, and EOS information for devices - ideal for refresh planning",
        inputSchema={
            "type": "object",
            "properties": {
                "months_until_eol": {
                    "type": "integer",
                    "description": "Find devices with EOL date within X months",
                    "minimum": 0,
                    "maximum": 60
                },
                "warranty_status": {
                    "type": "string",
                    "enum": ["active", "expired", "expiring_soon"],
                    "description": "Filter by warranty status"
                },
                "include_recommendations": {
                    "type": "boolean",
                    "description": "Include replacement recommendations",
                    "default": true
                },
                "site": {
                    "type": "string",
                    "description": "Filter by site"
                },
                "group_by": {
                    "type": "string",
                    "enum": ["model", "site", "manufacturer"],
                    "description": "Group results for summary view"
                }
            }
        }
    ),
    types.Tool(
        name="execute_nautobot_query",
        description="Execute advanced queries using Nautobot's filtering syntax - for power users",
        inputSchema={
            "type": "object",
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "API endpoint (e.g., 'dcim/devices', 'ipam/ip-addresses')"
                },
                "filters": {
                    "type": "object",
                    "description": "Filter parameters using Nautobot syntax",
                    "additionalProperties": True
                },
                "depth": {
                    "type": "integer",
                    "default": 0
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "summary", "table"],
                    "description": "Output format for AI consumption",
                    "default": "summary"
                }
            },
            "required": ["endpoint"]
        }
    )
]


class DeviceSummary(BaseModel):
    """Optimized device model for AI agents."""
    id: str
    name: str
    status: str
    site: Optional[str] = None
    device_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    primary_ip: Optional[str] = None
    # Warranty fields
    warranty_end: Optional[str] = None
    eol_date: Optional[str] = None
    eos_date: Optional[str] = None
    lifecycle_status: Optional[str] = None
    
    def to_ai_summary(self) -> str:
        """Format device info for AI consumption."""
        parts = [f"{self.name} ({self.status})"]
        
        if self.model:
            parts.append(f"Model: {self.manufacturer} {self.model}")
        if self.site:
            parts.append(f"Site: {self.site}")
        if self.primary_ip:
            parts.append(f"IP: {self.primary_ip}")
        if self.warranty_end:
            parts.append(f"Warranty: {self.warranty_end}")
        if self.eol_date:
            parts.append(f"EOL: {self.eol_date}")
            
        return " | ".join(parts)


class OptimizedResponse(BaseModel):
    """Standardized response format for AI agents."""
    success: bool = True
    count: int
    total_count: Optional[int] = None
    data: List[Dict[str, Any]]
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    
    def to_ai_text(self) -> str:
        """Convert to AI-friendly text format."""
        if self.error:
            return f"Error: {self.error}"
        
        lines = []
        
        if self.summary:
            lines.append(self.summary)
        else:
            lines.append(f"Found {self.count} results")
            
        if self.total_count and self.total_count > self.count:
            lines.append(f"(Showing {self.count} of {self.total_count} total)")
        
        # Add metadata if relevant
        if self.metadata.get("filters"):
            lines.append(f"Filters applied: {json.dumps(self.metadata['filters'])}")
            
        lines.append("")  # Empty line
        
        # Format data based on content
        if self.data and len(self.data) > 0:
            # Check if it's device data
            if "device_type" in self.data[0] or "model" in self.data[0]:
                lines.append("Devices:")
                for item in self.data:
                    device = DeviceSummary(**item)
                    lines.append(f"- {device.to_ai_summary()}")
            else:
                # Generic formatting
                lines.append("Results:")
                for item in self.data:
                    lines.append(f"- {json.dumps(item, indent=2)}")
        
        return "\n".join(lines)


# Example implementation of optimized device retrieval
async def get_devices_optimized(
    client,
    site: Optional[str] = None,
    sites: Optional[List[str]] = None,
    device_type: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    status: Optional[str] = None,
    role: Optional[str] = None,
    include_warranty: bool = False,
    depth: int = 0,
    fields: Optional[List[str]] = None,
    query: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
    **kwargs
) -> OptimizedResponse:
    """
    Optimized device retrieval for AI agents.
    
    Key optimizations:
    - Depth control for response size
    - Field selection
    - Smart defaults (limit=25)
    - AI-friendly response format
    """
    try:
        # Build query parameters
        params = {
            "limit": limit,
            "offset": offset,
            "depth": depth
        }
        
        # Add filters
        if site:
            params["site"] = site
        elif sites:
            params["site"] = ",".join(sites)  # Multiple sites
            
        if device_type:
            params["device_type"] = device_type
        if manufacturer:
            params["manufacturer__name"] = manufacturer
        if model:
            if "*" in model:
                params["model__ic"] = model.replace("*", "")  # Case-insensitive contains
            else:
                params["model"] = model
        if status:
            params["status"] = status
        if role:
            params["role"] = role
        if query:
            params["q"] = query
            
        # Field selection for performance
        if fields:
            params["include"] = ",".join(fields)
        elif depth == 0:
            # Minimal fields for depth=0
            params["include"] = "id,name,status,site,device_type,model,manufacturer,primary_ip"
            
        # Make request
        response = await client._make_request("GET", "/dcim/devices/", params)
        
        # Process results
        devices = []
        for device_data in response.get("results", []):
            # Transform nested objects based on depth
            if depth == 0:
                # Flatten for minimal response
                processed = {
                    "id": device_data.get("id"),
                    "name": device_data.get("name"),
                    "status": device_data.get("status", {}).get("value", "unknown"),
                    "site": device_data.get("site", {}).get("name"),
                    "device_type": device_data.get("device_type", {}).get("model"),
                    "manufacturer": device_data.get("device_type", {}).get("manufacturer", {}).get("name"),
                    "model": device_data.get("device_type", {}).get("model"),
                    "primary_ip": device_data.get("primary_ip", {}).get("address", "").split("/")[0] if device_data.get("primary_ip") else None
                }
            else:
                processed = device_data
                
            # Add warranty info if requested
            if include_warranty and device_data.get("custom_fields"):
                cf = device_data["custom_fields"]
                processed.update({
                    "warranty_end": cf.get("warranty_end_date"),
                    "eol_date": cf.get("end_of_life_date"),
                    "eos_date": cf.get("end_of_support_date"),
                    "lifecycle_status": cf.get("lifecycle_status", "active")
                })
                
            devices.append(processed)
        
        # Create summary for AI
        summary_parts = []
        if site:
            summary_parts.append(f"site {site}")
        if device_type:
            summary_parts.append(f"type {device_type}")
        if manufacturer:
            summary_parts.append(f"manufacturer {manufacturer}")
            
        summary = f"Found {len(devices)} devices"
        if summary_parts:
            summary += f" matching {', '.join(summary_parts)}"
            
        return OptimizedResponse(
            count=len(devices),
            total_count=response.get("count"),
            data=devices,
            summary=summary,
            metadata={
                "filters": {k: v for k, v in params.items() if k not in ["limit", "offset", "depth", "include"]},
                "page": (offset // limit) + 1,
                "has_more": response.get("next") is not None
            }
        )
        
    except Exception as e:
        return OptimizedResponse(
            success=False,
            count=0,
            data=[],
            error=str(e)
        )


# Example tool handler with optimized response
async def handle_get_devices(args: Dict[str, Any], client) -> List[types.TextContent]:
    """Handle get_devices tool with optimizations."""
    response = await get_devices_optimized(client, **args)
    
    # Return AI-optimized format
    return [
        types.TextContent(
            type="text",
            text=response.to_ai_text()
        )
    ]


# Example of lifecycle query for warranty/EOL
async def get_device_lifecycle_info(
    client,
    months_until_eol: Optional[int] = None,
    warranty_status: Optional[str] = None,
    site: Optional[str] = None,
    include_recommendations: bool = True,
    group_by: Optional[str] = None
) -> OptimizedResponse:
    """Get device lifecycle information for refresh planning."""
    from datetime import datetime, timedelta
    
    # Calculate EOL threshold date
    threshold_date = None
    if months_until_eol:
        threshold_date = (datetime.now() + timedelta(days=months_until_eol * 30)).isoformat()
    
    # Build query
    params = {
        "limit": 200,  # Higher limit for lifecycle queries
        "depth": 1,
        "include": "id,name,site,device_type,custom_fields,status"
    }
    
    if site:
        params["site"] = site
        
    # Add custom field filters if Nautobot supports them
    if threshold_date:
        params["custom_fields__end_of_life_date__lte"] = threshold_date
        
    response = await client._make_request("GET", "/dcim/devices/", params)
    
    # Process and group results
    devices_by_status = {
        "eol_soon": [],
        "warranty_expired": [],
        "warranty_expiring": [],
        "needs_refresh": []
    }
    
    for device in response.get("results", []):
        cf = device.get("custom_fields", {})
        
        # Categorize devices
        if cf.get("end_of_life_date"):
            eol_date = datetime.fromisoformat(cf["end_of_life_date"].replace("Z", ""))
            months_to_eol = (eol_date - datetime.now()).days / 30
            
            if months_to_eol <= (months_until_eol or 12):
                devices_by_status["eol_soon"].append({
                    "name": device["name"],
                    "model": device.get("device_type", {}).get("model"),
                    "site": device.get("site", {}).get("name"),
                    "eol_date": cf["end_of_life_date"],
                    "months_remaining": round(months_to_eol, 1)
                })
                
    # Create summary
    summary_lines = []
    if devices_by_status["eol_soon"]:
        summary_lines.append(f"{len(devices_by_status['eol_soon'])} devices approaching EOL")
        
    if include_recommendations:
        summary_lines.append("\nRecommendations:")
        summary_lines.append("- Plan refresh for devices with <6 months to EOL")
        summary_lines.append("- Budget for replacements in next fiscal cycle")
        
    return OptimizedResponse(
        count=sum(len(v) for v in devices_by_status.values()),
        data=devices_by_status,
        summary="\n".join(summary_lines),
        metadata={"grouped_by": group_by or "status"}
    )