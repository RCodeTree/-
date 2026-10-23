import asyncio
import aiohttp
import time

sem = asyncio.Semaphore(2)


async def gather_request(session, url):
    async with sem:
        start_time = time.perf_counter()
    try:
        async with session.get(url, timeout=5) as response:
            end_time = time.perf_counter()
            return url, response.status, end_time - start_time
    except Exception as e:  # 每一个协程都可能发生的异常，所以每个协程都 try except，从而达到故障隔离
        return url, None, f"{type(e).__name__}"


async def main():
    urls = ["https://httpbin.org/get"] * 5
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[gather_request(session, url) for url in urls])
    for url, status, response_time in results:
        print(f"URL: {url}, 状态: {status}, 响应时间: {response_time}")


if __name__ == "__main__":
    asyncio.run(main())
