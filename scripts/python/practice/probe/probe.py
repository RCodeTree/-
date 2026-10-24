import asyncio


# 探测单个主机的TCP
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


# 探测所有主机的TCP
async def prob_all(host: str, port: int, timeout: float, sem: asyncio.Semaphore):
    async with sem:
        return await prob_tcp(host, port, timeout)
