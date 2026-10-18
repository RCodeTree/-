# Linux 运维 Shell：终端颜色与 ANSI Escape Code 学习笔记

> 目标：掌握 Shell 运维脚本中常见的终端颜色、文字样式和 ANSI 转义序列。
>
> 学习原则：**够用即可，不需要深入 ANSI 标准。**

---

## 一、什么是 ANSI Escape Code？

在 Linux 终端中，我们可以通过一些特殊字符控制终端的显示效果。

例如：

```bash
echo -e "\033[32mHello\033[0m"
```

运行后，`Hello` 会显示为绿色。

这里：

```text
\033[32m
```

表示：

> 从这里开始使用绿色文字。

而：

```text
\033[0m
```

表示：

> 恢复终端默认样式。

因此可以简单理解为：

```text
开始设置样式
      ↓
\033[32m
      ↓
  要显示的文字
      ↓
\033[0m
      ↓
恢复默认
```

---

# 二、为什么运维脚本经常使用颜色？

在运维工作中，经常需要执行：

```bash
systemctl status nginx
journalctl
df -h
free -h
docker ps
```

或者自己编写大量 Shell 脚本。

如果所有输出都是白色：

```text
[INFO] 开始检查 nginx
[INFO] nginx 正常
[WARN] 磁盘空间不足
[ERROR] nginx 启动失败
```

大量日志混在一起时，不容易快速发现问题。

使用颜色后：

```text
绿色  [INFO] nginx 正常
黄色  [WARN] 磁盘空间不足
红色  [ERROR] nginx 启动失败
```

可以快速区分：

- 正常
- 警告
- 错误
- 调试信息

因此颜色输出是 Shell 运维脚本中非常常见的小技巧。

---

# 三、最重要的颜色代码

## 3.1 前景色（文字颜色）

最常用的是：

| 代码 | 颜色 | 常见用途 |
|---:|---|---|
| `30` | 黑色 | 很少使用 |
| `31` | 红色 | ERROR、失败 |
| `32` | 绿色 | SUCCESS、正常 |
| `33` | 黄色 | WARN、警告 |
| `34` | 蓝色 | 普通提示、信息 |
| `35` | 紫色 | 特殊信息 |
| `36` | 青色 | DEBUG、标题 |
| `37` | 白色 | 普通文字 |

最值得记住：

```text
31 红色
32 绿色
33 黄色
34 蓝色
35 紫色
36 青色
```

---

# 四、最基本的使用方式

通用格式：

```bash
echo -e "\033[颜色代码m文字\033[0m"
```

例如：

## 红色

```bash
echo -e "\033[31mERROR\033[0m"
```

## 绿色

```bash
echo -e "\033[32mSUCCESS\033[0m"
```

## 黄色

```bash
echo -e "\033[33mWARNING\033[0m"
```

## 蓝色

```bash
echo -e "\033[34mINFO\033[0m"
```

## 青色

```bash
echo -e "\033[36mDEBUG\033[0m"
```

---

# 五、`\033` 是什么？

这是理解 ANSI 转义序列的关键。

```bash
\033
```

表示 ASCII 中的 ESC（Escape）字符。

它告诉终端：

> 后面可能是一条终端控制指令，请按照控制指令处理。

所以：

```bash
\033[32m
```

可以拆成：

```text
\033
 ↓
ESC

[
 ↓
控制序列开始

32
 ↓
绿色

m
 ↓
应用这个设置
```

实际学习过程中不需要深入 ASCII 标准，记住：

```bash
\033[32m
```

就是：

> 开始绿色文字。

---

# 六、为什么最后一定要 `\033[0m`？

例如：

```bash
echo -e "\033[31mERROR"
echo "这是一条普通信息"
```

可能会导致后面的内容继续保持红色。

所以应该写：

```bash
echo -e "\033[31mERROR\033[0m"
echo "这是一条普通信息"
```

其中：

```bash
\033[0m
```

就是：

> 重置所有终端显示属性。

因此养成习惯：

```text
设置颜色
↓
输出内容
↓
恢复默认
```

即：

```bash
\033[31m内容\033[0m
```

---

# 七、文字样式

除了颜色，还可以设置文字样式。

最常用：

