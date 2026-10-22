import logging
import report


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

    report.record_for_json()






    pass


if __name__ == "__main__":
    main()
