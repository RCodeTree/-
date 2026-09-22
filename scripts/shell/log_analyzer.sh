#!/bin/bash
set -euo pipefail

LOG_FILE="${1:-}"

log_info()  { echo -e "\033[32m[INFO]  $(date '+%F %T') $*\033[0m"; }
log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m" >&2; }

# 1. 参数校验
[ -z "$LOG_FILE" ] && { log_error "用法: $0 <日志文件>"; exit 2; }
[ ! -f "$LOG_FILE" ] && { log_error "文件不存在: $LOG_FILE"; exit 1; }

# 2. 各分析函数（你来补全）
total_requests() {
    wc -l < "$LOG_FILE"
}

unique_ips() {
    awk '{print $1}' "${LOG_FILE}" | sort -u | wc -l
}

top_ips() {
    awk '{print $1}' "${LOG_FILE}" | sort | uniq -c | sort -rn | head -5
}

status_codes() {
    awk '{print $9}' "${LOG_FILE}" | sort | uniq -c | sort -rn
}

http_methods() {
    awk -F'"' '{print $2}' "${LOG_FILE}" | awk '{print $1}' | sort | uniq -c | sort -rn
}

# 3. 主流程
log_info "开始分析: $LOG_FILE"
echo "===== 总请求数 =====";   total_requests
echo "===== 独立 IP 数 ====="; unique_ips
echo "===== Top 5 IP =====";   top_ips
echo "===== 状态码分布 ====="; status_codes
echo "===== HTTP 方法 =====";  http_methods
log_info "分析完成"