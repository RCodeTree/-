# Linux 运维 Shell 综合笔记

> 这份笔记用于汇总以下主题：Shell 基础、终端颜色、日志函数、`set`/`trap`/退出码、`getopts`、`read`、`grep`/`sed`/`awk`、`cut`、`tr`、`sort`、`uniq`、`find`、`tar`、`tee`、`hostname` 以及基础系统巡检。
>
> 目标不是覆盖所有细节，而是建立一套适合 Linux 运维与 SRE 实战的知识框架。

---

## 一、Shell 脚本基础

Shell 脚本的核心，是把命令、条件判断、循环和函数组织起来，完成自动化运维任务。

在实际工作里，Shell 脚本最常见的用途包括：

- 巡检：检查 CPU、内存、磁盘、端口、进程
- 备份与恢复：打包、解压、轮转旧文件
- 批量处理：对一批主机、目录、日志做统一操作
- 发布辅助：做参数校验、环境检查、结果汇总
- 应急排障：快速提取日志关键信息、统计异常请求、定位资源瓶颈

### 1.1 常见控制结构

#### `if`

```bash
if [ 条件 ]; then
    条件成立时执行
else
    条件不成立时执行
fi
```

#### `for`

```bash
for item in a b c; do
    echo "$item"
done
```

#### `while`

```bash
while [ 条件 ]; do
    循环体
done
```

#### `case`

`case` 在运维脚本里也非常常见，尤其适合处理菜单和参数分支。

```bash
case "$1" in
    start)
        echo "启动服务"
        ;;
    stop)
        echo "停止服务"
        ;;
    restart)
        echo "重启服务"
        ;;
    *)
        echo "用法：$0 {start|stop|restart}"
        exit 2
        ;;
esac
```

### 1.2 常用条件判断

#### 文件与目录

```bash
[ -e path ]   # 路径存在
[ -f file ]   # 普通文件存在
[ -d dir ]    # 目录存在
[ -r file ]   # 可读
[ -w file ]   # 可写
[ -x file ]   # 可执行
[ -s file ]   # 文件存在且非空
[ -L file ]   # 符号链接
```

#### 字符串与变量

```bash
[ -z "$var" ]        # 变量为空
[ -n "$var" ]        # 变量非空
[ "$a" = "$b" ]      # 字符串相等
[ "$a" != "$b" ]     # 字符串不相等
```

#### 数值比较

```bash
[ "$n" -eq 100 ]     # 等于
[ "$n" -ne 100 ]     # 不等于
[ "$n" -gt 100 ]     # 大于
[ "$n" -lt 100 ]     # 小于
[ "$n" -ge 100 ]     # 大于等于
[ "$n" -le 100 ]     # 小于等于
```

### 1.3 三种执行方式的区别

同一个脚本常见有三种运行方式：

```bash
./hello.sh
bash hello.sh
source hello.sh
```

它们的区别在于是否创建子进程、是否要求执行权限、是否影响当前终端环境。

| 方式 | 是否子进程 | 是否需要执行权限 | 是否影响当前 shell |
|---|---|---|---|
| `./hello.sh` | 是 | 是 | 否 |
| `bash hello.sh` | 是 | 否 | 否 |
| `source hello.sh` / `. hello.sh` | 否 | 否 | 是 |

`source` 最大的特点是会污染当前环境，所以只适合加载配置、函数库，不适合随便执行来源不明的脚本。

### 1.4 特殊变量

运维脚本中最常见的特殊变量有：

| 变量 | 含义 |
|---|---|
| `$0` | 脚本名 |
| `$1`~`$9` | 位置参数 |
| `$#` | 参数个数 |
| `$@` | 所有参数，逐个独立 |
| `$*` | 所有参数，合并处理 |
| `$?` | 上一条命令的退出码 |
| `$$` | 当前脚本 PID |

其中最重要的是：

- `$?`：判断上一步是否成功
- `$@`：遍历所有传入参数
- `$#`：检查用户是否传够参数

### 1.5 函数的基本写法

Shell 中函数用于封装重复逻辑。运维脚本里，日志输出、参数校验、配置读取、状态检查，通常都应该写成函数。

```bash
check_nginx() {
    if systemctl is-active --quiet nginx; then
        echo "nginx is running"
    else
        echo "nginx is not running"
        return 1
    fi
}
```

说明：

