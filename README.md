# MCP-Nautobot

[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](https://github.com/modelcontextprotocol/create-python-server)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Model Context Protocol (MCP) server for Nautobot network automation platform. This project allows AI assistants to interact with your Nautobot instance, providing access to network inventory data.

> **Disclaimer:** This project is not officially affiliated with Anthropic, Claude, or Nautobot. It is an independent implementation of the Model Context Protocol for Nautobot integration.

## Features

- **Asynchronous API**: Built with modern async Python
- **MCP Compatible**: Works with Claude and other MCP-compatible AI assistants
- **Nautobot Integration**: Query your network inventory data directly
- **Site Information**: Retrieve detailed site location data
- **Device Details**: Access device specifications and configurations
- **Network Topology**: Visualize network connections and relationships
- **Role-based Access**: Control data access by user role
- **Flexible Configuration**: Customizable data presentation

## Requirements

- Python 3.10+
- Nautobot instance with API access
- Nautobot API token with appropriate permissions

## Installation

```bash
# Clone the repository
git clone https://github.com/aiopnet/mcp-nautobot.git
cd mcp-nautobot

# Create and activate a virtual environment
# If uv is not installed, follow instructions at: https://github.com/astral-sh/uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .  # Requires pip 21.3+ for editable installs with pyproject.toml
```

## Configuration

Copy the example environment file and update it with your settings:

```bash
cp .env.example .env
# Edit .env with your favorite editor
```

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `NAUTOBOT_URL` | Yes | URL of your Nautobot instance | None |
| `NAUTOBOT_TOKEN` | Yes | API token with read permissions | None |
| `MCP_PORT` | No | Port for the MCP server to listen on | 8000 |
| `MCP_HOST` | No | Host for the MCP server to bind to | 127.0.0.1 |
| `LOG_LEVEL` | No | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

> ⚠️ **Security Note**: Never commit your `.env` file to version control. It contains sensitive API tokens.

For advanced configuration options, see [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Usage

### Running the Server

```bash
# Start the MCP server
python -m mcp_nautobot.server

# Or using the provided CLI
mcp-nautobot-server
```

The server will start on http://127.0.0.1:8000 by default.

### Integrating with Claude Desktop

1. Open Claude Desktop and navigate to Settings > Tools > Configure Custom Tools
2. Add a new tool with the following details:
   - **Name**: Nautobot Network Data
   - **Description**: Access network inventory data from Nautobot
   - **Schema Type**: MCP
   - **Endpoint URL**: http://127.0.0.1:8000 (or your custom host/port)
3. Save and test the connection

Now you can ask Claude questions about your network inventory:

- "What sites do we have in the US West region?"
- "Show me all devices in the Chicago datacenter"
- "List all Cisco switches in our network"
- "What's the IP address of the core router in Atlanta?"

## Developer Guide

### Testing

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=mcp_nautobot
```

### Code Style and Linting

This project follows PEP 8 guidelines and uses Black and isort for formatting.

```bash
# Format code
black mcp_nautobot tests
isort mcp_nautobot tests

# Lint code
flake8 mcp_nautobot tests
mypy mcp_nautobot
```

## Roadmap

- **Device Configuration Retrieval**: Access running device configurations
- **Topology Visualization**: Generate network maps and diagrams
- **Multi-tenant Support**: Enhanced role-based access control
- **Circuit Information**: Data about WAN circuits and providers
- **Performance Data**: Historical performance metrics integration

## Contributing

Contributions are welcome! Please check out our [Contributing Guide](CONTRIBUTING.md) to get started.

If you encounter any issues or have feature requests, please [open an issue](https://github.com/aiopnet/mcp-nautobot/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project implements the [Model Context Protocol](https://github.com/modelcontextprotocol/create-python-server)
- Built for integration with [Nautobot](https://github.com/nautobot/nautobot)
- Not officially affiliated with Anthropic or Claude
```

## Troubleshooting

If you encounter issues, check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md) or open an issue on GitHub.
