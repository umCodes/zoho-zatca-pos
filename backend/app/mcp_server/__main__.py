"""Run the purchases MCP server over stdio, for local MCP clients:

    cd backend && python -m app.mcp_server

Uses the same .env as the API (Zoho, Postgres, Mistral, OpenRouter).
"""

from app.mcp_server.server import mcp

if __name__ == "__main__":
    mcp.run("stdio")
