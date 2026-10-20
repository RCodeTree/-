import logging
import collect
import report


def main():
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('collector.log'),
            logging.StreamHandler()
        ]
    )


    collect.get_memory()





    pass


if __name__ == "__main__":
    main()
