import aiohttp


# 探测TCP
async def prob_tcp(session, host, port):
    result = {
        "host": host,
        "port": port,
        "alive": True
    }
    try:
        async with session.get(f"{host}:{port}", timeout=aiohttp.ClientTimeout(total=3)):
            return result
    except Exception:
        result["alive"] = False
        return result
