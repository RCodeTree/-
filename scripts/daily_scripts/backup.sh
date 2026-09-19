#!/bin/bash

# 使用 set 防止脚本错误运行下去
set -euo pipefail

# 日志函数
log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m"; }
log_info() { echo -e "\033[32m[INFO] $(date '+%F %T') $*\033[0m"; }
log_warn() { echo -e "\033[33m[WARN] $(date '+%F %T') $*\033[0m"; }

# 清理函数
clean_up() {
	log_error "错误：数据备份失败，正在清理备份失败数据....!"
    # rm -rf /tmp/backupdir/* # TODO
    exit 1
}



# 源目录、备份目录
source_dir=$1
target_dir=$2

# 校验源目录是否存在
log_info "正在校验源目录有效性" 
if [[ ! -d "$source_dir"  ]]; then
	log_error "错误：${source_dir} 源目录不存在或 ${source_dir} 不是一个目录!" 
	log_error "用法：./backup.sh <源目录> <备份目录>" 
    log_error "示例：./backup.sh /var/html /backupdir" 
    exit 1

# 校验源目录是否可读可写
if [[ ! -r "$source_dir" || ! -x "$source_dir"  ]]; then
	log_error "错误：${source_dir} 源目录不可读!" 
    exit 1
fi

# 校验备份目录是否存在
log_info "正在校验备份目录有效性" 
if [[ ! -d "$target_dir"  ]]; then
	log_error "错误：${target_dir} 备份目录不存在或 ${target_dir} 不是一个目录!" 
    log_warn "警告：备份目录 ${target_dir} 正在创建目录......" 
    if ! mkdir -p $target_dir; then
    	log_error "错误：备份目录创建失败!" 
    	exit 1
    fi
fi

# 打包备份
time=$(date "+%Y%m%d_%H%M%S") # 备份日期时间
base_name=$(basename "$source_dir")

trap clean_up EXIT INT TERM
if tar -czf  /tmp/demo/* /tmp/backupdir/"${base_name}.tar.gz"; then # 备份文件并校验
    log_info "正在备份文件......"
	# mv /tmp/backupdir/"${base_name}.tar.gz" /backupdir/"${base_name}_${time}.tat.gz"
else
    log_error "错误：打包备份文件失败！"
    exit 1
fi

if [[ ! -s /tmp/backupdir/"${base_name}.tar.gz" ]]  || ! tar -tzf /tmp/backupdir/"${base_name}.tar.gz" >/dev/null 2>&1; then
    		log_error "错误：备份文件为空或备份文件损坏，请自行检查!"
            du -h /tmp/backupdir/"${base_name}.tar.gz"
            exit 1
fi

log_info "备份完成，路径：/backupdir/'${base_name}_${time}.tat.gz'，大小：$(du -h backup.sh | awk '{print $1}')"
            













	
	



