import logging
import os
import psutil
import platform
import datetime
import socket

log = logging.getLogger("collect")  # 配置模块日志


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
    log.info("获取CPU信息成功：逻辑核心数=>%s 物理核心数=>%s 总利用率=>%s", str(cpu_physical), str(cpu_physical),
             str(cpu_usage) + "%")
    cpu_info = {
        "cpu_logical": cpu_logical,
        "cpu_physical": cpu_physical,
        "cpu_usage": str(cpu_usage) + "%"
    }
    return cpu_info


# 采集内存
def get_memory():
    memory = psutil.virtual_memory()  # 获取 OS内存信息 元组
    total = round(memory.total / (1024 ** 3), 2)  # 字节 转 GB  保留两位小数
    used = round(memory.used / (1024 ** 3), 2)
    available = round(memory.available / (1024 ** 3), 2)
    percent = memory.percent
    log.info("获取内存信息成功：内存总量=>%sGB 已使用=>%sGB 可用=>%sGB 使用率=>%s", str(total), str(used),
             str(available), str(percent) + "%")
    memory_info = {
        "total": total,
        "used": used,
        "available": available,
        "percent": str(percent) + "%"
    }
    return memory_info


# 采集磁盘
def get_disk():
    disks_info = []
    disks = psutil.disk_partitions(all=False)  # all=False 过滤虚拟文件系统  ----> 返回磁盘信息列表
    for disk in disks:
        try:
            usage = psutil.disk_usage(disk.mountpoint)  # 获取其中一个磁盘的磁盘用量信息
            disks_info.append(
                {
                    "device": disk.device,
                    "mountpoint": disk.mountpoint,
                    "fstype": disk.fstype,
                    "total": round(usage.total / (1024 ** 3), 2),  # 字节转GB
                    "used_percent": usage.percent
                }
            )
            log.info("获取成功磁盘 %s 信息：磁盘=>%s 挂载点=>%s 格式化类型=>%s 总量=>%sGB 使用率=>%s", str(disk.device),
                     str(disk.device), str(disk.mountpoint), str(disk.fstype), str(round(usage.total / (1024 ** 3), 2)),
                     str(usage.percent) + "%")
        except PermissionError:  # 部分特殊挂载点可能无权限读取
            log.exception("访问该磁盘%s的权限不足，请联系管理员!", str(disk))
            continue

    return disks_info


# 采集IPv4
def get_IPv4():
    # addr.family：表示当前网络地址的协议族（Address Family）
    # socket.AF_INET：是 Python socket 模块中代表 IPv4 的常量。（如果是 IPv6，则是 socket.AF_INET6；如果是 MAC 地址，在 Linux 下通常是 psutil.AF_LINK）
    ipv4_list = []
    for iface, addrs in psutil.net_if_addrs().items():  # 分别拿到网卡和IPv4、IPv6的IP地址列表
        for addr in addrs:  # 每一块网卡的IP地址列表
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):  # 筛选 IPv4 并 筛选掉本机回环地址
                ipv4_list.append({"interface": iface, "ip": addr.address})
                log.info("成功获取系统IPv4地址：网卡=>%s IP地址=>%s", iface, addr.address)
    return ipv4_list


# 采集开机时间
def get_boot_time():
    boot_ts = psutil.boot_time()  # 获取开机时间的时间戳
    boot_time = datetime.datetime.fromtimestamp(boot_ts).strftime("%Y-%m-%d %H:%M:%S")  # 通过时间戳计算当下时间
    log.info("获取开机时间成功：%s", str(boot_time))
    return boot_time


# 采集进程数
def get_process_count():
    process_count = len(psutil.pids())
    # 或者通过生成器统计（适合同时需要读取进程属性时）：
    # process_count = sum(1 for _ in psutil.process_iter())
    log.info("获取当前系统进程数成功：%s", str(process_count))
    return process_count