- `return` 返回的是函数退出码，不是文本
- 文本输出通常靠 `echo`
- 函数失败时应返回非 0，便于外层判断

例如：

```bash
if check_nginx; then
    echo "检查通过"
else
    echo "检查失败"
fi
```

---

## 二、脚本健壮性：`set`、`trap`、退出码与日志

运维脚本不是“能跑就行”，而是要追求可预测、可排错、可恢复。

### 2.1 `set` 的核心选项

最常用的是：

```bash
set -euo pipefail
```

含义如下：

- `set -e`：命令失败立即退出
- `set -u`：使用未定义变量时报错
- `set -o pipefail`：管道中任意一步失败，整体就失败

调试时还常加：

```bash
set -x
```

它会打印每一步执行的命令，便于排障。

实际工作里最常见的脚本开头通常是：

```bash
#!/bin/bash
set -euo pipefail
```

如果要临时调试某一段逻辑，可以局部打开：

```bash
set -x
# 需要调试的代码
set +x
```

### 2.2 `set -e` 的注意事项

`set -e` 很有用，但要理解它的行为边界。最常见的坑是：

```bash
grep "abc" file.txt
```

如果没有匹配到内容，`grep` 会返回非 0，在严格模式下可能让脚本提前退出。

因此更稳妥的写法通常是：

```bash
if grep -q "abc" file.txt; then
    echo "找到了"
fi
```

类似地，下面这种写法在严格模式下也要小心：

```bash
count=$(grep -c "ERROR" app.log)
```

更稳妥的方式是结合条件判断，或者提前明确允许失败的命令返回值。

### 2.3 `trap`：脚本清理与优雅退出

### 2.3 `trap`：脚本清理与优雅退出

`trap` 用于在收到信号或脚本退出时执行指定动作，最常用场景是清理临时文件。

```bash
tmpfile=$(mktemp)

cleanup() {
    rm -f "$tmpfile"
}

trap cleanup EXIT
```

常见信号：

- `INT`：`Ctrl+C`
- `TERM`：优雅终止
- `EXIT`：脚本退出时触发
- `ERR`：命令失败时触发

例如：

```bash
trap 'echo "捕获到 Ctrl+C"; exit 130' INT
trap 'echo "收到终止信号"; exit 143' TERM
```

更完整一点的写法通常是：

```bash
#!/bin/bash
set -euo pipefail

tmpfile=$(mktemp)

cleanup() {
    local status=$?
    rm -f "$tmpfile"
    exit "$status"
}

trap cleanup EXIT
trap 'echo "收到中断信号" >&2; exit 130' INT
trap 'echo "收到终止信号" >&2; exit 143' TERM
```

这种写法适合：

- 生成临时文件
- 加文件锁
- 下载中间文件
- 执行过程中需要保证退出时清理现场

### 2.4 退出码约定

Shell 中：

- `0` 表示成功
- 非 `0` 表示失败

运维脚本推荐建立统一规范，例如：

- `0`：执行成功 / 服务健康
- `1`：逻辑失败 / 检查异常
- `2`：参数错误 / 用法错误

示例：

```bash
if [ "$#" -lt 1 ]; then
    echo "用法错误"
    exit 2
fi
```

### 2.5 日志函数

日志函数可以让脚本输出更清晰，也更适合排障。

```bash
log_info()  { echo -e "\033[32m[INFO]  $(date '+%F %T') $*\033[0m"; }
log_warn()  { echo -e "\033[33m[WARN]  $(date '+%F %T') $*\033[0m"; }
log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m" >&2; }
```

建议约定：

- `[INFO]`：流程信息
- `[WARN]`：非致命风险
- `[ERROR]`：实际失败

一个稍完整的日志模板如下：

```bash
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]  $(date '+%F %T') $*${RESET}"; }
log_warn()  { echo -e "${YELLOW}[WARN]  $(date '+%F %T') $*${RESET}"; }
log_error() { echo -e "${RED}[ERROR] $(date '+%F %T') $*${RESET}" >&2; }
```

使用示例：

```bash
log_info "开始检查 nginx"

if systemctl is-active --quiet nginx; then
    log_info "nginx 运行正常"
else
    log_error "nginx 未运行"
fi
```

---

## 三、终端颜色与 ANSI Escape Code

Shell 中的彩色输出，本质上依赖 ANSI 转义序列。

最常见写法：

```bash
echo -e "\033[32mSUCCESS\033[0m"
```

其中：

