#!/bin/bash

# 使用 set 防止脚本错误运行下去
set -euo pipefail


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













