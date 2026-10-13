#!/bin/bash

# 使用 set 防止脚本错误运行下去
set -euo pipefail


# 目录黑名单
blacklist_dir=("/" "/etc" "/bin" "/sbin" "/usr" "/lib" "/boot" "/root" "/dev" "/proc" "/sys")


# 选项参数
log_dir="" # 日志目录(要清理的)
preserve_day=7 # 保留天数 --- 默认值 7 天
review_log="/tmp/log_clean.log" # 审计日志
compress_mode=false # 是否启用压缩模式
execute_mode=false # 是否启用执行模式



# 日志函数
log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m" >&2; }
log_info() { echo -e "\033[32m[INFO] $(date '+%F %T') $*\033[0m"; }
log_warn() { echo -e "\033[33m[WARN] $(date '+%F %T') $*\033[0m"; }


# 用法提醒函数
usage(){
  log_error "$0 -d <日志目录> [-p <保留天数>] [-z] [-e] [-l <审计日志>] [-h]"
  log_error "-d：要治理的日志目录（必填）"
  log_error "-p：保留最近 N 天（默认 7），正整数"
  log_error "-z：压缩模式——把超期 *.log 用 gzip 归档为 *.gz（压缩成功后再删原文件）"
  log_error "-e：执行模式——真正删除/压缩；不加 -e 时默认 dry-run，只打印将处理哪些文件"
  log_error "-l：审计日志文件（默认 /tmp/log_clean.log）"
  log_error "-h：打印用法"
  log_error "示例：$0 -d /var/log -p 7 -z -e -l /tmp/log_clean.log"
}


# 获取选项参数
while getopts ":d:p:zel:h" opt
do
  case "$opt" in
    d) log_dir="$OPTARG" ;;
    p) preserve_day="$OPTARG" ;;
    z) compress_mode=true ;;
    e) execute_mode=true ;;
    l) review_log="$OPTARG" ;;
    h)
      usage;
      exit 0
      ;;
    \?)
      log_error "错误: 非法参数: $OPTARG!";
      usage;
      exit 1
      ;;
    :)
      log_error "错误: 未能提供参数值!";
      usage;
      exit 1
      ;;
  esac
done


# 校验选项参数
for (( i = 0; i < ${#blacklist_dir[@]}; i++ )); do
  if [ "$log_dir" = "${blacklist_dir[$i]}" ]; then
    log_error "错误: 日志目录在黑名单中: $log_dir!"
    exit 1
  fi
done
if [ ! -d "$log_dir" ]; then
  log_error "错误: 日志目录不存在: $log_dir!"
  exit 1
fi
if [[ ! -x "$log_dir" || ! -r "$log_dir" ]]; then
  log_error "错误: 日志目录无执行或读取权限: $log_dir!"
  exit 1
fi
if [[ ! $preserve_day =~ ^[1-9]+$ ]]; then
  log_error "错误: 保留天数必须是正整数: $preserve_day!"
  exit 2
fi


# 获取清理文件数量和体积
clean_count=$(find "$log_dir"  -type f -name '*.log' -mtime +$preserve_day | wc -l) # 清理的文件数量
clean_volume=$(du -ch $(find "$log_dir"  -type f -name '*.log' -mtime +"$preserve_day") | tail -n 1 | awk '{print $1}') # 清理的文件体积


# dry-run模式
if [ "$execute_mode" = false ]; then
  log_warn "[dry-run]以下 $clean_count 个文件将被处理（模式: delete，合计约 $clean_volume）:"
  find "$log_dir"  -type f -name '*.log' -mtime +$preserve_day
  log_info "本次为演练，未做任何改动。确认无误后加 -e 执行。"
  echo "date:$(date '+%F %T') mode:dry-run dir:${log_dir} preserve_day:${preserve_day} clean_count:${clean_count} result:success" >> "$review_log"
  exit 0
fi


# 删除模式
if [[ "$execute_mode" = true && "$compress_mode" = false ]]; then
  delete_count=0
  while IFS= read -r file || [[ -n "$file" ]]; do
    rm -f "$file"
    ((delete_count++))
  done < $(find "$log_dir"  -type f -name '*.log' -mtime +$preserve_day)
  log_info "处理完成: 共命中 $clean_count 个，成功处理 $clean_count 个（模式: delete，约 $clean_volume）"
  echo "date:$(date '+%F %T') mode:delete dir:${log_dir} preserve_day:${preserve_day} clean_count:${clean_count} result:success" >> "$review_log"
  exit 0
fi













