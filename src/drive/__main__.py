"""Entry point for `python -m drive.server`."""

from drive.server import mcp

mcp.run(transport="stdio")
