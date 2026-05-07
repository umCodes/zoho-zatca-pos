from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx
from app.core.config import RENDER_URL
import os



async def keep_alive():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.get(f"{RENDER_URL}/health")
            print("Keep-alive ping sent")
    except Exception as e:
        print("Keep-alive failed:", e)

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.add_job(keep_alive, "interval", minutes=5)  # adjust frequency
    scheduler.start()