- `\033`：ESC 字符
- `[32m`：设置绿色前景色
- `\033[0m`：恢复默认样式

### 3.1 最常用颜色

| 代码 | 颜色 | 用途 |
|---:|---|---|
| `31` | 红色 | 错误、失败 |
| `32` | 绿色 | 成功、正常 |
| `33` | 黄色 | 警告 |
| `34` | 蓝色 | 普通提示 |
| `36` | 青色 | 调试、标题 |
| `0` | 重置 | 恢复默认 |

### 3.2 常见样式

| 代码 | 效果 |
|---:|---|
| `1` | 粗体 |
| `4` | 下划线 |
| `7` | 反色 |

组合示例：

```bash
echo -e "\033[1;31mERROR\033[0m"
```

表示粗体红色。

### 3.3 推荐做法：定义变量

```bash
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
RESET='\033[0m'
```

然后：

```bash
echo -e "${GREEN}成功${RESET}"
```

这比把颜色码写死在每一行里更易维护。

### 3.4 背景色与组合样式

除了前景色，还有背景色：

| 代码 | 背景颜色 |
|---:|---|
| `41` | 红色背景 |
| `42` | 绿色背景 |
| `43` | 黄色背景 |
| `44` | 蓝色背景 |

例如：

```bash
echo -e "\033[41m ERROR \033[0m"
```

不过在运维脚本里，背景色使用频率不高，通常前景色已经足够。

### 3.5 `echo -e` 与 `printf`

很多示例会用：

```bash
echo -e "\033[32mOK\033[0m"
```

但在更讲究可移植性的脚本里，也经常使用：

```bash
printf "\033[32m%s\033[0m\n" "OK"
```

`printf` 的优点是格式更稳定，尤其适合脚本中有变量拼接的场景。

---

## 四、命令行参数处理：`getopts`

当脚本需要支持 `-h`、`-v`、`-d /path` 这类参数时，应该用 `getopts`。

### 4.1 基本结构

```bash
while getopts ":a:b:vh" opt; do
    case "$opt" in
        a) value_a="$OPTARG" ;;
        b) value_b="$OPTARG" ;;
        v) verbose=1 ;;
        h)
            echo "用法：$0 [-a value] [-b value] [-v] [-h]"
            exit 0
            ;;
        \?)
            echo "错误：未知选项 -$OPTARG"
            exit 1
            ;;
        :)
            echo "错误：选项 -$OPTARG 缺少参数"
            exit 1
            ;;
    esac
done

shift $((OPTIND - 1))
```

### 4.2 重点概念

- `a:`：`-a` 后必须跟参数
- `v`：`-v` 是开关，不带参数
- `OPTARG`：当前选项对应的值
- `OPTIND`：下一个待解析参数的位置
- `shift $((OPTIND - 1))`：移除已解析选项，保留剩余普通参数

### 4.3 前置冒号的意义

```bash
getopts ":a:b:vh" opt
```

前面的 `:` 表示让脚本自己处理错误，而不是让 Shell 直接报错。这样更适合写出统一、友好的错误输出。

### 4.4 实际工作中的高频参数设计

运维脚本常见的参数设计有：

- `-h`：帮助
- `-v`：详细模式
- `-d`：演练模式 / 目标目录
- `-c`：配置文件路径
- `-t`：超时时间
- `-n`：名称、次数或阈值

例如一个巡检脚本：

```bash
#!/bin/bash

set -euo pipefail

config_file=""
verbose=0
timeout=3

while getopts ":c:t:vh" opt; do
    case "$opt" in
        c) config_file="$OPTARG" ;;
        t) timeout="$OPTARG" ;;
        v) verbose=1 ;;
        h)
            echo "用法：$0 [-c config] [-t timeout] [-v] [-h]"
            exit 0
            ;;
        \?)
            echo "错误：未知选项 -$OPTARG" >&2
            exit 2
            ;;
        :)
            echo "错误：选项 -$OPTARG 缺少参数" >&2
            exit 2
            ;;
    esac
done

shift $((OPTIND - 1))
```

这样设计后，脚本就比直接依赖 `$1`、`$2` 更易读，也更适合长期维护。

---

## 五、用户输入与逐行读取：`read`

`read` 是 Bash 内建命令，用来从标准输入读取内容。

### 5.1 最基础的读取

```bash
read name
echo "$name"
```

### 5.2 常用选项

