#!/bin/bash

# 日志函数
log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m"; }
log_info() { echo -e "\033[32m[INFO] $(date '+%F %T') $*\033[0m"; }
log_warn() { echo -e "\033[33m[WARN] $(date '+%F %T') $*\033[0m"; }

check_args() {
  if [[ $# -ne 2 ]]; then
    log_error "错误: 传入的普通参数数量不正确!"
    exit 2
  fi
}

getopts ":df" opt
case "$opt" in
      d)
            shift 1

            log_info "演练模式: 以下文件将被恢复到 ${}（未实际执行）"
            tar -tzf ${}
            exit 0
            ;;
      f)
            log_warn "警告: 目标目录${}非空, 正在强制恢复数据!"
            log_info "开始恢复: ${} -> ${}"
            tar -xvf ${} -C ${}
            log_info "恢复完成，共恢复 ${} 个文件/目录"
            exit 0
            ;;
      *)


