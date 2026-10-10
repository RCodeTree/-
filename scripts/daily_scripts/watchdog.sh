#!/bin/bash

# 使用 set 防止脚本错误运行下去
set -euo pipefail


# 获取当前脚本名称
BASENAME=$(basename "$0")


# 选项参数
CONFIG_SCRIPT="" # 传给运行脚本的配置文件
STATE="" # 状态文件
LOG="/tmp/watchdog_alert.log" # 日志文件


# 运行的脚本参数
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
    c) CONFIG_SCRIPT="$OPTARG" ;;
    s) STATE="$OPTARG" ;;
    l) LOG="$OPTARG" ;;
    *) usage; exit 2 ;;
    \?) log_error "非法选项: -$OPTARG" ;;
  esac
done


# 校验选项参数
if [ -z "$CONFIG_SCRIPT" ] || [ -z "$STATE" ]; then
  log_error "请传入巡检配置文件和状态文件"
  usage
  exit 2
fi
if [ ! -f "$CONFIG_SCRIPT" ]; then
  log_error "巡检配置文件不存在"
  exit 2
fi
if [ ! -f "$STATE" ]; then
  log_error "状态文件不存在"
  log_info "正在创建状态文件..."
  STATE=$(touch "$STATE")
  log_info "状态文件已创建"
fi
if [ ! -r "$CONFIG_SCRIPT" ]; then
  log_error "巡检配置文件不可读"
  exit 2
fi
if [ ! -w "$CONFIG_SCRIPT" ]; then
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
source "$STATE"


# 运行脚本
DATE=$(date "+%F %T")
TMP_OUT=$(mktemp "/tmp/.${BASENAME}_${DATE}.XXXXXX")
if bash "/云计算运维/scripts/daily_scripts/healthcheck.sh" -c "$CONFIG_SCRIPT" -r "$RETRIES_SCRIPT" -t "$TIMEOUT_SCRIPT" > "$TMP_OUT" 2>&1; then # 本次巡检结果都为UP
  log_info "上次状态: ${LAST_STATUS}"
  log_info "本次状态: UP"
  if [[ $LAST_STATUS == "DOWN" && $CURRENT_STATUS == "UP" ]]; then
    echo "[$(date '+%F %T')] RECOVERY ${LAST_STATUS} -> ${CURRENT_STATUS} config=${CONFIG_SCRIPT} summary=\"巡检结束: 共 ${total} 项，UP=${up}，DOWN=${down}\"" >> "$LOG"
    log_warn "检测到状态变化: ${LAST_STATUS} -> ${CURRENT_STATUS}，已写入告警日志${LOG}"
  fi
  sed -i "s/LAST_STATUS=.*/LAST_STATUS=UP/" "$STATE" # 更新状态
  sed -i "s/LAST_CHECK_TIME=.*/LAST_CHECK_TIME=$(date "+%F %T")/" "$STATE" # 更新时间
else # 本次巡检结果有不同的状态结果
  rc=$? # 获取返回码
  source "/云计算运维/scripts/daily_scripts/healthcheck.sh"
  CURRENT_STATUS="" # 当前状态
  log_info "上次状态: ${LAST_STATUS}"
  case $rc in
    1)
      CURRENT_STATUS="DOWN"
      log_info "本次状态: ${CURRENT_STATUS}"
      if [[ $LAST_STATUS == "UP" && $CURRENT_STATUS == "DOWN" ]]; then # 状态变化: UP -> DOWN
        echo "[$(date '+%F %T')] ALERT ${LAST_STATUS} -> ${CURRENT_STATUS} config=${CONFIG_SCRIPT} summary=\"巡检结束: 共 ${total} 项，UP=${up}，DOWN=${down}\"" >> "$LOG"
        log_warn "检测到状态变化: ${LAST_STATUS} -> ${CURRENT_STATUS}，已写入告警日志${LOG}"
      fi
      sed -i "s/LAST_STATUS=.*/LAST_STATUS=${CURRENT_STATUS}/" "$STATE" # 更新状态
      sed -i "s/LAST_CHECK_TIME=.*/LAST_CHECK_TIME=$(date "+%F %T")/" "$STATE" # 更新时间
      ;;
    2)
      log_info "本次状态: ERROR"

      ;;
  esac

fi