| 选项 | 作用 |
|---|---|
| `-p` | 显示提示语 |
| `-s` | 静默输入，常用于密码 |
| `-r` | 不把反斜杠当转义 |
| `-t` | 超时 |
| `-n` | 读取固定字符数 |
| `-a` | 读入数组 |

例如：

```bash
read -p "请输入主机名: " host
read -s -p "请输入密码: " passwd
echo
```

再补几个工作里很常见的例子：

#### 超时输入

```bash
if read -t 5 -p "是否继续？(y/N) " ans; then
    echo "你输入的是：$ans"
else
    echo "超时，默认不继续"
fi
```

#### 读入数组

```bash
read -a services <<< "nginx mysql redis"
echo "${services[0]}"
```

#### 按任意键继续

```bash
read -n 1 -s -p "按任意键继续..."
echo
```

### 5.3 `while read`：逐行处理文件的标准姿势

```bash
while IFS= read -r line; do
    echo "处理行: $line"
done < /etc/hosts
```

这里的关键点是：

- `IFS=`：保留行首尾空白
- `-r`：保留反斜杠
- `< file`：从文件读，不是从键盘读

### 5.4 常见坑点

#### 管道子 shell 问题

```bash
echo -e "1\n2\n3" | while read -r n; do
    sum=$((sum + n))
done
echo "$sum"
```

这种写法里，`while` 循环常运行在子 shell 中，循环结束后变量可能丢失。

更稳妥的是：

```bash
while read -r n; do
    sum=$((sum + n))
done < <(printf '1\n2\n3\n')
```

#### 文件最后一行无换行

如果要严谨处理最后一行，可以写成：

```bash
while IFS= read -r line || [ -n "$line" ]; do
    echo "$line"
done < file
```

### 5.5 运维中的典型用途

- 破坏性操作前人工确认
- 逐行读取配置
- 菜单选择
- 密码输入

例如：

```bash
read -p "确认删除？输入 YES 才继续: " confirm
if [ "$confirm" = "YES" ]; then
    echo "开始执行"
fi
```

更实际一点的例子是：

```bash
read -p "⚠️ 确认删除旧备份目录 ${target_dir} ? 输入 YES 继续: " confirm
if [ "$confirm" != "YES" ]; then
    echo "已取消"
    exit 1
fi
```

这类交互非常适合用于：

- 删除旧备份
- 清理日志
- 执行覆盖式恢复
- 批量停止服务

---

## 六、文本处理三剑客：`grep`、`sed`、`awk`

这三者是 Shell 文本处理的核心。

- `grep`：筛选行
- `sed`：按行编辑
- `awk`：按字段处理

### 6.1 `grep`：搜索与过滤

基本语法：

```bash
grep [选项] "模式" 文件
```

常用选项：

| 选项 | 作用 |
|---|---|
| `-i` | 忽略大小写 |
| `-v` | 反向匹配 |
| `-n` | 显示行号 |
| `-c` | 统计匹配行数 |
| `-o` | 只输出匹配部分 |
| `-w` | 整词匹配 |
| `-r` | 递归搜索 |
| `-E` | 扩展正则 |
| `-q` | 静默模式，不输出匹配行 |
| `-A N` | 显示匹配行后 N 行 |
| `-B N` | 显示匹配行前 N 行 |
| `-C N` | 显示匹配行前后各 N 行 |

常用正则：

```bash
^   # 行首
$   # 行尾
.   # 任意单字符
*   # 前一个字符重复 0 次或多次
[]  # 字符集合
```

示例：

```bash
grep -n "Error" app.log
grep -v "DEBUG" app.log
grep -E "500|403" access.log
```

高频工作例子：

```bash
grep -rn "listen 80" /etc/nginx/
grep -C 3 "ERROR" app.log
grep -o "[0-9]\{1,3\}\(\.[0-9]\{1,3\}\)\{3\}" access.log
```

说明：

- `-r`：递归查配置目录
- `-n`：显示行号，便于定位
- `-C 3`：排障时连上下文一起看
- `-o`：只提取匹配片段

### 6.2 `sed`：替换、删除、打印

基本语法：

```bash
sed [选项] '动作' 文件
```

最常用操作是替换：

```bash
sed 's/apple/orange/' file.txt
sed 's/apple/orange/g' file.txt
```

区别是：

- 不带 `g`：每行只替换第一个
- 带 `g`：每行全部替换

其他常见操作：

