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
    rm -rf /tmp/backupdir/*
    exit 1
}


# 脚本临时日志文件
tmp_log_file=$(mktemp -p /tmp/backup_log)

# 源目录、备份目录
source_dir=$1
target_dir=$2

# 校验目录是否存在
log_info "正在校验目录有效性" >> "$tmp_log_file"
if [[ !( -d $source_dir ) ]]; then
	log_error "错误：${source_dir} 源目录不存在或 ${source_dir} 不是一个目录!" >> "$tmp_log_file"
	log_error "用法：./backup.sh <源目录> <备份目录>" >> "$tmp_log_file"
    log_error "示例：./backup.sh /var/html /backupdir" >> "$tmp_log_file"
    exit 1
    if [[ !( -r $source_dir && -x $source_dir ) ]]; then
    	log_error "错误：${source_dir} 目录不可读!" >> "$tmp_log_file"
        exit 1
    fi
elif [[ !( -d $target_dir ) ]]; then
	log_error "错误：${target_dir} 目录不存在或 ${target_dir} 不是一个目录!" >> "$tmp_log_file"
    log_warn "警告：备份目录 ${target_dir} 正在创建目录......" >> "$tmp_log_file"
    mkdir -p /backupdir
    if [ $? ]; then
    	log_error "错误：备份目录创建失败!" >> "$tmp_log_file"
    	exit $?
    fi
fi

# 打包备份
time=$(date "+%Y-%m-%d_%H:%M:%S") # 备份日期时间
basename="backupdir"

if [[ tar -czf  /tmp/demo/* /tmp/backupdir/"${basename}.tar.gz" ]]; then # 备份文件并校验
    trap clean_up EXIT INT TREM
else
	log_info "正在备份文件......"
	mv /tmp/backupdir/"${basename}.tar.gz" /backupdir/"${basename}_${time}.tat.gz"
fi

if [[ !( -s /tmp/backupdir/"${basename}.tar.gz" ) || !( tar -tzf /tmp/backupdir/"${basename}.tar.gz" ) ]]; then
    		log_error "错误：备份文件为空或备份文件损坏，请自行检查!"
            du -h /tmp/backupdir/"${basename}.tar.gz"
            exit 1
fi

log_info "备份完成，路径：/backupdir/'${basename}_${time}.tat.gz'，大小：${du -h backup.sh | awk '{print $1}'}"
            













	
	



