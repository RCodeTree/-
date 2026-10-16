import shutil

def main():
    # 磁盘巡检脚本 disk_check.py 用 shutil.disk_usage 输出 总/已用/可用/使用率，使用率 > 85% 时打印告警
    disk_status = shutil.disk_usage("/") # total used free
    total_gib = disk_status.total / (1024 ** 3)
    used_gib = disk_status.used / (1024 ** 3)
    free_gib = disk_status.free / (1024 ** 3)
    used_percent = disk_status.used / disk_status.total * 100
    print(f"Total: {total_gib:.2f} GiB")
    print(f"Used: {used_gib:.2f} GiB")
    print(f"Free: {free_gib:.2f} GiB")
    print(f"Used Percentage: {used_percent:.2f}%")
    if used_percent > 85:
        print("Warning: Disk usage is above 85%")
    pass


if __name__ == "__main__":
    main()