```bash
sed '1d' file.txt           # 删除第一行
sed '2,4d' file.txt         # 删除 2 到 4 行
sed -n '1,3p' file.txt      # 只打印 1 到 3 行
sed '/POST/d' access.log    # 删除包含 POST 的行
```

追加和插入也很常见：

```bash
sed '1i # generated by script' file.txt
sed '$a # end' file.txt
```

多重替换：

```bash
sed -e 's/apple/A/g' -e 's/dog/DOG/g' samples.txt
```

修改原文件时用：

```bash
sed -i 's/old/new/g' file.txt
```

但 `-i` 会直接改原文件，生产环境要慎用。

实战例子：

```bash
sed -n '/ERROR/p' app.log
sed '/^#/d' app.conf
sed '/^$/d' app.conf
```

这三类操作在清洗配置文件和日志时很常用：

- 只打印错误行
- 删除注释行
- 删除空行

### 6.3 `awk`：按列处理

`awk` 默认按空白分列，非常适合日志、表格和结构化文本。

常见内置变量：

| 变量 | 含义 |
|---|---|
| `$0` | 整行 |
| `$1` | 第 1 列 |
| `$NF` | 最后一列 |
| `NF` | 当前行字段数 |
| `NR` | 当前行号 |

基本语法：

```bash
awk '条件 {动作}' 文件
```

示例：

```bash
awk '{print $1}' access.log
awk '$NF == 200 {print $0}' access.log
awk -F: '{print $2, $4}' employees.txt
awk 'NR > 1 {sum += $3} END {print sum}' sales.txt
```

工作里常见写法还包括：

```bash
awk '{print NR, $0}' app.log
awk '$1 ~ /^192\.168\./ {print $0}' access.log
awk 'NR > 1 {sum += $NF} END {print sum}' metrics.txt
awk -F: '$3 >= 1000 {print $1, $3}' /etc/passwd
```

这类用法常用于：

- 给日志加行号
- 过滤某网段访问
- 对数值字段求和
- 从结构化文件里抽列并筛选

### 6.4 `awk` 中的两个重要点

#### 数值转换

```bash
+$5
```

等价于 `$5 + 0`，表示强制按数字处理。

#### 正则匹配

在 `awk` 中用的是：

```bash
$1 ~ /abc/
$1 !~ /abc/
```

不是 Bash 里的 `=~`。

### 6.5 三剑客的分工建议

实际排障时，可以这么理解：

- 只是找有没有某个关键词：优先 `grep`
- 只是替换、删行、插行：优先 `sed`
- 涉及列、条件、统计、累加：优先 `awk`

例如分析访问日志：

```bash
grep " 500 " access.log | awk '{print $1, $7}' | sort | uniq -c | sort -nr
```

这是一个很典型的生产分析链路：

1. `grep` 先过滤 500 错误
2. `awk` 抽取 IP 和路径
3. `sort` 排序
4. `uniq -c` 计数
5. `sort -nr` 看 Top

---

## 七、按字段和字符处理：`cut` 与 `tr`

### 7.1 `cut`：简单截取

`cut` 适合做简单、固定分隔符的字段提取。

三种模式：

- `-b`：按字节
- `-c`：按字符
- `-f`：按字段

示例：

```bash
cut -d: -f1 /etc/passwd
cut -d: -f1,3 /etc/passwd
cut -c1-10 file.txt
```

常用选项：

- `-d`：指定分隔符
- `-f`：取字段
- `-s`：只输出包含分隔符的行
- `--complement`：反选
- `--output-delimiter`：自定义输出分隔符

注意：`cut` 不适合处理分隔不稳定、多个空格对齐的文本，那种场景更适合 `awk`。

实战例子：

```bash
cut -d: -f1,3 /etc/passwd
cut -d, -f2 sales.csv
cut -c1-20 app.log
```

对应场景：

- 取用户名和 UID
- 取 CSV 的某一列
- 截取日志前 20 个字符快速预览

### 7.2 `tr`：字符级替换、删除、压缩

`tr` 是字符级工具，只读标准输入，只写标准输出。

常见能力：

- 替换字符
- 删除字符
- 压缩连续重复字符

示例：

```bash
echo 'Hello' | tr 'a-z' 'A-Z'
echo 'a1b2c3' | tr -d '[:digit:]'
echo 'a     b' | tr -s ' '
tr -d '\r' < dos.txt > unix.txt
```

只保留数字：

