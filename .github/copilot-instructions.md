# Copilot Instructions for MCP Nautobot Server

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is an MCP (Model Context Protocol) server project that integrates with Nautobot to provide IP address data retrieval capabilities.

## Project Guidelines

- You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt
- Refer to the official MCP Python SDK: https://github.com/modelcontextprotocol/create-python-server
- Follow async/await patterns for all I/O operations
- Use proper error handling and logging throughout the codebase
- Implement comprehensive type hints using Pydantic models
- Follow the MCP specification for tool definitions and responses
- Use environment variables for configuration (API keys, URLs, etc.)
- Implement rate limiting for Nautobot API calls to avoid overwhelming the server
- Ensure all responses are JSON serializable
- Include comprehensive docstrings and inline comments
- Follow Python best practices: PEP 8, proper exception handling, etc.

## Key Components

1. **Nautobot API Client**: Handles authentication and API communication
2. **MCP Tools**: Define available functions for IP address data retrieval
3. **Error Handling**: Comprehensive error handling for API failures
4. **Logging**: Structured logging for debugging and monitoring
5. **Configuration**: Environment-based configuration management

## Testing Strategy

- Unit tests for individual components
- Integration tests with mock Nautobot responses
- Error scenario testing
- Type checking with mypy
