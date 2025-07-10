# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that integrates with Nautobot to provide IP address data retrieval capabilities. The server implements comprehensive error handling, rate limiting, and logging for reliable API interactions.

## Key Commands

### Development
- **Run server**: `uv run mcp-nautobot-server`
- **Install dependencies**: `uv sync`
- **Build package**: `uv build`
- **Run tests**: `pytest`
- **Run tests with async support**: `pytest -v --asyncio-mode=auto`
- **Type checking**: `mypy src/`
- **Format code**: `black src/ tests/`
- **Sort imports**: `isort src/ tests/`
- **Debug with MCP Inspector**: `npx @modelcontextprotocol/inspector uv --directory /Users/admin/Documents/projects/mcp-nautobot run mcp-nautobot-server`

### Environment Setup
Required environment variables:
- `NAUTOBOT_URL`: Base URL for Nautobot instance (e.g., http://localhost:8000)
- `NAUTOBOT_TOKEN`: API token for authentication

## Architecture

### Core Components

1. **MCP Server** (`src/mcp_nautobot_server/server.py`):
   - Implements MCP protocol handlers for tools, resources, and prompts
   - Manages server lifecycle and stdio communication
   - Provides 5 main tools: get_ip_addresses, get_prefixes, get_ip_address_by_id, search_ip_addresses, test_connection
   - Implements comprehensive error handling for authentication, connection, and API errors

2. **Nautobot Client** (`src/mcp_nautobot_server/nautobot_client.py`):
   - Async HTTP client using httpx for Nautobot API communication
   - Implements rate limiting to prevent API overload
   - Pydantic models for IPAddress and Prefix data validation
   - Custom exception hierarchy for error handling

### Key Design Patterns

- **Async/Await**: All I/O operations use async patterns for efficient concurrency
- **Rate Limiting**: Built-in rate limiter prevents overwhelming the Nautobot API
- **Error Handling**: Specific exception types for different failure modes (authentication, connection, API errors)
- **Type Safety**: Comprehensive type hints using Pydantic models for API responses
- **Configuration**: Environment-based configuration using pydantic-settings

### Testing Strategy

The project uses pytest with async support. Tests are organized into:
- Unit tests for individual components (client methods, server handlers)
- Integration tests with mocked Nautobot responses using pytest-httpx
- Error scenario testing for resilience

## MCP Integration

The server exposes Nautobot data through MCP's standard interfaces:
- **Tools**: Direct API operations for retrieving IP addresses and prefixes
- **Resources**: Read-only access to Nautobot data sources
- **Prompts**: Pre-configured templates for IP summary reports and network utilization analysis

For more information about MCP, see: https://modelcontextprotocol.io/