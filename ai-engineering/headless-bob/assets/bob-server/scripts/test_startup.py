"""Quick smoke-test: runs the lifespan context to verify skill startup logs."""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bobserver.main import lifespan, app  # noqa: E402


async def main() -> None:
    async with lifespan(app):
        print("[test] lifespan OK — skills loaded above")


asyncio.run(main())
