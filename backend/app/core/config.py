import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
PASSWORD = os.getenv("PASSWORD")
ENV = os.getenv("ENV", "dev")
FRONTEND_DOMAIN = os.getenv("FRONTEND_DOMAIN")

def get_settings():
    return {
        "access_token": os.getenv("ACCESS_TOKEN"),
        "refresh_token": os.getenv("REFRESH_TOKEN"),
        "organization_id": os.getenv("ORGANIZATION_ID"),
    }