```bash
echo 'a1b2c3' | tr -cd '[:digit:]'
```

常见注意点：

- `tr` 不直接接收文件名，要配合重定向或管道
- `tr` 不支持正则
- 更适合 ASCII / 单字节字符处理

再补几个很常见的例子：

```bash
echo 'A B   C' | tr -s ' '
tr -cd '0-9\n' < file.txt
echo 'a,b,c' | tr ',' '\n'
```

这些对应的实战目的分别是：

- 压缩连续空格
- 只保留数字和换行
- 把逗号分隔转成逐行输出

---

## 八、排序与去重：`sort`、`uniq`

### 8.1 `sort`

`sort` 的核心是对文本行排序。

常用选项：

| 选项 | 作用 |
|---|---|
| `-n` | 数值排序 |
| `-r` | 倒序 |
| `-h` | 人类可读数值排序 |
| `-u` | 排序并去重 |
| `-t` | 指定分隔符 |
| `-k` | 指定按哪一列排序 |
| `-o` | 输出到文件 |
| `-c` | 检查文件是否已排序 |

示例：

```bash
sort file.txt
sort -n numbers.txt
sort -t ':' -k3,3n /etc/passwd
du -sh /var/* | sort -rh
```

工作里常见的排序需求：

```bash
sort -u users.txt
sort -nr cpu_top.txt
LC_ALL=C sort file.txt
```

说明：

- `sort -u`：排序并去重
- `sort -nr`：按数值倒序
- `LC_ALL=C sort`：强制按 ASCII 排序，结果更稳定

重要坑点：

```bash
sort file > file
```

这种写法会先把文件清空。原地排序要用：

```bash
sort file -o file
```

### 8.2 `uniq`

`uniq` 只能去除连续重复行，因此通常要先配合 `sort`。

常用选项：

| 选项 | 作用 |
|---|---|
| `-c` | 统计重复次数 |
| `-d` | 只显示有重复的行 |
| `-D` | 显示所有重复副本 |
| `-u` | 只显示唯一行 |
| `-i` | 忽略大小写 |

示例：

```bash
sort demo.txt | uniq
sort demo.txt | uniq -c
sort demo.txt | uniq -d
sort demo.txt | uniq -u
```

再补两个常见例子：

```bash
awk '{print $1}' access.log | sort | uniq -d
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -10
```

分别表示：

- 找出出现过重复的 IP
- 统计访问次数最高的前 10 个 IP

### 8.3 `sort` 与 `uniq` 的经典组合

统计访问量最高的 IP：

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
```

这个流水线非常适合 SRE 面试和日志分析。

---

## 九、查找文件：`find`

`find` 用于在文件系统中按条件搜索文件。

基本语法：

```bash
find [路径] [条件]
```

示例：

```bash
find /var/log -type f -name "*.log"
find /var/log -type f -name "*.log" -mtime +7
find /var/log -type f -name "*.log" -mtime -7
```

高频参数还包括：

| 参数 | 含义 |
|---|---|
| `-type f` | 普通文件 |
| `-type d` | 目录 |
| `-name` | 按名称匹配 |
| `-mtime` | 按修改时间 |
| `-size` | 按文件大小 |
| `-maxdepth` | 限制搜索深度 |
| `-delete` | 直接删除匹配文件 |
| `-print` | 打印结果 |

### 9.1 时间条件

- `-mtime +7`：超过 7 天前修改
- `-mtime -7`：最近 7 天内修改
- `-mtime 7`：恰好 7 天前修改

### 9.2 深度控制

```bash
find "$target_dir" -maxdepth 1 -type f
```

`-maxdepth 1` 表示只查当前目录，不递归进入子目录。

### 9.3 大小与删除

查找大文件：

```bash
find /var/log -type f -size +100M -print
```

查找并删除 7 天前的日志：

```bash
find /var/log -type f -name "*.log" -mtime +7 -delete
```

注意：`-delete` 属于修改性操作，生产环境建议先用 `-print` 预览，再决定是否删除。

### 9.4 自定义输出

GNU `find` 常见写法：

```bash
find . -type f -printf '%T@ %p\n'
```

含义：

- `%T@`：修改时间时间戳
- `%p`：文件路径

很适合后续接 `sort -n` 做按时间排序。

例如找出某目录下最新的备份文件：

```bash
find /backup -maxdepth 1 -type f -name "*.tar.gz" -printf '%T@ %p\n' | sort -n | tail -1
```

---

## 十、归档与压缩：`tar`

`tar` 本质上是归档工具，常和 `gzip`、`bzip2`、`xz`、`zstd` 一起使用。

### 10.1 最核心的参数

| 参数 | 含义 |
|---|---|
| `-c` | 创建归档 |
| `-x` | 解包 |
| `-t` | 查看内容 |
| `-v` | 显示过程 |
| `-f` | 指定归档文件 |
| `-z` | gzip |
| `-j` | bzip2 |
| `-J` | xz |
| `-C` | 指定目录 |
| `--exclude` | 排除文件 |

### 10.2 最常用的命令

```bash
tar -cf backup.tar project/
tar -xf backup.tar
tar -tf backup.tar

