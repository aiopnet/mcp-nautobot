# MCP Nautobot Server

[![MCP](https://img.shields.io/badge/MCP-1.0-blue)](https://github.com/anthropics/mcp)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Nautobot](https://img.shields.io/badge/Nautobot-2.0+-orange)](https://nautobot.com/)

A Model Context Protocol (MCP) server that integrates with [Nautobot](https://nautobot.com/) to provide network automation and infrastructure data to AI assistants like Claude. This server enables AI agents to query and interact with your network Source of Truth, making network operations more intelligent and accessible.

## 🌟 Features

- **Comprehensive IP Address Management**: Query and search IP addresses with advanced filtering
- **Network Prefix Discovery**: Explore network prefixes with site and role-based filtering
- **Device Inventory** (Coming Soon): Access device information including warranty and lifecycle data
- **Asynchronous Operations**: Built on async/await for optimal performance
- **Rate Limiting**: Protects your Nautobot instance from overload
- **Enterprise-Ready**: Includes error handling, logging, and connection management
- **AI-Optimized**: Responses formatted for optimal AI agent consumption

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Access to a Nautobot instance (2.0+)
- Nautobot API token with appropriate permissions
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/mcp-nautobot.git
cd mcp-nautobot
```

2. **Install dependencies**:
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

3. **Configure environment**:
```bash
cp .env.example .env
```

Edit `.env` with your Nautobot credentials:
```env
NAUTOBOT_URL=https://your-nautobot-instance.com
NAUTOBOT_TOKEN=your-api-token-here
```

4. **Test the connection**:
```bash
python test_connection.py
```

### Claude Desktop Integration

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nautobot": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-nautobot",
        "run",
        "mcp-nautobot-server"
      ]
    }
  }
}
```

## 📖 Usage

Once configured, you can interact with Nautobot through Claude:

### Example Queries

- "Show me all IP addresses in the 10.0.0.0/8 network"
- "Find all active IP addresses at the Reno site"
- "Search for IP addresses with 'gateway' in the description"
- "List all network prefixes for the production VRF"
- "Check the connection status to Nautobot"

### Available Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_ip_addresses` | Retrieve IP addresses with filtering | `prefix`, `status`, `site`, `vrf`, `limit` |
| `get_prefixes` | Get network prefixes | `prefix`, `site`, `role`, `status` |
| `search_ip_addresses` | Search IPs by keyword | `query`, `limit` |
| `get_ip_address_by_id` | Get specific IP by ID | `ip_id` |
| `test_connection` | Verify Nautobot connectivity | None |

## 🛠️ Development

### Project Structure

```
mcp-nautobot/
├── src/
│   └── mcp_nautobot_server/
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py          # MCP server implementation
│       └── nautobot_client.py  # Nautobot API client
├── tests/                      # Test suite
├── .env.example               # Environment template
├── pyproject.toml             # Project configuration
├── README.md                  # This file
└── LICENSE                    # MIT license
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_nautobot_server

# Run specific test
pytest tests/test_nautobot_client.py -v
```

### Development Mode

```bash
# Run server with debug logging
LOG_LEVEL=DEBUG uv run mcp-nautobot-server

# Use MCP Inspector for debugging
npx @modelcontextprotocol/inspector uv --directory . run mcp-nautobot-server
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NAUTOBOT_URL` | Base URL of your Nautobot instance | Required |
| `NAUTOBOT_TOKEN` | API authentication token | Required |
| `NAUTOBOT_VERIFY_SSL` | Verify SSL certificates | `true` |
| `NAUTOBOT_TIMEOUT` | Request timeout in seconds | `30` |
| `NAUTOBOT_RATE_LIMIT` | Max requests per minute | `100` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Advanced Configuration

For custom field mappings, GraphQL queries, or enterprise features, see [CONFIGURATION.md](docs/CONFIGURATION.md).

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all public functions
- Run `black` for formatting
- Run `isort` for imports

## 📋 Roadmap

### Current Focus
- [x] Basic IP address and prefix queries
- [x] Search functionality
- [x] Rate limiting and error handling
- [ ] Response optimization for AI agents

### Upcoming Features
- [ ] Device inventory queries
- [ ] GraphQL support
- [ ] Bulk operations
- [ ] Custom field support
- [ ] Webhook integration
- [ ] Circuit management
- [ ] Configuration contexts

### Future Enhancements
- [ ] Multi-tenancy support
- [ ] Advanced caching strategies
- [ ] Prometheus metrics
- [ ] OpenTelemetry tracing
- [ ] Plugin architecture

## 🐛 Troubleshooting

### Common Issues

**Connection Failed**
- Verify Nautobot URL is accessible
- Check API token permissions
- Ensure network connectivity
- Review firewall rules

**Authentication Error**
- Confirm token is valid
- Check token hasn't expired
- Verify user permissions in Nautobot

**Rate Limiting**
- Adjust `NAUTOBOT_RATE_LIMIT`
- Implement caching for frequent queries
- Use pagination for large datasets

For more issues, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) or open an [issue](https://github.com/yourusername/mcp-nautobot/issues).

## 📚 Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [Nautobot Documentation](https://docs.nautobot.com)
- [Nautobot API Guide](https://docs.nautobot.com/projects/core/en/stable/user-guide/platform-functionality/rest-api/overview/)
- [Python Async Best Practices](https://docs.python.org/3/library/asyncio.html)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for the Model Context Protocol
- [Nautobot](https://nautobot.com) community for the excellent network Source of Truth platform
- All contributors who help improve this integration

---

**Note**: This is a community project and is not officially affiliated with or endorsed by Nautobot or Anthropic.