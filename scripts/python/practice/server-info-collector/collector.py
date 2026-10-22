import logging
import report
import argparse


def main():
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler('collector.log', encoding="utf-8"),
            logging.StreamHandler()
        ]

    )

    # 接收CLI参数
    p = argparse.ArgumentParser(description="执行示例：python collector.py [--output json/yaml] [--out-dir dir] [-v]")
    p.add_argument("--output", default="json")  # 可选参数 + 默认值
    p.add_argument("--out-dir", default="./")  # 类型转换
    p.add_argument("-v", "--verbose", action="store_true")  # 布尔开关（不带值）
    args = p.parse_args()

    match args.output:
        case "json":
            report.record_for_json()
        case "yaml":
            report.record_for_yaml()


if __name__ == "__main__":
    main()
