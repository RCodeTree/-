import logging
import collect
import json
from datetime import datetime

log = logging.getLogger("report")  # 配置模块日志


def record_for_json():
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

    date = datetime.now().strftime("%Y%m%d-%H%M%S")
    try:
        with open(f"collector-{date}.json", "w", encoding="utf-8") as json_file:
            json.dump(os_info, json_file, ensure_ascii=False, indent=2)
    except Exception:
        log.exception("文件操作异常，请检查!")
        return


def record_for_yaml():
    return
