from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx
import os


RENDER_URL = os.getenv("RENDER_URL", "http://127.0.0.1:8080")

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