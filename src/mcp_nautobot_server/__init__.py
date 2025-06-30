"""
MCP Nautobot Server - A Model Context Protocol server for Nautobot integration.

This package provides an MCP server that connects to Nautobot and offers
tools for retrieving IP address and network data.
"""

import asyncio
import sys

from . import server

__version__ = "1.0.0"
__author__ = "Mike Lee"
__email__ = "michael@aiop.net"


def main():
    """Main entry point for the package."""
    try:
        asyncio.run(server.main())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


# Optionally expose other important items at package level
__all__ = ['main', 'server']