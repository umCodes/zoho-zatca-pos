from fastapi import Request, HTTPException
from app.core.config import PASSWORD


async def validate_password(request: Request, call_next):

    if request.method == "OPTIONS":
        return await call_next(request)
    

    if request.url.path in ["/docs", "/openapi.json", "/redoc", "/check_password", "/health"] or request.match(r"^/invoice/.*/pdf$", request.url.path):
        return await call_next(request)

    if request.headers.get("x-password") != PASSWORD:
        raise HTTPException(status_code=404, 
            detail={
                "message": "Invalid Password",
                "error_code": "INVALID_PASSWORD",
            })

    return await call_next(request)