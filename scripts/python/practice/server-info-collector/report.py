import logging
import yaml
import collect
import json
from datetime import datetime

log = logging.getLogger("report")  # 配置模块日志

# 获取系统总信息
def get_os_info():
    date = datetime.now().strftime("%Y%m%d-%H%M%S")
    hostname = collect.get_hostname()
    os_ = collect.get_os()
    cpu = collect.get_cpu()
    memory = collect.get_memory()
    disk = collect.get_disk()
    IPv4 = collect.get_IPv4()
    boot_time = collect.get_boot_time()
    process_count = collect.get_process_count()

    os_info = {
        "hostname": hostname,
        "os": os_,
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "IPv4": IPv4,
        "boot_time": boot_time,
        "process_count": process_count
    }
    return os_info, date


# 序列化成json文件
def record_for_json():
    os_info, date = get_os_info()
    try:
        with open(f"collector-{date}.json", "w", encoding="utf-8") as json_file:
            json.dump(os_info, json_file, ensure_ascii=False, indent=2)
        log.info(f"已经记录到collector-{date}.json中")
    except Exception:
        log.exception("文件操作异常，请检查!")
        return


# 序列化成yaml文件
def record_for_yaml():
    os_info, date = get_os_info()
    try:
        with open(f"collector-{date}.yaml", "w", encoding="utf-8") as json_file:
            yaml.safe_dump(os_info, json_file, allow_unicode=True)
        log.info(f"已经记录到collector-{date}.yaml中")
    except Exception:
        log.exception("文件操作异常，请检查!")
