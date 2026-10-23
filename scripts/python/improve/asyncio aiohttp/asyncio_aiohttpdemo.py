import asyncio
import aiohttp


# async def hello(name):        # async def = 协程
#     await asyncio.sleep(1)    # await = 挂起，让出控制权
#     return f"hello {name}"
#
# async def main():
#     results = await asyncio.gather(hello("a"), hello("b"), hello("c"))
#     print(results)
#
# asyncio.run(main())           # 入口：创建事件循环并运行


# aiohttp 三件套
# async with aiohttp.ClientSession() as session:     # 复用连接
#     async with session.get(url, timeout=...) as resp:
#         await resp.json()                           # 异步取 JSON

# 限流：Semaphore (并发限制)
# sem = asyncio.Semaphore(3)   # 最多同时 3 个
# async with sem:              # 超过就排队等待
#     ...


# 异步函数里禁用同步阻塞代码：time.sleep → await asyncio.sleep；requests → aiohttp（同步调用会阻塞整个事件循环，异步直接废掉）；
# 事件循环里别混用：协程要在 asyncio.run 里跑；
# ClientSession 用 async with，用完自动关闭连接。


# 实例
async def probe(session, host):
    try:
        async with session.get(f"http://{host}", timeout=aiohttp.ClientTimeout(total=3)) as resp:
            return host, resp.status
    except Exception:
        return host, "DOWN"


async def main():
    hosts = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5"]
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(probe(session, h) for h in hosts))
    for h, s in results:
        print(f"{h}: {s}")


if __name__ == "__main__":
    asyncio.run(main())
