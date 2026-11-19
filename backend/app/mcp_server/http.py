"""Serves the purchases MCP server over Streamable HTTP at /mcp inside the
FastAPI app, gated by a bearer token (MCP_API_KEY)."""

import hmac
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import MCP_API_KEY
from app.mcp_server.server import mcp

MCP_PATH = "/mcp"


class BearerTokenGate:
    """Rejects requests without `Authorization: Bearer <MCP_API_KEY>`. If no
    key is configured the endpoint is disabled rather than left open."""

    def __init__(self, app: ASGIApp, token: str | None):
        self.app = app
        self.token = token

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        if not self.token:
            return await self._reject(send, 503, "MCP endpoint is disabled: MCP_API_KEY is not set")

        headers = dict(scope.get("headers") or [])
        provided = headers.get(b"authorization", b"").decode("latin-1")
        scheme, _, token = provided.partition(" ")
        if scheme.lower() != "bearer" or not hmac.compare_digest(token.strip().encode(), self.token.encode()):
            return await self._reject(send, 401, "Invalid or missing bearer token")

        return await self.app(scope, receive, send)

    @staticmethod
    async def _reject(send: Send, status: int, message: str) -> None:
        body = json.dumps({"error": message}).encode()
        response_headers = [(b"content-type", b"application/json")]
        if status == 401:
            response_headers.append((b"www-authenticate", b"Bearer"))
        await send({"type": "http.response.start", "status": status, "headers": response_headers})
        await send({"type": "http.response.body", "body": body})


def mount_mcp(app: FastAPI) -> None:
    """Adds the /mcp route to `app` and runs the MCP session manager inside
    the app's lifespan (mounted sub-app lifespans are not run by Starlette)."""
    # Stateless + JSON responses: every request stands alone, so it survives
    # Render restarts/sleeps and needs no sticky sessions. host="0.0.0.0"
    # turns off the localhost-only Host check; access is gated by the token.
    mcp_app = mcp.streamable_http_app(
        streamable_http_path=MCP_PATH,
        stateless_http=True,
        json_response=True,
        host="0.0.0.0",
    )
    for route in mcp_app.routes:
        route.app = BearerTokenGate(route.app, MCP_API_KEY)
        app.router.routes.append(route)

    previous_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(app_: FastAPI):
        async with mcp.session_manager.run():
            async with previous_lifespan(app_) as state:
                yield state

    app.router.lifespan_context = lifespan
