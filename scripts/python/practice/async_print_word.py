import asyncio

# 协程基础：写一个 async def 协程，await asyncio.sleep(1) 后打印一句话，用 asyncio.run 运行
async def print_word(word):
    await asyncio.sleep(1)
    print(word)


async def main():
    await asyncio.gather(print_word("hello"), print_word("world"))


if __name__ == "__main__":
    asyncio.run(main())
