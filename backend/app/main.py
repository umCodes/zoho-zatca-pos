from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import health, invoices, telegram, items, pdf, check_password

from app.middlewares.token_refresh import token_refresh_middleware
from app.middlewares.validate_password import validate_password

from app.core.config import ENV, FRONTEND_DOMAIN


app = FastAPI()


if ENV == "prod":
    origins = [FRONTEND_DOMAIN]
else:
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(validate_password)
app.middleware("http")(token_refresh_middleware)


app.include_router(router=check_password.router)
app.include_router(router=health.router)
app.include_router(router=invoices.router)
app.include_router(router=telegram.router)
app.include_router(router=items.router)
app.include_router(router=pdf.router)