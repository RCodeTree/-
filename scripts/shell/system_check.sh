#!/bin/bash
set -euo pipefail

log_info() { echo -e "\033[32m[INFO] $(date '+%F %T') $*\033[0m"; }
log_warn() { echo -e "\033[33m[WARN] $(date '+%F %T') $*\033[0m"; }



    # 1. 单方括号 [ ] 是内置命令，不支持 || 或 && 这样的逻辑运算符 
    # 2. 使用双方括号 [[ ]]（支持 || 和 &&），或者使用单方括号加 -o（代表 or）和 -a（代表 and） 
    # 3. -gt、-lt 等比较运算符只支持整数
    # 4. -o、-a 等逻辑运算符只支持整数
    # 5. -n、-z 等字符串比较运算符只支持字符串
    # 6. -f、-d 等文件比较运算符只支持文件
    # 7. 在 awk 的单引号 '...' 里面，shell 不会替换它们！ awk 会以为这是它自己的"字段变量"（$1、$2 那种），结果都是空值
    # 8. -v 传进去后，awk 里直接写 used、cores（不带 $），它们是 awk 自己的变量了

check_cpu() {
    cores=$(nproc)
    load1=$(uptime | awk -F'load average:' '{print $2}' | cut -d',' -f1 | tr -d ' ')
    log_info "CPU 核心数: $cores, 1分钟负载: $load1"
    if awk -v load="$load1" -v cores="$cores" 'BEGIN{exit !(load > cores)}'; then
        log_warn "CPU 负载过高！负载 $load1 > 核心数 $cores"
    else
        log_info "CPU 负载正常"
    fi
}

check_memory() {
    total=$(free -m | awk '/Mem:/{print $2}')
    available=$(free -m | awk '/Mem:/{print $7}')
    log_info "内存总量: ${total}MB, 可用: ${available}MB"
    if awk -v t="$total" -v a="$available" 'BEGIN{exit !((t-a)/t*100 > 80)}'; then
        log_warn "内存使用率超过 80%"
    else
        log_info "内存使用率正常"
    fi
}

check_disk() {
    df -h | awk 'NR>1 && +$5 > 80 {print $1" "$5" "$6}' | while read -r line; do
        log_warn "磁盘使用率超阈值: $line"
    done
}

check_network() {
    log_info "本机 IP: $(hostname -I)"
    log_info "监听端口:"
    ss -tlnp
    log_info "连接数汇总:"
    ss -s
}

log_info "===== 开始系统巡检 ====="
check_cpu
check_memory
check_disk
check_network
log_info "===== 巡检结束 ====="