| 代码 | 效果 |
|---:|---|
| `0` | 重置 |
| `1` | 粗体 |
| `4` | 下划线 |
| `7` | 反色 |

例如：

## 粗体

```bash
echo -e "\033[1m这是粗体\033[0m"
```

## 下划线

```bash
echo -e "\033[4m这是下划线\033[0m"
```

## 反色

```bash
echo -e "\033[7m这是反色\033[0m"
```

---

# 八、颜色和样式可以组合

例如：

```bash
echo -e "\033[1;31mERROR\033[0m"
```

其中：

```text
1  = 粗体
31 = 红色
```

因此：

```text
1;31
```

就是：

> 粗体 + 红色

常见组合：

```bash
\033[1;31m
```

粗体红色

```bash
\033[1;32m
```

粗体绿色

```bash
\033[1;33m
```

粗体黄色

```bash
\033[1;34m
```

粗体蓝色

```bash
\033[1;36m
```

粗体青色

结束时统一：

```bash
\033[0m
```

---

# 九、背景颜色

除了文字颜色：

```text
30 ~ 37
```

还可以设置背景颜色：

```text
40 ~ 47
```

常见对应关系：

| 代码 | 背景颜色 |
|---:|---|
| `40` | 黑色 |
| `41` | 红色 |
| `42` | 绿色 |
| `43` | 黄色 |
| `44` | 蓝色 |
| `45` | 紫色 |
| `46` | 青色 |
| `47` | 白色 |

例如：

```bash
echo -e "\033[41m ERROR \033[0m"
```

表示红色背景。

运维脚本中一般不需要大量使用背景色，文字颜色已经足够。

---

# 十、Shell 中为什么经常看到 `echo -e`？

例如：

```bash
echo -e "\033[32mSUCCESS\033[0m"
```

这里的：

```bash
-e
```

表示让 `echo` 解释反斜杠转义字符。

例如：

```text
\033
\n
\t
```

等。

因此：

```bash
echo "\033[32mSUCCESS\033[0m"
```

和：

```bash
echo -e "\033[32mSUCCESS\033[0m"
```

行为可能不同。

在学习阶段，可以简单记：

```bash
echo -e
```

常用于让 `echo` 解释转义序列。

---

# 十一、实际运维脚本中的日志函数

这是最常见的应用。

```bash
log_info() {
    echo -e "\033[32m[INFO] $(date '+%F %T') $*\033[0m"
}

log_warn() {
    echo -e "\033[33m[WARN] $(date '+%F %T') $*\033[0m"
}

log_error() {
    echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m"
}

log_debug() {
    echo -e "\033[36m[DEBUG] $(date '+%F %T') $*\033[0m"
}
```

使用：

```bash
log_info "开始检查 nginx"
log_warn "磁盘使用率较高"
log_error "nginx 启动失败"
log_debug "当前配置文件为 /etc/nginx/nginx.conf"
```

---

# 十二、推荐：统一定义颜色变量

脚本变大以后，不建议到处直接写：

```bash
\033[31m
\033[32m
\033[33m
```

可以统一定义：

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
echo -e "${YELLOW}警告${RESET}"
echo -e "${RED}失败${RESET}"
echo -e "${CYAN}调试信息${RESET}"
```

这样可读性更好。

---

# 十三、一个比较完整的日志模板

以后写 Shell 运维脚本，可以直接参考这种结构：

```bash
#!/bin/bash

GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
RESET='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO] $(date '+%F %T') $*${RESET}"
}

log_warn() {
    echo -e "${YELLOW}[WARN] $(date '+%F %T') $*${RESET}"
}

log_error() {
    echo -e "${RED}[ERROR] $(date '+%F %T') $*${RESET}"
}

log_debug() {
    echo -e "${CYAN}[DEBUG] $(date '+%F %T') $*${RESET}"
}

log_info "开始检查服务"

if systemctl is-active --quiet nginx; then
    log_info "nginx 运行正常"
else
    log_error "nginx 未运行"
fi
```

---

# 十四、推荐记忆表

如果只是为了运维，建议记住下面这张表即可：

```text
颜色：

31 = 红
32 = 绿
33 = 黄
34 = 蓝
35 = 紫
36 = 青

样式：

1 = 粗体
4 = 下划线
7 = 反色
0 = 重置

常见：

