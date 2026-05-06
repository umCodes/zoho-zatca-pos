from fastapi import Request
from app.core.auth import refresh_token_if_needed

async def token_refresh_middleware(request: Request, call_next):
    await refresh_token_if_needed()
    return await call_next(request)