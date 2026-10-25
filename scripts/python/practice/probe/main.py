import asyncio
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

import probe
import upload


async def main():
    # 配置解析CLI参数
    p = argparse.ArgumentParser(description="多主机批量探活 + 并发上报")
    p.add_argument("--seq", default=",", help="分隔符")
    p.add_argument("--hosts", help="多个主机IP(直接传入)")
    p.add_argument("--hosts-file", type=str,
                   help="多个主机IP(文件形式)")  # argparse.FileType("r") 会在参数解析阶段立即打开文件，文件不存在就直接报错退出，这通常没问题。但如果你的脚本可能长时间运行、或者要重复使用文件名，建议改成 type=str，用的时候再打开
    p.add_argument("--port", type=int, help="主机端口", required=True)
    p.add_argument("--concurrency", type=int, default=3, help="并发数量")
    p.add_argument("--timeout", default=3.0, type=float, help="超时时长")
    p.add_argument("-v", "--verbose", action="store_true")  # 布尔开关（不带值）
    args = p.parse_args()

    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler('probe.log', encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    log = logging.getLogger("main")

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

    if not hosts:
        p.error("请通过 --hosts 或 --hosts-file 提供主机列表")

    log.info("待探测主机 %d 台: %s (port=%s, concurrency=%s, timeout=%ss)",
             len(hosts), hosts, args.port, args.concurrency, args.timeout)

    # 配置并发数量
    sem = asyncio.Semaphore(args.concurrency)

    # 探测
    results = []
    results = await asyncio.gather(*(probe.prob_all(host, args.port, args.timeout, sem) for host in hosts))

    alive = [r for r in results if r["alive"]]
    down = [r for r in results if not r["alive"]]
    log.info("探测完成: 在线 %d / 离线 %d / 共 %d", len(alive), len(down), len(results))

    # 落盘
    date = datetime.now().strftime("%Y%m%d-%H%M%S")
    dir_path = Path("report")
    dir_path.mkdir(exist_ok=True, parents=True)
    final_path = dir_path / f"prob-{date}.json"
    final_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("结果已落盘: %s", final_path)

    # 上报（尽力而为，失败不影响已完成的探活与落盘）
    upload.upload(results)


if __name__ == "__main__":
    asyncio.run(main())