\033[31m = 红色
\033[32m = 绿色
\033[33m = 黄色
\033[36m = 青色
\033[0m  = 恢复默认

组合：

\033[1;31m = 粗体红色
\033[1;32m = 粗体绿色
\033[1;33m = 粗体黄色
```

---

# 十五、ANSI Escape Code 不只是颜色

ANSI 转义序列还可以控制：

- 文字颜色
- 背景颜色
- 粗体
- 下划线
- 光标位置
- 清除屏幕
- 清除当前行
- 隐藏/显示光标
- 终端输出格式

例如一些终端程序会实现：

```text
进度条
动态刷新
实时监控界面
彩色日志
交互式菜单
```

不过对于普通 Linux 运维脚本：

> **先掌握颜色和少量文字样式即可。**

没有必要为了运维专门深入所有 ANSI 控制序列。

---

# 十六、运维学习优先级

如果你的目标是 **Linux 运维 / DevOps / Shell 自动化**，ANSI 颜色属于“实用小技巧”，不是核心知识。

推荐学习顺序：

```text
Linux 基础
    ↓
Shell 基础
    ↓
文件 / 权限 / 进程 / 服务
    ↓
管道与重定向
    ↓
grep / sed / awk
    ↓
Shell 脚本
    ↓
函数 / 参数 / 数组
    ↓
退出码和错误处理
    ↓
日志
    ↓
ANSI 颜色 ← 现在这里
    ↓
Shell 自动化
    ↓
Docker
    ↓
Git
    ↓
CI/CD
    ↓
监控与日志系统
```

其中 Shell 中建议重点掌握：

```text
$?
$0
$1 $2 ...
$#
$@
$*
```

以及：

```bash
if
for
while
case
function
```

还有：

```bash
>
>>
<
2>
2>&1
|
&&
||
```

以及：

```bash
set -e
set -u
set -o pipefail
```

这些对实际运维工作的价值通常比记住更多颜色代码高得多。

---

# 十七、一个简单练习

可以创建：

```bash
vim color_test.sh
```

写入：

```bash
#!/bin/bash

echo -e "\033[31m红色\033[0m"
echo -e "\033[32m绿色\033[0m"
echo -e "\033[33m黄色\033[0m"
echo -e "\033[34m蓝色\033[0m"
echo -e "\033[35m紫色\033[0m"
echo -e "\033[36m青色\033[0m"

echo

echo -e "\033[1;31m粗体红色\033[0m"
echo -e "\033[1;32m粗体绿色\033[0m"
echo -e "\033[1;33m粗体黄色\033[0m"
echo -e "\033[1;36m粗体青色\033[0m"
```

然后：

```bash
chmod +x color_test.sh
./color_test.sh
```

观察不同效果。

---

# 十八、最终需要掌握到什么程度？

对于 Linux 运维来说，建议达到下面这个程度：

### 必须掌握

```text
31 红色
32 绿色
33 黄色
36 青色
0  重置
```

能够看懂：

```bash
\033[32m
```

知道它是：

> ANSI 转义序列，用于设置绿色文字。

能够写：

```bash
GREEN='\033[32m'
RESET='\033[0m'

echo -e "${GREEN}OK${RESET}"
```

能够编写：

```bash
log_info
log_warn
log_error
```

### 了解即可

```text
背景色
粗体
下划线
反色
光标控制
```

### 暂时不需要深入

```text
ANSI/VT 控制序列完整规范
终端模拟器实现细节
复杂光标控制
复杂 TUI 编程
```

---

# 十九、一句话总结

```text
ANSI Escape Code
        ↓
终端控制指令
        ↓
颜色 / 样式 / 光标等
        ↓
Shell 运维脚本中最常用于彩色日志
```

最核心的几个：

```bash
\033[31m   # 红
\033[32m   # 绿
\033[33m   # 黄
\033[36m   # 青
\033[0m    # 重置
```

而运维实际使用时，推荐封装成：

```bash
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'
```

再配合：

```bash
log_info
log_warn
log_error
```

即可。

---

## 相关关键词

以后查资料时，可以使用这些关键词：

```text
ANSI Escape Code
ANSI escape sequence
Terminal Color
Terminal Control Sequence
Shell 彩色输出
Bash 彩色日志
Linux terminal color
```

