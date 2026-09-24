#!/bin/bash

# 日志函数
log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m"; }
log_info() { echo -e "\033[32m[INFO] $(date '+%F %T') $*\033[0m"; }
log_warn() { echo -e "\033[33m[WARN] $(date '+%F %T') $*\033[0m"; }

# 校验普通参数 参数1：文件  参数2：目标目录
  check_args() {
    # 校验文件有效性
    if [[ ! -f "$1" || ! -r "$1" || "$1" =~ *.tar.gz ]]; then
      log_error "错误: $1 不存在或不可读或不是有效文件!"
      exit 1
    fi

    # 校验目标目录有效性
    if [[ ! -d "$2" || ! -x "$2" ]]; then
      log_error "错误: 错误：$2 源目录不存在或 $2 不是一个目录!"
      exit 1
    fi
  }

  # 恢复文件
  restore() {
    double_point=$(tar -tzf "$1" | grep ".." | wc -l)
    if [[ $double_point -eq 1 ]]; then
      log_error "错误: 备份路径存在问题，停止备份......"
      exit 1
    fi

    count=$(tar -tzf "$1"  | awk "NR > 1" | wc -l)

    log_info "开始恢复: $1 -> $2"
    if ! tar -xvf "$1" -C "$2" > /dev/null 2>&1; then
      log_error "错误: 文件恢复失败!"
      exit 1
    fi
    log_info "恢复完成，共恢复 ${count} 个文件/目录"
  }


# 有参数的处理
while getopts ":df" opt
do
  case "$opt" in
        d)
              shift $((OPTIND - 1))
              if [[ $# -ne 2 ]]; then # 校验普通参数数量
                log_error "错误: 传入的普通参数数量不正确!"
                exit 2
              fi

              check_args "$1" "$2"
              log_info "演练模式: 以下文件将被恢复到 $2（未实际执行）"
              tar -tzf "$1"
              exit 0
              ;;
        f)
              shift $((OPTIND - 1))
              if [[ $# -ne 2 ]]; then # 校验普通参数数量
                log_error "错误: 传入的普通参数数量不正确!"
                exit 2
              fi

              check_args "$1" "$2"
              log_warn "警告: 目标目录 $2 非空, 正在强制恢复数据!"
              restore "$1" "$2"
              exit 0
              ;;
        \?)
              log_error "错误: 错误参数!"
              exit 1
              ;;
  esac
done

# 只有普通参数的处理
check_args "$1" "$2"
restore "$1" "$2"



