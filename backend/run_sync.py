import logging
import asyncio

# Enable ALL logging so you see progress
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
# Suppress noisy HTTP logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

from app.workers.tmdb_sync import _run_sync

print("Starting sync... This will take 15-25 minutes.")
print("You'll see progress updates below.\n")

asyncio.run(_run_sync())
print("\nDone!")