tar -czf backup.tar.gz project/
tar -xzf backup.tar.gz
tar -tzf backup.tar.gz
```

其他压缩格式也很常见：

```bash
tar -cjf backup.tar.bz2 project/
tar -xjf backup.tar.bz2

tar -cJf backup.tar.xz project/
tar -xJf backup.tar.xz
```

### 10.3 常见实战场景

#### 解压到指定目录

```bash
tar -xzf backup.tar.gz -C /tmp/
```

#### 只查看内容

```bash
tar -tzf backup.tar.gz
```

#### 排除文件

```bash
tar -czf backup.tar.gz project/ --exclude='*.log'
```

#### 只解压指定文件

```bash
tar -xzf backup.tar.gz project/config/app.conf
```

#### 显示详细过程

```bash
tar -czvf backup.tar.gz project/
```

### 10.4 运维中的两个要点

- 拿到陌生压缩包时，先 `tar -tf` 或 `tar -tzf` 查看内容
- 使用 `-C` 可以控制归档内部路径或解压目标位置

实战建议：

- 备份前先确认打包目录是否正确
- 恢复前先 `tar -tf` 看内部路径，避免解压到错误位置
- 大多数日常场景，优先记住 `-czf`、`-xzf`、`-tzf`

---

## 十一、输出分流与落盘：`tee`

`tee` 的作用是把标准输入同时输出到屏幕和文件。

```bash
command | tee file.log
```

追加写入：

```bash
command | tee -a file.log
```

常用选项还有：

- `-a`：追加
- `-i`：忽略中断信号

### 11.1 与重定向的区别

```bash
echo "hello" > test.txt
```

只写文件，不显示到屏幕。

```bash
echo "hello" | tee test.txt
```

既显示到屏幕，也写入文件。

### 11.2 常见用途

- 记录脚本执行输出
- 保留巡检日志
- 调试时边看边存

例如：

```bash
df -h | tee disk.log
./healthcheck.sh | tee -a healthcheck.log
```

一个典型巡检日志收集例子：

```bash
{
    echo "===== $(date '+%F %T') ====="
    uptime
    free -m
    df -h
    ss -s
} | tee -a system_check.log
```

---

## 十二、主机名与主机信息：`hostname`

`hostname` 用于查看当前系统主机名、域名和 IP 信息。

### 12.1 常用命令

```bash
hostname
hostname -s
hostname -f
hostname -I
hostname -i
```

含义：

- `hostname`：当前主机名
- `-s`：短主机名
- `-f`：FQDN
- `-I`：所有非回环 IP
- `-i`：主机名解析出的 IP

补充几个常见选项：

| 选项 | 含义 |
|---|---|
| `-d` | 显示域名 |
| `-A` | 显示所有 FQDN |
| `-s` | 显示短主机名 |
| `-f` | 显示完整域名 |

### 12.2 修改主机名

临时修改：

```bash
sudo hostname web01
```

永久修改更推荐：

```bash
sudo hostnamectl set-hostname web01
```

如果系统使用 systemd，优先选择 `hostnamectl`。

排障时常用组合：

```bash
hostname
hostname -I
cat /etc/hostname
```

这样可以快速确认：

- 当前系统内核主机名
- 当前主机 IP
- 静态主机名配置

---

## 十三、系统基础巡检指标

运维入门阶段，最先要养成的不是“拍脑袋猜故障”，而是先看系统基本面。

### 13.1 CPU：看负载

```bash
nproc
uptime
```

重点关注 `load average`：

- 1 分钟
- 5 分钟
- 15 分钟

经验判断：

- 负载长期高于 CPU 核心数，说明系统过载
- 单核机器持续高于 1，4 核机器持续高于 4，需要警惕

### 13.2 内存：看 `available`

```bash
free -m
```

不要只盯着 `free`，更要看：

```text
available
```

因为 Linux 会把空闲内存用于缓存。真正可继续分配给新进程的内存，更接近 `available`。

### 13.3 磁盘：空间与 inode 都要看

```bash
df -h
df -i
```

很多“磁盘已满”并不是空间没了，而是 inode 被耗尽了。

### 13.4 网络：IP、监听端口、连接数

```bash
hostname -I
ss -tlnp
ss -s
```

这三条命令能帮助你快速确认：

- 本机 IP 是什么
- 有哪些 TCP 监听端口
- 当前连接数是否异常

### 13.5 常用巡检命令补充

虽然这一节主要来自系统基础巡检笔记，但在实际工作中，下面这些命令也常常和前面的基础命令一起使用：

```bash
top
ps aux
systemctl status nginx
journalctl -u nginx --since "10 minutes ago"
```

它们分别适合：

- `top`：看实时资源占用
- `ps aux`：看进程列表
- `systemctl status`：看服务状态
- `journalctl`：看服务日志

---

## 十四、这些命令在运维中的组合思路

单独记命令不够，关键是知道如何把它们组合起来。

### 14.1 日志排障

```bash
grep -E "500|403" access.log | awk '{print $1, $7, $(NF-1)}'
```

先用 `grep` 过滤异常状态码，再用 `awk` 提取关键字段。

如果想带上下文一起看，可以先：

```bash
grep -C 2 "ERROR" app.log
```

### 14.2 统计热点访问来源

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
```

