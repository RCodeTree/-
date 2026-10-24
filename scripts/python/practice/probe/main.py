import asyncio, logging, argparse, aiohttp
import probe


async def main():
    # 配置解析CLI参数
    p = argparse.ArgumentParser(description="多主机批量探活 + 并发上报")
    p.add_argument("--seq", default=",", help="分隔符")
    p.add_argument("--hosts", help="多个主机IP(直接传入)")
    p.add_argument("--hosts-file", type=str,
                   help="多个主机IP(文件形式)")  # argparse.FileType("r") 会在参数解析阶段立即打开文件，文件不存在就直接报错退出，这通常没问题。但如果你的脚本可能长时间运行、或者要重复使用文件名，建议改成 type=str，用的时候再打开
    p.add_argument("--port", type=int, help="主机端口")
    p.add_argument("--concurrency", type=int, default=3, help="并发数量")
    p.add_argument("--out-dir", default="./", help="探活数据落盘目录")
    p.add_argument("-v", "--verbose", action="store_true")  # 布尔开关（不带值）
    args = p.parse_args()

    # 解析host
    hosts = []
    if args.hosts:  # 直接传入的方式
        hosts = [h.strip() for h in str(args.hosts).split(args.seq) if h.strip()]
    if args.hosts_file:  # hosts文件传入方式
        with open(args.hosts_file, 'r', encoding="utf-8") as hosts_file:
            for host in hosts_file:
                host = str(host).strip()
                if host and not host.startswith("#"):
                    hosts.append(host)

    # 配置并发数量
    sem = asyncio.Semaphore(args.concurrency)

    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler('probe.log', encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    # 探测
    results = []
    async with sem:
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(*(probe.prob_tcp(session, host, args.port) for host in hosts))

    print(results)


if __name__ == "__main__":
    asyncio.run(main())
