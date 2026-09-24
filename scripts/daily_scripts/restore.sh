#!/bin/bash

# 日志函数
log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m"; }
log_info() { echo -e "\033[32m[INFO] $(date '+%F %T') $*\033[0m"; }
log_warn() { echo -e "\033[33m[WARN] $(date '+%F %T') $*\033[0m"; }

# 校验普通参数
check_args() {

  # 校验普通参数数量
  if [[ $# -ne 2 ]]; then
    log_error "错误: 传入的普通参数数量不正确!"
    exit 2
  fi

  # 校验文件有效性
  if [[ ! -f "$backup_file" || ! -r "$backup_file" || "$backup_file" =~ *.tar.gz ]]; then
    log_error "错误: ${backup_file} 不存在或不可读或不是有效文件!"
    exit 1
  fi

  # 校验目标目录有效性
  if [[ ! -d "$target_dir" || ! -x "$target_dir" ]]; then
    log_error "错误: 错误：${target_dir} 源目录不存在或 ${target_dir} 不是一个目录!"
    exit 1
  fi
}

  # 恢复文件
  restore() {
    double_point=$(tar -tzf "$backup_file" | grep ".." | wc -l)
    if [[ $double_point -eq 1 ]]; then
      log_error "错误: 备份路径存在问题，停止备份......"
      exit 1
    fi

    count=$(tar -tzf "$backup_file"  | awk "NR > 1" | wc -l)

    log_info "开始恢复: ${backup_file} -> ${target_dir}"
    if ! tar -xvf $backup_file -C $target_dir > /dev/null 2>&1; then
      log_error "错误: 文件恢复失败!"
      exit 1
    fi
    log_info "恢复完成，共恢复 ${count} 个文件/目录"
  }

# 获取普通参数
backup_file=$1
target_dir=$2

# 有参数的处理
getopts ":df" opt
case "$opt" in
      d)
            shift 1
            check_args
            log_info "演练模式: 以下文件将被恢复到 ${target_dir}（未实际执行）"
            tar -tzf $backup_file
            exit 0
            ;;
      f)
            shift 1
            check_args
            log_warn "警告: 目标目录${target_dir}非空, 正在强制恢复数据!"
            restore
            exit 0
            ;;
      \?)
            log_error "错误: 错误参数!"
            exit 1
            ;;
esac

# 只有普通参数的处理
check_args
restore



