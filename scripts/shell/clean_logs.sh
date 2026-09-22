#!/bin/bash
set -euo pipefail

# ==================== 参数接收 ====================
if [ $# -ne 2 ]; then
    echo "用法: $0 <目录路径> <保留天数>"
    echo "示例: $0 /var/log 7"
    exit 1
fi

DIR="${1:-/var/log}"
DAYS="${2:-7}"

# ==================== 参数校验 ====================
# 1. 校验目录是否存在
if [ ! -d "$DIR" ]; then
    echo "错误: 目录 '${DIR}' 不存在或不是一个目录。"
    exit 1
fi

# 2. 校验天数是否为非负整数
if ! [[ "$DAYS" =~ ^[0-9]+$ ]]; then
    echo "错误: 保留天数 '${DAYS}' 必须是数字。"
    exit 1
fi

# ==================== 打印待删除文件 ====================
echo "===== 以下文件将被删除（${DAYS}天前）====="
# 加上 -type f 保证只找文件，-name "*.log" 过滤日志
find "$DIR" -type f -name "*.log" -mtime +"$DAYS" -print # -mtime n：按文件内容最后修改时间筛选，单位是“天”（24 小时）。
														 # +n：表示大于 n 天，即文件最后修改时间在 n 天之前。

# ==================== 交互式确认 ====================
echo "========================================"
read -r -p "确认删除以上文件吗？(y/N): " CONFIRM

if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "正在删除..."
    find "$DIR" -type f -name "*.log" -mtime +"$DAYS" -delete
    echo "清理完成。"
else
    echo "已取消删除操作。"
fi