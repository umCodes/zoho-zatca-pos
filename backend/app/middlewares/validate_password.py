from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import PASSWORD
import re

async def validate_password(request: Request, call_next):

    if request.method == "OPTIONS":
        return await call_next(request)
    
    print(f"Validating password for path: {request.url.path}")
    if request.url.path in ["/push-invoices", "/docs", "/openapi.json", "/redoc", "/check_password", "/health", "/upload", "/read_qr", "/expenses", "/vendors", "/webhook/telegram"] or re.match(r"^/invoice/.*/pdf$", request.url.path):
        return await call_next(request)

    if request.headers.get("x-password") != PASSWORD:
        return JSONResponse(status_code=404, 
            content={
                "message": "Invalid Password Header",
                "error_code": "INVALID_PASSWORD",
            })

    return await call_next(request)