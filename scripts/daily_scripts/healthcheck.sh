#!/bin/bash

# 使用 set 防止脚本错误运行下去
set -euo pipefail


# 选项参数和默认参数
CONFIG=""
RETRIES=3
TIMEOUT=3
INTERVAL=2


# 日志函数
log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m" >&2; }
log_info() { echo -e "\033[32m[INFO] $(date '+%F %T') $*\033[0m"; }
log_warn() { echo -e "\033[33m[WARN] $(date '+%F %T') $*\033[0m"; }


# 用法提醒函数
usage(){
  log_error "$0 -c <配置文件> [-r <重试次数>] [-t <超时秒>] [-h]"
  log_error "-c：巡检清单文件路径（必填）"
  log_error "-r：每个目标失败后的重试次数，默认 3"
  log_error "-t：单次探测超时秒数，默认 3"
  log_error "示例: $0 -c /tmp/healthcheck.conf -r 3 -t 3"
}


# 提取选项参数和默认参数，并根据选项参数传入的值进行赋值
while getopts ":c:r:t:h" opt
do
  case "$opt" in
    c) CONFIG="$OPTARG" ;;
    r) RETRIES="$OPTARG" ;;
    t) TIMEOUT="$OPTARG" ;;
    h) usage; exit 0 ;;
    \?) usage; exit 2 ;;
  esac
done

shift $((OPTIND - 1))


# 校验必填参数
if [ -z "$CONFIG" ]; then # -z 判断变量是否为空
  usage;
  exit 2
fi
if [ ! -f "$CONFIG" ]; then
  log_error "错误: ${CONFIG} 不是一个合法文件"
  exit 2
fi
if [ ! -r "$CONFIG" ]; then
  log_error "错误: ${CONFIG} 不可读"
  exit 2
fi


# 探测http的服务
check_http(){
  local url="$1" code
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time "$TIMEOUT" "$url" || true)
  [ "$code" -eq 200 ]
}

# 探测tcp的服务
check_tcp(){
  local addr="$1"
  local host="${addr%%:*}"   # 取冒号前
  local port="${addr##*:}"   # 取冒号后
  timeout "$TIMEOUT" bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null
}

check_proc(){
  local name="$1"
  pgrep -x "$name" >/dev/null 2>&1 # -x 精准匹配服务进程的名称   pgrep  按进程名称或条件查找PID
}

# 带重试的探测
check_with_retry(){
  local type="$1" name="$2" addr="$3" i
  for ((i = 1; i <= RETRIES; i++));
    do
      case "$type" in
        http) check_http "$addr" && return 0 ;;
        tcp) check_tcp "$addr" && return 0 ;;
        proc) check_proc "$name" && return 0 ;;
        *) log_warn "未知类型: $type（跳过 $name）"; return 2 ;;
      esac
      if [ $i -lt "$RETRIES" ]; then # 如果没有超过重试次数，则进行时间间隔
        sleep "$INTERVAL"
      fi
    done
  return 1
}

# ==================== 主流程 ====================
up=0; down=0; total=0
log_info "开始健康巡检，配置文件: $CONFIG"

while IFS= read -r line || [ -n "$line" ]; do
    # 跳过空行与注释行
    [ -z "$line" ] && continue
    case "$line" in \#*) continue ;; esac

    # 拆字段：类型 名称 目标
    read -r type name addr <<< "$line"

    if [ -z "$type" ] || [ -z "$name" ]; then
        log_warn "配置行格式错误，已跳过: $line"
        continue
    fi

    total=$((total + 1))
    if check_with_retry "$type" "$name" "$addr"; then
        log_info "[UP]   $name ($type) -> $addr"
        up=$((up + 1))
    else
        log_error "[DOWN] $name ($type) -> $addr"
        down=$((down + 1))
    fi
done < "$CONFIG"

log_info "巡检结束: 共 $total 项，UP=$up，DOWN=$down"

# 用退出码表达健康状态，供监控/告警使用
if [ "$down" -gt 0 ]; then
    exit 1
fi
exit 0






