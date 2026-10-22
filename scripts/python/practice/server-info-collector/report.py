import logging
import yaml
import collect
import json
from datetime import datetime
from pathlib import Path

log = logging.getLogger("report")  # 配置模块日志


# 获取系统总信息
# fn 是函数对象，fn() 才是执行调用。存进字典用于“延迟调用”时，必须存 fn 不带括号。
def get_os_info():
    date = datetime.now().strftime("%Y%m%d-%H%M%S")
    collector = {
        "hostname": collect.get_hostname,
        "os": collect.get_os,
        "cpu": collect.get_cpu,
        "memory": collect.get_memory,
        "disk": collect.get_disk,
        "IPv4": collect.get_IPv4,
        "boot_time": collect.get_boot_time,
        "process_count": collect.get_process_count
    }

    os_info = {}
    for key, fn in collector.items():
        try:
            os_info[key] = fn()
        except Exception:
            os_info[key] = None
            log.exception("采集失败: %s", key)
    return os_info, date


# 序列化成json文件
def record_for_json(out_dir="reports"):
    os_info, date = get_os_info()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"collector-{date}.json"
    path.write_text(json.dumps(os_info, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("已记录到 %s", path)


# 序列化成yaml文件
def record_for_yaml(out_dir="reports"):
    os_info, date = get_os_info()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"collector-{date}.yaml"
    path.write_text(yaml.safe_dump(os_info, allow_unicode=True), encoding="utf-8")
    log.info("已记录到 %s", path)
