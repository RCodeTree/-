#!/bin/bash
set -euo pipefail

log_info() { echo -e "\033[32m[INFO] $(date '+%F %T') $*\033[0m"; }
log_warn() { echo -e "\033[33m[WARN] $(date '+%F %T') $*\033[0m"; }

check_cpu() {
	cores=$(nproc)
    used1=$(uptime | awk '{print $9, $10}' | awk -F, '{print $1}')
    used2=$(uptime | awk '{print $9, $10}' | awk -F, '{print $2}')
    if [ $used1 -gt $cores || $used2 -gt $cores ]; then
    	log_warn
    fi
}

check_memory() {
    total=$(free -m | grep 'Mem:' | awk '{print $2}')
    available=$(free -m | grep 'Mem:' | awk '{print $6}')
    check=$((available / total))
    if [ $check -gt 0.8 || $check -gt 0.8 ]; then
    log_warn
    fi
}

check_disk() {
    used=$(df -h | awk  'BEGIN{sum = 0}   NR > 1{sum += $5} END{print sum / 100 }')
    if [ $used -gt 0.8  ]; then
    	log_warn
    fi
}

check_network() {
	hostname -I        # 本机所有 IP
	ss -tlnp           # 看监听中的 TCP 端口（-t tcp -l 监听 -n 数字 -p 进程）
	ss -s              # 连接数汇总
}

log_info "===== 开始系统巡检 ====="
check_cpu
check_memory
check_disk
check_network
log_info "===== 巡检结束 ====="