# find
`find`是一个命令行工具，用于在文件系统中搜索文件。
`find`的语法如下：
`find [选项] [路径]`
`选项`表示搜索的条件。
`路径`表示要搜索的目录或文件目录。

--- 

`-mtime +7`：修改时间超过 7 天前（严格大于 7 天）
`-mtime -7`：最近 7 天内修改的
`-mtime 7`：恰好 7 天前修改的
``` bash
# 示例
find /var/log -type f -name "*.log" -mtime +"$DAYS" -print # 打印所有超过 $DAYS 天修改的日志文件

find /var/log -type f -name "*.log" -mtime -7 -delete # 删除最近 7 天内修改的日志文件
```
--- 