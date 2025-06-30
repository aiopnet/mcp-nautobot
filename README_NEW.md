# MCP Nautobot Server

A Model Context Protocol (MCP) server that integrates with Nautobot to provide IP address and network data retrieval capabilities.

## 🌟 Features

- **IP Address Management**: Query, search, and retrieve IP address data from Nautobot
- **Network Prefix Operations**: Access network prefix information with filtering
- **Comprehensive Error Handling**: Robust error handling for API failures and network issues
- **Rate Limiting**: Built-in rate limiting to prevent API overload
- **Async Support**: Full asynchronous operation for optimal performance
- **Type Safety**: Comprehensive type hints and Pydantic models
- **Testing**: Complete test suite with mocking capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- Access to a Nautobot instance
- Nautobot API token with appropriate permissions

### Installation

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd mcp-nautobot
   ```

2. **Install dependencies:**
   ```bash
   uv sync --dev
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Nautobot settings
   ```

4. **Set up your environment variables:**
   ```bash
   export NAUTOBOT_URL="https://your-nautobot-instance.com"
   export NAUTOBOT_TOKEN="your-api-token"
   ```

### Running the Server

```bash
# Activate the virtual environment (if not using uv run)
source .venv/bin/activate

# Run the MCP server
python -m mcp_nautobot_server
```

Or using uv:
```bash
uv run python -m mcp_nautobot_server
```

## 🔧 Configuration

The server uses environment variables for configuration:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NAUTOBOT_URL` | Base URL of your Nautobot instance | `http://localhost:8000` | Yes |
| `NAUTOBOT_TOKEN` | API token for authentication | - | Yes |
| `NAUTOBOT_VERIFY_SSL` | Whether to verify SSL certificates | `true` | No |
| `NAUTOBOT_TIMEOUT` | Request timeout in seconds | `30` | No |
| `NAUTOBOT_RATE_LIMIT` | Max requests per minute | `100` | No |

## 📡 MCP Integration

### Available Tools

#### `get_ip_addresses`
Retrieve IP addresses with optional filtering.

**Parameters:**
- `address` (string, optional): Specific IP address to search for
- `prefix` (string, optional): Network prefix to filter by (e.g., "10.0.0.0/24")
- `status` (string, optional): Status filter (e.g., "active", "reserved")
- `role` (string, optional): Role filter (e.g., "loopback", "secondary")
- `tenant` (string, optional): Tenant filter
- `vrf` (string, optional): VRF filter
- `limit` (integer, optional): Maximum results (default: 100, max: 1000)
- `offset` (integer, optional): Pagination offset (default: 0)

**Example:**
```json
{
  "name": "get_ip_addresses",
  "arguments": {
    "prefix": "192.168.1.0/24",
    "status": "active",
    "limit": 50
  }
}
```

#### `get_prefixes`
Retrieve network prefixes with optional filtering.

**Parameters:**
- `prefix` (string, optional): Specific network prefix to search for
- `status` (string, optional): Status filter
- `site` (string, optional): Site filter
- `role` (string, optional): Role filter
- `tenant` (string, optional): Tenant filter
- `vrf` (string, optional): VRF filter
- `limit` (integer, optional): Maximum results (default: 100, max: 1000)
- `offset` (integer, optional): Pagination offset (default: 0)

#### `get_ip_address_by_id`
Retrieve a specific IP address by its Nautobot ID.

**Parameters:**
- `ip_id` (string, required): The Nautobot ID of the IP address

#### `search_ip_addresses`
Search IP addresses using a general query string.

**Parameters:**
- `query` (string, required): Search query (matches IP, description, etc.)
- `limit` (integer, optional): Maximum results (default: 50, max: 500)

#### `test_connection`
Test the connection to the Nautobot API.

**Parameters:** None

### Available Resources

- `nautobot://ip-addresses`: Sample IP address data
- `nautobot://prefixes`: Sample network prefix data  
- `nautobot://status`: Connection status information

### Available Prompts

#### `ip-summary-report`
Generate a comprehensive IP address summary report.

**Arguments:**
- `network` (optional): Network prefix to analyze
- `status` (optional): Filter by IP status
- `include_details` (optional): Include detailed information

#### `network-utilization`
Analyze network prefix utilization and capacity.

**Arguments:**
- `prefix` (required): Network prefix to analyze
- `depth` (optional): Analysis depth (summary/detailed)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=mcp_nautobot_server

# Run specific test file
uv run pytest tests/test_nautobot_client.py

# Run with verbose output
uv run pytest -v
```

### Test Categories

- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test API interactions with mocked responses
- **Error Handling Tests**: Test various error scenarios
- **Type Checking**: Verify type safety with mypy

## 🏗️ Development

### Code Quality

The project includes several code quality tools:

```bash
# Format code
uv run black src/ tests/

# Sort imports
uv run isort src/ tests/

# Type checking
uv run mypy src/
```

### Project Structure

```
mcp-nautobot/
├── src/
│   └── mcp_nautobot_server/
│       ├── __init__.py
│       ├── server.py          # Main MCP server implementation
│       └── nautobot_client.py  # Nautobot API client
├── tests/
│   ├── conftest.py            # Test fixtures and configuration
│   ├── test_nautobot_client.py # Client tests
│   └── test_server.py         # Server tests
├── .github/
│   └── copilot-instructions.md # Copilot coding guidelines
├── pyproject.toml             # Project configuration
├── README.md                  # This file
└── .env.example              # Environment variables template
```

## 🔌 MCP Client Integration

### Using with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "nautobot": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_nautobot_server"],
      "cwd": "/path/to/mcp-nautobot",
      "env": {
        "NAUTOBOT_URL": "https://your-nautobot-instance.com",
        "NAUTOBOT_TOKEN": "your-api-token"
      }
    }
  }
}
```

### Using with Python MCP Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_nautobot_server"],
        env={
            "NAUTOBOT_URL": "https://your-nautobot-instance.com",
            "NAUTOBOT_TOKEN": "your-api-token"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
            
            # Call a tool
            result = await session.call_tool(
                "get_ip_addresses", 
                {"prefix": "10.0.0.0/8", "limit": 10}
            )
            print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🚨 Troubleshooting

### Common Issues

**1. Authentication Errors**
- Verify your `NAUTOBOT_TOKEN` is correct and has appropriate permissions
- Check that the token hasn't expired
- Ensure the token has read access to IPAM objects

**2. Connection Errors**  
- Verify `NAUTOBOT_URL` is correct and accessible
- Check SSL certificate settings if using HTTPS
- Ensure Nautobot API is accessible from your network

**3. Rate Limiting**
- Reduce `NAUTOBOT_RATE_LIMIT` if getting rate limit errors
- Implement request batching for large datasets
- Consider using pagination for large result sets

**4. SSL Certificate Issues**
- Set `NAUTOBOT_VERIFY_SSL=false` for development environments
- For production, ensure proper SSL certificate configuration

### Debug Mode

Enable debug logging:

```bash
export PYTHONPATH=src
export LOG_LEVEL=DEBUG
python -m mcp_nautobot_server
```

## 📚 API Documentation

For detailed information about Nautobot's REST API, refer to:
- [Nautobot REST API Documentation](https://nautobot.readthedocs.io/en/latest/user-guide/platform-functionality/rest-api/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the specification
- [Nautobot](https://nautobot.com/) for the network automation platform
- [Pydantic](https://pydantic.dev/) for data validation
- [httpx](https://www.python-httpx.org/) for async HTTP client
