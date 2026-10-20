import logging
import os
import psutil
import platform

log = logging.getLogger("__name__")  # 配置模块日志


# 采集主机名
def get_hostname():
    hostname = os.uname().nodename
    log.info("获取主机名成功：%s", hostname)
    return hostname


# 采集OS
def get_os():
    os_ = platform.system()
    log.info("获取OS成功：%s", os_)
    return os_


# 采集CPU
def get_cpu():
    cpu_logical = psutil.cpu_count(logical=True)  # 逻辑核心数
    cpu_physical = psutil.cpu_count(logical=False)  # 物理核心数
    cpu_usage = psutil.cpu_percent(interval=1)  # CPU 总利用率（%），采样 1 秒
    log.info("获取CPU信息成功：逻辑核心数=>%s 物理核心数=>%s 总利用率=>%s", cpu_physical, cpu_physical, cpu_usage)
    return cpu_logical, cpu_physical, cpu_usage


# 采集内存
def get_memory():
    memory = psutil.virtual_memory()  # 获取 OS内存信息 元组
    total = round(memory.total / (1024 ** 3), 2)  # 字节 转 GB  保留两位小数
    used = round(memory.used / (1024 ** 3), 2)
    available = round(memory.available / (1024 ** 3), 2)
    percent = memory.percent
    log.info("获取内存信息成功：内存总量=>%sGB 已使用=>%sGB 可用=>%sGB 使用率=>%s", str(total), str(used), str(available), str(percent))
    return total, used, available, percent


# 采集磁盘
def get_disk():
    return


# 采集IPv4
def get_IPv4():
    return


# 采集开机时间
def get_boot_time():
    return


# 采集进程数
def get_process_count():
    return
