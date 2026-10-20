import argparse
from datetime import datetime, timedelta


def main():
    # 练习1 — CLI采集参数写collect_cli.py：接收 - -host、--port(int, 默认8080)、--interval(int, 默认30)、-v / --verbose，打印解析结果。
    parser = argparse.ArgumentParser(description="Collect CLI")
    parser.add_argument("--host", help="目标主机")
    parser.add_argument("--port", type=int, default=8080, help="目标端口")
    parser.add_argument("--interval", type=int, default=30, help="时间间隔")
    parser.add_argument("-v", "--verbose", action="store_true", help="是否显示详细信息")

    args = parser.parse_args()
    print(args.host)
    print(args.port)
    print(args.interval)

    print("\n")

    # 练习2——日期运算 计算“今天 + 7天”和“今天 - 30天”，用strftime输出结果
    today = datetime.now()
    print("Today:", today.strftime("%Y-%m-%d"))
    print("Today + 7 days:", (today + timedelta(days=7)).strftime("%Y-%m-%d"))
    print("Today - 30 days:", (today - timedelta(days=30)).strftime("%Y-%m-%d"))


    print("\n")

    # 练习3——带时间戳的日志文件名 生成collector-YYYYMMDD-HHMMSS.log文件名
    log_file_name = f"collector-{today.strftime('%Y%m%d-%H%M%S')}.log"
    print("Log file name:", log_file_name)

pass

if __name__ == "__main__":
    main()
