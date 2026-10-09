#!/bin/bash

# 使用 set 防止脚本错误运行下去
set -euo pipefail


# 选项参数
CONFIG="" # 配置文件
STATE="" # 状态文件
LOG="/tmp/watchdog_alert.log" # 日志文件


# 运行的脚本参数
CONFIG_SCRIPT="/tmp/healthcheck.conf" # 配置文件
RETRIES_SCRIPT=3 # 重试次数
TIMEOUT_SCRIPT=3 # 超时时间
INTERVAL_SCRIPT=2 # 间隔时间



# 日志函数
log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m" >&2; }
log_info() { echo -e "\033[32m[INFO] $(date '+%F %T') $*\033[0m"; }
log_warn() { echo -e "\033[33m[WARN] $(date '+%F %T') $*\033[0m"; }


# 用法提醒函数
usage(){
  log_error "$0 -c <巡检配置> -s <状态文件> [-l <日志文件>]"
  log_error "-c：传给 healthcheck.sh 的巡检配置文件"
  log_error "-s：状态文件路径（必须持久化保存）"
  log_error "-l：告警日志文件，可选；若不传则默认 /tmp/watchdog_alert.log"
  log_error "示例：$0 -c /tmp/healthcheck.conf -s /tmp/watchdog.state"
}


# 获取选项参数
while getopts ":c:s:l:" opt
do
  case $opt in
    c) CONFIG="$OPTARG" ;;
    s) STATE="$OPTARG" ;;
    l) LOG="$OPTARG" ;;
    *) usage; exit 2 ;;
    \?) log_error "非法选项: -$OPTARG" ;;
  esac
done


# 校验选项参数
if [ -z "$CONFIG" ] || [ -z "$STATE" ]; then
  log_error "请传入巡检配置文件和状态文件"
  usage
  exit 2
fi
if [ ! -f "$CONFIG" ]; then
  log_error "巡检配置文件不存在"
  exit 2
fi
if [ ! -f "$STATE" ]; then
  log_error "状态文件不存在"
  log_info "正在创建状态文件..."
  STATE=$(touch "$STATE")
  log_info "状态文件已创建"
fi
if [ ! -r "$CONFIG" ]; then
  log_error "巡检配置文件不可读"
  exit 2
fi
if [ ! -w "$CONFIG" ]; then
  log_error "巡检配置文件不可写"
  exit 2
fi
if [ ! -w "$STATE" ]; then
  log_error "状态文件不可写"
  exit 2
fi
if [ ! -w "$LOG" ]; then
  log_error "日志文件不可写"
  exit 2
fi


#  source 状态文件，拿到 LAST_STATUS / LAST_CHECK_TIME
source "$LOG"