这是典型的“提取 -> 排序 -> 计数 -> 再排序”思路。

### 14.3 巡检输出保存

```bash
{
    date
    uptime
    free -m
    df -h
} | tee system_check.log
```

### 14.4 批量读配置并执行检查

```bash
while IFS= read -r line; do
    grep -q "enabled" <<< "$line" && echo "$line"
done < app.conf
```

如果配置文件是 `key=value` 形式，更常见的写法是：

```bash
while IFS='=' read -r key value; do
    [ -z "$key" ] && continue
    case "$key" in
        \#*) continue ;;
    esac
    echo "配置项: $key = $value"
done < app.conf
```

### 14.5 查找旧日志并归档

```bash
find /var/log -type f -name "*.log" -mtime +7 | tee old_logs.txt
tar -czf old_logs.tar.gz -T old_logs.txt
```

### 14.6 配置搜索与批量替换

查配置：

```bash
grep -rn "server_name" /etc/nginx/
```

预览替换效果：

```bash
sed 's/old.example.com/new.example.com/g' nginx.conf
```

### 14.7 统计错误请求 Top IP

```bash
grep " 500 " access.log | awk '{print $1}' | sort | uniq -c | sort -nr | head
```

### 14.8 提取并检查监听端口

```bash
ss -tlnp | grep -E "80|443|3306"
```

这个组合常用于：

- 检查 Web 服务是否监听
- 检查数据库是否误暴露
- 发布后快速确认端口状态

---

## 十五、学习优先级建议

如果你的目标是 Linux 运维 / DevOps / SRE，建议按照下面顺序掌握：

1. Shell 基础语法：变量、判断、循环、函数
2. 特殊变量与退出码：`$?`、`$#`、`$@`
3. 脚本健壮性：`set -euo pipefail`
4. 参数与输入：`getopts`、`read`
5. 文本处理：`grep`、`sed`、`awk`
6. 基础辅助工具：`cut`、`tr`、`sort`、`uniq`
7. 文件处理：`find`、`tar`、`tee`
8. 终端增强：颜色输出、日志函数
9. 系统巡检：CPU、内存、磁盘、网络

---

## 十六、一句话总览

这套知识可以概括为下面这条链路：

```text
Shell 基础
    ↓
健壮性控制（set / trap / 退出码）
    ↓
参数与输入（getopts / read）
    ↓
文本处理（grep / sed / awk / cut / tr / sort / uniq）
    ↓
文件处理（find / tar / tee）
    ↓
终端展示（ANSI 颜色 / 日志函数）
    ↓
系统巡检（CPU / 内存 / 磁盘 / 网络）
```

如果把这些内容真正串起来，你就已经具备了编写日常运维 Shell 脚本和做基础故障排查的核心骨架。
