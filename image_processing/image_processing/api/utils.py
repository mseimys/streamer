import asyncio
from typing import BinaryIO
from pathlib import Path

import aiofiles


async def async_save_file(src: BinaryIO, dst_path: Path, chunk_size: int = 8192):
    async with aiofiles.open(dst_path, "wb") as dst:
        loop = asyncio.get_running_loop()
        while True:
            chunk = await loop.run_in_executor(None, src.read, chunk_size)
            if not chunk:
                break
            await dst.write(chunk)


async def file_reader(file_path: str, chunk_size: int = 8192):
    """Asynchronous generator that reads a file in chunks."""
    async with aiofiles.open(file_path, mode="rb") as file:
        while chunk := await file.read(chunk_size):
            yield chunk
            await asyncio.sleep(0)  # Yield control to event loop
