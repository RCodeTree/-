import shutil

def main():
    # 磁盘巡检脚本 disk_check.py 用 shutil.disk_usage 输出 总/已用/可用/使用率，使用率 > 85% 时打印告警
    status = shutil.disk_usage("/")
    print(status)
    pass


if __name__ == "__main__":
    main()

