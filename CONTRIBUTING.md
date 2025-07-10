# Contributing to MCP Nautobot Server

First off, thank you for considering contributing to MCP Nautobot Server! It's people like you that make this tool better for everyone.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment details (OS, Python version, Nautobot version)
- Any relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- A detailed description of the proposed enhancement
- Use cases and examples
- Any potential drawbacks or considerations

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Follow the setup instructions** in the README
3. **Make your changes**:
   - Add tests for new functionality
   - Update documentation as needed
   - Follow the existing code style
4. **Test your changes**:
   ```bash
   # Run tests
   pytest
   
   # Check code style
   black src/ tests/
   isort src/ tests/
   mypy src/
   ```
5. **Commit your changes** using clear, descriptive messages
6. **Push to your fork** and submit a pull request

## Development Process

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/yourusername/mcp-nautobot.git
cd mcp-nautobot

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Style Guidelines

- Follow [PEP 8](https://pep8.org/)
- Use type hints for all function parameters and returns
- Write descriptive docstrings for all public functions and classes
- Keep line length to 88 characters (Black's default)
- Use meaningful variable and function names

### Testing Guidelines

- Write tests for all new functionality
- Maintain or improve code coverage
- Use pytest fixtures for common test data
- Mock external API calls to Nautobot
- Test both success and error cases

Example test structure:
```python
import pytest
from mcp_nautobot_server.nautobot_client import NautobotClient

@pytest.mark.asyncio
async def test_get_ip_addresses_success(mock_nautobot_response):
    """Test successful IP address retrieval."""
    client = NautobotClient(config)
    result = await client.get_ip_addresses(prefix="10.0.0.0/8")
    assert len(result) > 0
    assert all(ip.address.startswith("10.") for ip in result)
```

### Documentation

- Update the README for new features
- Add docstrings to all new functions and classes
- Include usage examples for new tools
- Update the roadmap if implementing planned features

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add device inventory tool with warranty tracking
fix: handle pagination correctly for large IP address queries
docs: add troubleshooting guide for connection issues
```

## Project Structure

```
mcp-nautobot/
├── src/mcp_nautobot_server/
│   ├── server.py          # Main MCP server implementation
│   ├── nautobot_client.py # Nautobot API client
│   └── models.py          # Pydantic models (if separated)
├── tests/
│   ├── test_server.py     # Server tests
│   ├── test_client.py     # Client tests
│   └── conftest.py        # Pytest fixtures
├── docs/                  # Additional documentation
└── examples/              # Usage examples
```

## Areas for Contribution

### High Priority
- [ ] Implement device inventory tools
- [ ] Add GraphQL support
- [ ] Improve response formatting for AI agents
- [ ] Add caching layer for performance

### Good First Issues
- [ ] Add more comprehensive error messages
- [ ] Improve test coverage
- [ ] Add usage examples
- [ ] Enhance documentation

### Feature Ideas
- [ ] Webhook support for real-time updates
- [ ] Bulk operations for efficiency
- [ ] Custom field mapping
- [ ] Multi-tenancy support

## Review Process

1. All submissions require review before merging
2. Reviewers will check for:
   - Code quality and style
   - Test coverage
   - Documentation updates
   - Backward compatibility
3. Address review feedback promptly
4. Once approved, a maintainer will merge your PR

## Release Process

We use semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

Releases are automated via GitHub Actions when tags are pushed.

## Questions?

- Check the [README](README.md) and existing issues first
- For general questions, open a [Discussion](https://github.com/yourusername/mcp-nautobot/discussions)
- For bugs or features, open an [Issue](https://github.com/yourusername/mcp-nautobot/issues)

## Recognition

Contributors will be recognized in:
- The project README
- Release notes
- The contributors graph

Thank you for helping make MCP Nautobot Server better! 🎉