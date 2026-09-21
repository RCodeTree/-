#!/bin/bash

# 使用 set 防止脚本错误运行下去
set -euo pipefail

# 日志函数
log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m" | tee -a "$log_file"; }
log_info() { echo -e "\033[32m[INFO] $(date '+%F %T') $*\033[0m" | tee -a "$log_file"; }
log_warn() { echo -e "\033[33m[WARN] $(date '+%F %T') $*\033[0m" | tee -a "$log_file"; }

TMPFILE=""

# 清理函数
clean_up() {
     if [[ -n "$TMPFILE" && -f "$TMPFILE" ]]; then
        rm -f "$TMPFILE"
        log_warn "已清理未完成的临时文件: $TMPFILE"
     fi
}

# 提示函数
usage() {
	# 用法: ./backup.sh [-k 保留份数] <源目录> <备份目录>
    echo -e "\033[32m用法: ./backup.sh [-k 保留份数] <源目录> <备份目录>\033[0m"
}

trap clean_up EXIT          # 任何退出都走清理（成功时 TMPFILE 已清空，不误删）
trap 'exit 130' INT         # Ctrl+C → 退出码 130 = 128 + 2(SIGINT)
trap 'exit 143' TERM        # kill   → 退出码 143 = 128 + 15(SIGTERM)


# 参数校验
if [ $# -ne 2 ]; then
    log_error "错误：参数数量错误，需要提供源目录和备份目录!" 
    log_error "用法：./backup.sh <源目录> <备份目录>" 
    log_error "示例：./backup.sh /var/html /backupdir" 
    exit 2
fi

# 源目录、备份目录
source_dir=$1
target_dir=$2

# 磁盘空间阈值
disk_max=90


# 日志文件
log_file="/var/log/backup.log"

# 校验日志文件是否存在
log_info "正在校验日志文件有效性" 
if [[ ! -f "$log_file"  ]]; then
	log_error "错误：${log_file} 源目录不存在或 ${log_file} 不是一个目录!" 
	log_warn "警告：备份目录 ${log_file} 正在创建......"
    if ! touch "$log_file" || chmod u+w "$log_file"; then
    	log_error "错误：日志文件创建失败!"
    	log_error "错误：日志文件修改权限失败!"
        exit 1
    fi
fi


# 校验源目录是否存在
log_info "正在校验源目录有效性" 
if [[ ! -d "$source_dir"  ]]; then
	log_error "错误：${source_dir} 源目录不存在或 ${source_dir} 不是一个目录!" 
	log_error "用法：./backup.sh <源目录> <备份目录>" 
    log_error "示例：./backup.sh /var/html /backupdir" 
    exit 1
fi

# 校验源目录是否可读可写
if [[ ! -r "$source_dir" || ! -x "$source_dir"  ]]; then
	log_error "错误：${source_dir} 源目录不可读!" 
    exit 1
fi

# 校验备份目录是否存在
log_info "正在校验备份目录有效性" 
if [[ ! -d "$target_dir"  ]]; then
	log_error "错误：${target_dir} 备份目录不存在或 ${target_dir} 不是一个目录!" 
    log_warn "警告：备份目录 ${target_dir} 正在创建......" 
    if ! mkdir -p "$target_dir"; then
    	log_error "错误：备份目录创建失败!" 
    	exit 1
    fi
fi


# 校验备份目录所在的磁盘空间
disk_used=$(df -h | awk 'NR>1 && $6 == "/" {print +$5}')
if [[ $disk_used -gt $disk_max ]]; then
	log_error "错误：备份盘使用率已达 ${disk_used}%，空间不足，中止备份"
    exit 1
fi







# 打包备份
time=$(date "+%Y%m%d_%H%M%S") # 备份日期时间
base_name=$(basename "$source_dir")

FINAL_FILE="$target_dir/${base_name}_${time}.tar.gz" # 最终备份文件路径
TMPFILE=$(mktemp "${target_dir}/.backup_${base_name}.XXXXXX")

if ! tar -czf "$TMPFILE" -C "$(dirname "$source_dir")" "$base_name"; then
    log_error "打包失败"
    exit 1
fi

if [[ ! -s "$TMPFILE" ]]  || ! tar -tzf "$TMPFILE" >/dev/null 2>&1; then
    		log_error "错误：备份文件为空或备份文件损坏，请自行检查!"
            exit 1
fi

# 校验通过，原子改名
mv "$TMPFILE" "$FINAL_FILE"
TMPFILE=""

log_info "备份完成，路径：'$FINAL_FILE'，大小：$(du -h "$FINAL_FILE" | awk '{print $1}')"
            













	
	



