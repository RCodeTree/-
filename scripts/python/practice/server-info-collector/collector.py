import logging

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




    pass

if __name__ == "__main__":
    main()