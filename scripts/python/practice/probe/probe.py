import asyncio

import aiohttp


# 探测TCP
async def prob_tcp(host: str, port: int, timeout: float = 3.0) -> dict:
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host=host, port=port), timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return {
            "host": host,
            "port": port,
            "alive": True
        }
    except Exception as e:
        return {
            "host": host,
            "port": port,
            "alive": False,
            "error": type(e).__name__
        }
