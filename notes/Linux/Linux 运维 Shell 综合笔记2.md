# Linux 常用命令完整学习笔记

> **学习重点**：本笔记整理自你给出的命令清单，覆盖文件与目录、权限、进程、文本处理、日志、压缩归档等常见 Linux 运维场景。
>
> 图片中标红/高亮的命令作为重点讲解，并补充实际工作中最常见的参数、组合方式和实例。

---

# 一、先建立整体认识

这些命令可以大致分成 6 类：

| 类别 | 命令 |
|---|---|
| 文件与目录 | ⭐ `pwd`、⭐ `ls`、⭐ `cd`、⭐ `cp`、⭐ `mv`、⭐ `rm`、⭐ `mkdir`、⭐ `touch`、⭐ `find`、`locate`、`file`、`stat`、`du`、`df`、`tree` |
| 权限与所有权 | ⭐ `chmod`、⭐ `chown`、`chgrp`、`umask` |
| 进程与任务 | ⭐ `ps`、⭐ `top`、`htop`、`pgrep`、`pkill`、⭐ `kill`、⭐ `killall`、`jobs`、`bg`、`fg`、`nohup` |
| 文件查看与日志 | ⭐ `cat`、`less`、`tail`、`head`、⭐ `grep`、⭐ `awk`、⭐ `sed`、`journalctl` |
| 文本处理与管道 | ⭐ `grep`、⭐ `sed`、⭐ `awk`、⭐ `cut`、⭐ `sort`、`uniq`、`tr`、`xargs`、⭐ `tee` |
| 压缩与归档 | ⭐ `find`、`tar`、`gzip` |

> `⭐` 表示重点命令。重点命令不是说其他命令不重要，而是这些命令更值得你优先掌握并练到熟练。

---

# 二、命令学习的统一思路

学习 Linux 命令，不建议只背“命令 = 中文意思”。

建议每条命令都按下面 5 个问题去理解：

```text
1. 它解决什么问题？
2. 最基本的语法是什么？
3. 实际工作最常用哪些参数？
4. 它通常和谁组合使用？
5. 使用时有什么坑？
```

例如 `grep` 不应该只记成：

```text
grep = 查找文本
```

而应该逐步理解成：

```text
grep
  ↓
在文本中匹配内容
  ↓
-i 忽略大小写
-n 显示行号
-v 反向匹配
-r 递归目录
-E 使用扩展正则
  ↓
经常和 |、awk、sed、tail、journalctl 组合
```

---

# 三、文件与目录命令

## 3.1 ⭐ `pwd`

### 作用

显示当前工作目录。

### 基本用法

```bash
pwd
```

例如：

```text
/root/scripts
```

### 常见场景

```bash
cd /var/log
pwd
```

用于确认“我现在到底在哪个目录”。

### 记忆

```text
pwd = print working directory
```

---

# 3.2 ⭐ `ls`

### 作用

查看目录内容。

### 基本用法

```bash
ls
```

### 高频参数

| 参数 | 作用 |
|---|---|
| `-l` | 详细信息 |
| `-a` | 显示隐藏文件 |
| `-h` | 以易读方式显示大小，通常配合 `-l` |
| `-A` | 显示隐藏文件，但不显示 `.` 和 `..` |
| `-t` | 按修改时间排序 |
| `-S` | 按文件大小排序 |
| `-r` | 反向排序 |
| `-d` | 查看目录本身，而不是展开目录内容 |
| `-R` | 递归显示子目录 |
|

### 工作中最常用

```bash
ls -l
```

查看文件权限、所有者、大小、时间等。

```bash
ls -lah
```

最经典的“看目录详情”写法。

```bash
ls -lt
```

按修改时间查看，排查最近变化的文件时很方便。

```bash
ls -lhS
```

按文件大小排序。

### 例子

```bash
ls -lah /var/log
```

### 易错点

`ls` 默认不显示隐藏文件。

Linux 中以 `.` 开头的普通文件一般是隐藏文件，例如：

```text
.bashrc
.profile
.gitconfig
```

---

# 3.3 ⭐ `cd`

### 作用

切换目录。

### 常见用法

```bash
cd /etc
cd /var/log
cd ..
cd ~
cd -
```

### 重点理解

| 写法 | 含义 |
|---|---|
| `cd /etc` | 进入绝对路径 |
| `cd ..` | 返回上一级目录 |
| `cd .` | 当前目录 |
| `cd ~` | 当前用户家目录 |
| `cd` | 通常进入家目录 |
| `cd -` | 回到上一次所在目录 |

### 实用技巧

```bash
cd -
```

在两个目录之间快速来回切换，非常实用。

---

# 3.4 ⭐ `cp`

### 作用

复制文件或目录。

### 基本语法

```bash
cp 源 目标
```

### 高频参数

| 参数 | 作用 |
|---|---|
| `-r` / `-R` | 递归复制目录 |
| `-i` | 覆盖前询问 |
| `-v` | 显示复制过程 |
| `-a` | 归档复制，尽量保留权限、时间、符号链接等属性 |
| `-p` | 保留权限、时间等基本属性 |

### 例子

复制文件：

```bash
cp a.txt b.txt
```

复制到目录：

```bash
cp a.txt /tmp/
```

复制整个目录：

```bash
cp -r project /backup/
```

实际备份中经常直接用：

```bash
cp -a project /backup/project
```

### 工作习惯

覆盖前比较谨慎时：

```bash
cp -iv a.txt b.txt
```

---

# 3.5 ⭐ `mv`

### 作用

`mv` 有两个核心用途：

```text
移动
重命名
```

### 例子

移动文件：

```bash
mv app.log /tmp/
```

重命名：

```bash
mv old.txt new.txt
```

移动目录：

```bash
mv project /opt/
```

### 常用参数

| 参数 | 作用 |
|---|---|
| `-i` | 覆盖前询问 |
| `-v` | 显示操作过程 |

### 重点理解

在同一个目录下：

```bash
mv old.conf new.conf
```

本质上就是重命名。

---

# 3.6 ⭐ `rm`

### 作用

删除文件或目录。

### 高频参数

| 参数 | 作用 |
|---|---|
| `-r` | 递归删除目录 |
| `-f` | 强制删除，不询问 |
| `-i` | 删除前询问 |
| `-v` | 显示删除过程 |

### 例子

```bash
rm test.txt
```

删除目录：

```bash
rm -r project
```

强制删除：

```bash
rm -f test.txt
```

删除目录并递归：

```bash
rm -rf project
```

### 最重要的安全提醒

```bash
rm -rf
```

非常强大，也非常危险。

特别是在 root 下不要习惯性执行：

```bash
rm -rf *
```

执行前一定确认当前目录：

```bash
pwd
ls
```

生产服务器上建议先尽量使用：

```bash
rm -ri directory
```

---

# 3.7 ⭐ `mkdir`

### 作用

创建目录。

### 常用参数

| 参数 | 作用 |
|---|---|
| `-p` | 连同父目录一起创建 |
| `-m` | 创建时直接指定权限 |
| `-v` | 显示创建过程 |

### 例子

```bash
mkdir test
```

递归创建：

```bash
mkdir -p /opt/project/logs/nginx
```

指定权限：

```bash
mkdir -m 755 scripts
```

### 实际工作

脚本中很常见：

```bash
mkdir -p /var/log/myapp
```

即使中间目录不存在，也可以一起创建。

---

# 3.8 ⭐ `touch`

### 作用

常见用途：

```text
创建空文件
更新文件时间
```

### 例子

```bash
touch test.txt
```

一次创建多个：

```bash
touch a.txt b.txt c.txt
```

### 更新时间

如果文件已经存在：

```bash
touch test.txt
```

通常会更新时间戳，而不会清空原文件内容。

### 高频选项

```bash
touch -a file
```

只更新访问时间。

```bash
touch -m file
```

只更新修改时间。

---

# 3.9 ⭐ `find`

> `find` 是 Linux 运维中非常重要的命令，建议重点掌握。

### 作用

在目录树中按条件查找文件或目录。

### 基本语法

```bash
find [路径] [条件] [动作]
```

### 最常用：按名字找

```bash
find /etc -name "*.conf"
```

大小写不敏感：

```bash
find /etc -iname "*.conf"
```

### 按类型

```bash
find . -type f
```

只找普通文件。

```bash
find . -type d
```

只找目录。

### 按大小

```bash
find /var/log -type f -size +100M
```

查找大于 100MB 的文件。

```bash
find . -type f -size -10M
```

查找小于 10MB 的文件。

### 按时间

```bash
find /var/log -type f -mtime -1
```

查找最近 1 天内修改过的文件。

```bash
find /tmp -type f -mmin -30
```

查找最近 30 分钟修改过的文件。

### `maxdepth`

```bash
find . -maxdepth 1 -type f
```

只搜索当前层级，不深入子目录。

### 按用户

```bash
find /home -user root
```

### 按权限

```bash
find /var/www -type f -perm 644
```

### `-exec`

找到后执行命令：

```bash
find . -type f -name "*.log" -exec ls -lh {} +
```

这里：

```text
{} → find 找到的文件
+  → 尽可能一次传给命令多个文件
```

### 删除匹配文件

```bash
find /tmp -type f -name "*.tmp" -delete
```

生产环境中使用 `-delete` 前一定先验证：

```bash
find /tmp -type f -name "*.tmp"
```

确认结果后再删除。

### 经典组合

查找并统计：

```bash
find /var/log -type f | wc -l
```

查找 100MB 以上日志：

```bash
find /var/log -type f -size +100M -ls
```

---

# 3.10 `locate`

### 作用

通过数据库快速查找文件。

```bash
locate passwd
```

### 与 `find` 的区别

| 命令 | 特点 |
|---|---|
| `find` | 实时搜索文件系统 |
| `locate` | 查询预先建立的数据库，速度通常更快 |

### 注意

`locate` 依赖数据库，数据库没有及时更新时，结果可能不是最新的。

常见更新命令：

```bash
sudo updatedb
```

### 适合

“我只想快速找一下某个文件大概在哪里。”

### 不适合

要求结果必须实时、同时带复杂条件的场景。

---

# 3.11 `file`

### 作用

判断文件的实际类型。

```bash
file test
```

例如可能得到：

```text
ELF 64-bit LSB executable
```

或者：

```text
ASCII text
```

### 实际用途

当文件扩展名不可信时尤其有用：

```bash
file unknown_file
```

Linux 判断文件类型不能只看扩展名。

---

# 3.12 `stat`

### 作用

查看文件的详细状态信息。

```bash
stat test.txt
```

可以看到：

```text
File
Size
Blocks
IO Block
Access
Modify
Change
Birth
```

### 重点区分 3 个时间

```text
atime → Access，访问时间
mtime → Modify，内容修改时间
ctime → Change，元数据变化时间
```

例如：

```bash
stat /etc/hosts
```

排查“文件到底什么时候修改过”时很有价值。

---

# 3.13 `du`

### 作用

查看文件或目录占用的磁盘空间。

### 高频参数

| 参数 | 作用 |
|---|---|
| `-h` | 易读单位 |
| `-s` | 只统计总量 |
| `--max-depth=1` | 指定目录深度 |

### 常见命令

```bash
du -sh /var/log
```

查看日志目录总大小。

```bash
du -h --max-depth=1 /var
```

看 `/var` 下一级目录分别占了多少。

### 排查磁盘暴增

```bash
du -h --max-depth=1 /var | sort -h
```

这类组合非常实用。

---

# 3.14 `df`

### 作用

查看文件系统整体磁盘使用情况。

```bash
df -h
```

常见输出：

```text
Filesystem  Size  Used Avail Use% Mounted on
```

### 重点理解

```text
df → 文件系统整体还剩多少
 du → 某个目录/文件到底占了多少
```

### 工作中常用

```bash
df -h
```

快速判断服务器磁盘是否爆满。

```bash
df -ih
```

查看 inode 使用情况。

---

# 3.15 `tree`

### 作用

以树形结构查看目录。

```bash
tree
```

常见参数：

```bash
tree -L 2
```

只显示两层。

```bash
tree -a
```

显示隐藏文件。

```bash
tree -d
```

只看目录。

> 某些极简 Linux 系统默认没有安装 `tree`，可以自行安装对应软件包。

---

# 四、权限与所有权

# 4.1 ⭐ `chmod`

> `chmod` 是 Linux 权限管理的核心命令之一。

### 作用

修改文件或目录权限。

Linux 基本权限：

```text
r = read    = 4
w = write   = 2
x = execute = 1
```

对应三个对象：

```text
u = user
 g = group
 o = other
```

### 数字权限

```bash
chmod 755 script.sh
```

含义：

```text
7 = rwx
5 = r-x
5 = r-x
```

所以：

```text
user  → rwx
 group → r-x
 other → r-x
```

### 常见权限

| 权限 | 典型用途 |
|---|---|
| `644` | 普通文件 |
| `600` | 私密文件、密钥类文件 |
| `755` | 可执行脚本、程序目录 |
| `700` | 只有自己可访问 |
| `775` | 用户和组都需要写入 |

### 符号方式

```bash
chmod u+x script.sh
```

给文件所有者增加执行权限。

```bash
chmod g+w file
```

给组增加写权限。

```bash
chmod o-r file
```

删除其他人的读权限。

### 递归修改

```bash
chmod -R 755 /opt/project
```

**很危险，要谨慎。**

特别是一个目录里同时包含：

```text
目录
普通文件
脚本
密钥
```

不应该简单粗暴地全部改成同一个权限。

### 脚本最常见

```bash
chmod +x script.sh
```

然后：

```bash
./script.sh
```

---

# 4.2 ⭐ `chown`

### 作用

修改文件所有者和所属组。

```bash
chown user file
```

同时修改用户和组：

```bash
chown user:group file
```

### 常用参数

```bash
chown -R user:group directory
```

递归修改整个目录。

### 常见场景

Web 服务目录：

```bash
chown -R www-data:www-data /var/www/html
```

### 注意

`chown` 是改“谁拥有它”，不是改“能做什么”。

```text
chown → 所有权
chmod → 权限
```

---

# 4.3 `chgrp`

### 作用

只修改所属组。

```bash
chgrp devops file.txt
```

递归：

```bash
chgrp -R devops project/
```

如果同时修改用户和组，通常使用：

```bash
chown user:group file
```

---

# 4.4 `umask`

### 作用

控制新创建文件和目录的默认权限掩码。

查看：

```bash
umask
```

常见结果：

```text
0022
```

### 理解方式

通常可以从：

```text
文件基准权限：666
目录基准权限：777
```

再结合 `umask` 得到实际权限。

例如 `umask 022` 时，常见结果：

```text
新文件  → 644
新目录  → 755
```

### 临时修改

```bash
umask 027
```

然后当前 Shell 创建的新文件/目录会采用新的掩码。

### 记忆

```text
chmod → 改已经存在的
umask → 控制新创建的
```

---

# 五、进程与任务管理

# 5.1 ⭐ `ps`

### 作用

查看当前系统进程快照。

### 高频用法

```bash
ps
```

查看当前终端进程。

```bash
ps aux
```

查看系统中更完整的进程信息，是运维非常经典的写法。

```bash
ps -ef
```

也是非常常用的完整进程查看方式。

### `ps aux` 与 `ps -ef`

两个都很常用，没有必要死记成“谁绝对正确”，关键是看输出是否满足需求。

### 配合 grep

```bash
ps aux | grep nginx
```

查 nginx 相关进程。

更推荐现代环境下：

```bash
pgrep -af nginx
```

后面会讲。

### 看指定 PID

```bash
ps -p 1234 -f
```

### 看进程树

```bash
ps -ef --forest
```

排查父子进程关系很有用。

---

# 5.2 ⭐ `top`

### 作用

动态查看系统资源和进程。

```bash
top
```

可以观察：

```text
CPU
内存
Load Average
进程
PID
用户
CPU 占用
内存占用
```

### 常用交互键

进入 `top` 后：

| 按键 | 作用 |
|---|---|
| `P` | 按 CPU 排序 |
| `M` | 按内存排序 |
| `N` | 按 PID 排序 |
| `1` | 显示各 CPU 核心 |
| `k` | 向进程发送信号 |
| `q` | 退出 |
| `h` | 查看帮助 |

### 非交互方式

脚本里不适合一直停留在交互界面，可以：

```bash
top -b -n 1
```

表示批处理模式运行 1 次。

例如保存结果：

```bash
top -b -n 1 > top.txt
```

---

# 5.3 `htop`

### 作用

`top` 的交互式增强版，通常界面更直观。

```bash
htop
```

常见特点：

```text
更直观
支持鼠标
更方便查看/操作进程
```

但注意：

```text
htop 不是很多最小化系统默认自带的。
```

---

# 5.4 `pgrep`

### 作用

按进程名称或条件查找 PID。

```bash
pgrep nginx
```

只输出 PID。

查看 PID + 命令：

```bash
pgrep -af nginx
```

### 常用参数

| 参数 | 作用 |
|---|---|
| `-a` | 显示完整命令行 |
| `-f` | 匹配完整命令行 |
| `-u user` | 指定用户进程 |
| `-l` | 显示 PID 和进程名 |

例如：

```bash
pgrep -u root nginx
```

---

# 5.5 `pkill`

### 作用

按照进程名/条件发送信号。

```bash
pkill nginx
```

相当于按名称匹配进程并发送默认终止信号。

### 更稳妥的使用

先查看：

```bash
pgrep -af nginx
```

确认无误后再：

```bash
pkill nginx
```

### 按用户

```bash
pkill -u alice
```

### 指定信号

```bash
pkill -TERM nginx
```

---

# 5.6 ⭐ `kill`

> `kill` 的本质不是“强制杀进程”，而是**向进程发送信号**。

### 基本语法

```bash
kill PID
```

默认通常发送：

```text
SIGTERM (15)
```

### 常用信号

| 信号 | 编号 | 含义 |
|---|---:|---|
| `SIGTERM` | 15 | 请求程序正常退出 |
| `SIGKILL` | 9 | 强制终止，不能被程序捕获处理 |
| `SIGHUP` | 1 | 挂起/常被用于通知重新加载 |
| `SIGINT` | 2 | 中断，类似 Ctrl+C |
| `SIGSTOP` | 19 | 暂停进程 |
| `SIGCONT` | 18 | 继续执行 |

### 推荐顺序

先：

```bash
kill PID
```

如果程序不退出，再：

```bash
kill -9 PID
```

不要习惯性使用：

```bash
kill -9
```

因为程序被强杀通常没有机会进行清理工作。

### `kill -l`

查看信号列表：

```bash
kill -l
```

---

# 5.7 ⭐ `killall`

### 作用

按进程名称批量发送信号。

```bash
killall nginx
```

也可以：

```bash
killall -TERM nginx
```

强制：

```bash
killall -9 nginx
```

### 和 `kill` 的区别

```text
kill PID       → 根据 PID
killall name  → 根据进程名
```

### 风险

进程名匹配范围可能很大。

所以执行前最好：

```bash
pgrep -af nginx
```

---

# 5.8 `jobs`

### 作用

查看当前 Shell 的后台任务/作业。

```bash
jobs
```

例如：

```text
[1]+  Running  sleep 1000 &
```

这里的：

```text
[1]
```

是 job 编号，不是 PID。

### 重点

`jobs` 主要针对：

```text
当前 Shell 的作业控制
```

不是用来查看整个系统所有进程的。

---

# 5.9 `bg`

### 作用

让被暂停的 Shell 作业在后台继续执行。

例如程序正在前台运行时按：

```text
Ctrl+Z
```

先暂停。

然后：

```bash
bg
```

使其在后台继续。

指定作业：

```bash
bg %1
```

---

# 5.10 `fg`

### 作用

把后台作业拉回前台。

```bash
fg
```

或者：

```bash
fg %1
```

典型流程：

```text
运行程序
   ↓
Ctrl+Z
   ↓
jobs
   ↓
bg %1
   ↓
后台运行
   ↓
fg %1
   ↓
重新回到前台
```

---

# 5.11 `nohup`

### 作用

让命令在退出终端后仍尽量继续运行。

最经典写法：

```bash
nohup ./server.sh > server.log 2>&1 &
```

拆开理解：

```text
nohup      → 忽略终端挂断影响
> server.log → 标准输出写日志
2>&1       → 标准错误也写到同一个地方
&          → 后台运行
```

### 常见错误

很多人只写：

```bash
nohup ./server.sh
```

虽然也可以工作，但不如明确重定向日志：

```bash
nohup ./server.sh > server.log 2>&1 &
```

### 注意

`nohup` 不是现代生产环境守护进程管理的替代方案。

生产服务更推荐：

```text
systemd
Docker
Kubernetes
```

---

# 六、文件查看与日志分析

# 6.1 ⭐ `cat`

### 作用

连接并输出文件内容。

最简单：

```bash
cat file.txt
```

### 常用参数

| 参数 | 作用 |
|---|---|
| `-n` | 显示所有行号 |
| `-b` | 只给非空行编号 |
| `-A` | 显示不可见字符的详细形式 |
| `-s` | 合并连续空行 |

### 实例

```bash
cat -n test.txt
```

### 组合：创建文件

```bash
cat > file.txt
```

输入内容，按 `Ctrl+D` 结束。

追加：

```bash
cat >> file.txt
```

### 多文件合并

```bash
cat a.txt b.txt > all.txt
```

### 注意

不要把 `cat` 当成“任何文件都直接看”的万能工具。

大日志文件：

```bash
cat huge.log
```

可能直接刷屏。

此时更适合：

```bash
less huge.log
```

或者：

```bash
tail -f huge.log
```

---

# 6.2 `less`

### 作用

分页查看文件，适合大文件。

```bash
less /var/log/syslog
```

### 常用操作

| 按键 | 作用 |
|---|---|
| `Space` | 下一页 |
| `b` | 上一页 |
| `g` | 开头 |
| `G` | 结尾 |
| `/关键字` | 搜索 |
| `n` | 下一个匹配 |
| `N` | 上一个匹配 |
| `q` | 退出 |

### 常见参数

```bash
less -N file.txt
```

显示行号。

```bash
less -S file.txt
```

不自动折行，长行可以水平查看。

---

# 6.3 `tail`

### 作用

查看文件末尾内容。

```bash
tail file.log
```

### 高频参数

```bash
tail -n 50 app.log
```

最后 50 行。

```bash
tail -f app.log
```

持续跟踪文件变化，非常常用。

### `-F`

```bash
tail -F app.log
```

比 `-f` 更适合日志轮转后继续跟踪，因为文件被替换/重新创建时通常更容易继续追踪。

### 实际排错

```bash
tail -n 100 /var/log/nginx/error.log
```

---

# 6.4 `head`

### 作用

查看文件开头内容。

```bash
head file.txt
```

最后 20 行：

```bash
head -n 20 file.txt
```

前 100 字节：

```bash
head -c 100 file.txt
```

### 常见用途

快速查看配置文件、CSV、日志的开头。

---

# 七、⭐ 文本搜索与处理：重点模块

这是 Shell 运维真正非常核心的一部分。

建议重点形成下面这个思维：

```text
grep → 找
cut  → 切
sort → 排
uniq → 去重/统计
tr   → 替换/删除字符
sed  → 按规则修改文本
awk  → 按字段分析文本
xargs → 把文本变成命令参数
tee  → 一边输出一边保存
```

---

# 7.1 ⭐ `grep`

> **最重要的文本搜索命令之一。**

### 作用

在文本中查找匹配内容。

### 基本语法

```bash
grep [选项] "模式" 文件
```

### 最基本

```bash
grep "error" app.log
```

查找包含 `error` 的行。

### 忽略大小写 `-i`

```bash
grep -i "error" app.log
```

`ERROR`、`Error`、`error` 都可以匹配。

### 显示行号 `-n`

```bash
grep -n "error" app.log
```

非常适合排错。

### 反向匹配 `-v`

```bash
grep -v "debug" app.log
```

排除包含 `debug` 的行。

### 递归搜索 `-r`

```bash
grep -r "server_name" /etc/nginx
```

### `-R`

`-R` 也可递归，并且对符号链接的处理和 `-r` 有区别。在日常排查中，不确定符号链接情况时可以先理解为：

```text
-r / -R → 递归目录查找
```

### 单词匹配 `-w`

```bash
grep -w "root" file.txt
```

匹配完整单词，而不是任意包含 `root` 的字符串。

### 扩展正则 `-E`

```bash
grep -E "error|warning" app.log
```

表示匹配 `error` 或 `warning`。

等价工具名也常见：

```bash
egrep "error|warning" app.log
```

但新学习时更推荐记 `grep -E`。

### 固定字符串 `-F`

```bash
grep -F '[ERROR]' app.log
```

不按正则解释，更适合真正的“固定字符串查找”。

### 只输出匹配内容 `-o`

```bash
grep -oE '[0-9]+' file.txt
```

只输出匹配到的数字。

### 只输出文件名 `-l`

```bash
grep -rl "TODO" .
```

只列出包含 `TODO` 的文件。

### 查找上下文 `-A/-B/-C`

```bash
grep -A 2 "ERROR" app.log
```

显示 ERROR 后 2 行。

```bash
grep -B 2 "ERROR" app.log
```

显示 ERROR 前 2 行。

```bash
grep -C 2 "ERROR" app.log
```

前后都显示 2 行。

### 组合：查看正在监听的进程/端口等输出

现代系统推荐根据工具情况直接使用结构化命令，但文本分析中常见：

```bash
some_command | grep nginx
```

### 工作中最常见的组合

```bash
grep -in "error" app.log
```

```bash
grep -Rni "listen" /etc/nginx
```

```bash
tail -f app.log | grep --line-buffered "ERROR"
```

### 易错点：变量/正则中的特殊字符

如果你只是想找一个固定字符串，尤其字符串中含有正则特殊字符时，可优先考虑：

```bash
grep -F 'a.b' file
```

而不是直接：

```bash
grep 'a.b' file
```

---

# 7.2 ⭐ `awk`

> `awk` 是 Linux 文本处理里非常值得长期掌握的命令。
>
> 它尤其擅长：**按列/字段取值、过滤、统计、计算、格式化输出。**

### 基本结构

```bash
awk '条件 {动作}' 文件
```

### 先理解 `$1 $2 $3`

例如：

```text
Tom 20 Beijing
Jack 22 Shanghai
```

默认按空白分字段：

```text
$1 = Tom
$2 = 20
$3 = Beijing
```

而：

```text
$0 = 整行
NF = 当前行字段数量
NR = 当前行行号
```

### 打印某一列

```bash
awk '{print $1}' file.txt
```

### 打印多列

```bash
awk '{print $1, $3}' file.txt
```

### 条件过滤

```bash
awk '$3 > 80 {print $1, $3}' score.txt
```

意思：第三列大于 80 才输出。

### 指定分隔符 `-F`

对于 `/etc/passwd`：

```bash
awk -F: '{print $1, $7}' /etc/passwd
```

结果类似：

```text
root /bin/bash
user /bin/bash
```

### `-v`

给 awk 变量传入值：

```bash
awk -v threshold=80 '$3 > threshold {print $1, $3}' score.txt
```

### `BEGIN`

处理正式输入前执行：

```bash
awk 'BEGIN {print "start"} {print $1}' file.txt
```

### `END`

所有输入处理完后执行：

```bash
awk '{sum += $2} END {print sum}' data.txt
```

### 统计总和

```bash
awk '{sum += $2} END {print sum}' data.txt
```

### 统计平均值

```bash
awk '{sum += $2; n++} END {print sum/n}' data.txt
```

### 结合 `ps`

```bash
ps -eo pid,comm,%cpu --no-headers | awk '$3 > 50 {print $1, $2, $3}'
```

含义：找 CPU 大于 50% 的进程。

### 结合 `df`

```bash
df -P | awk 'NR > 1 {print $5, $6}'
```

取磁盘使用率和挂载点。

### 注意

`awk` 是“按字段分析”的利器，但遇到真正复杂的 CSV（带引号、字段内部又包含逗号等）时，不能简单地认为 `-F,` 就是完整 CSV 解析器。

---

# 7.3 ⭐ `sed`

> `sed` 最常用的感觉可以理解成：**按规则批量修改或筛选文本。**

### 基本语法

```bash
sed [选项] '命令' 文件
```

### 替换 `s`

最经典：

```bash
sed 's/old/new/' file.txt
```

默认只替换每一行第一次出现的内容。

### 全行替换 `g`

```bash
sed 's/old/new/g' file.txt
```

### 忽略大小写

GNU sed 可写：

```bash
sed 's/error/ERROR/gi' file.txt
```

### 指定行

只修改第 3 行：

```bash
sed '3s/old/new/' file.txt
```

第 3～5 行：

```bash
sed '3,5s/old/new/g' file.txt
```

### 删除行 `d`

删除第 3 行：

```bash
sed '3d' file.txt
```

删除包含 error 的行：

```bash
sed '/error/d' file.txt
```

### 只打印指定内容 `-n + p`

只显示第 1～10 行：

```bash
sed -n '1,10p' file.txt
```

### 直接修改文件 `-i`

```bash
sed -i 's/old/new/g' file.txt
```

### **生产环境建议先备份**

GNU sed：

```bash
sed -i.bak 's/old/new/g' file.txt
```

这样会留下：

```text
file.txt
file.txt.bak
```

### 扩展正则

GNU sed 可以：

```bash
sed -E 's/(foo|bar)/xxx/g' file.txt
```

### 实际运维例子

修改配置中的端口：

```bash
sed -i.bak 's/^port=8080$/port=9090/' app.conf
```

这里只替换整行恰好是 `port=8080` 的情况，更安全。

### `^` 与 `$`

正则中：

```text
^ → 行开头
$ → 行结尾
```

例如：

```bash
sed -n '/^server/p' app.conf
```

查找以 `server` 开头的行。

---

# 7.4 ⭐ `cut`

> `cut` 很适合做简单、规则明确的“切列”。

### 按分隔符切字段

例如：

```text
Tom:20:Beijing
```

执行：

```bash
echo 'Tom:20:Beijing' | cut -d: -f1
```

结果：

```text
Tom
```

### 多列

```bash
echo 'Tom:20:Beijing' | cut -d: -f1,3
```

结果：

```text
Tom:Beijing
```

### 连续字段

```bash
cut -d: -f1-3 file.txt
```

### `-c`

按字符位置截取：

```bash
cut -c1-5 file.txt
```

### `-f`

按字段截取：

```bash
cut -d: -f1 /etc/passwd
```

### `cut` 和 `awk` 的区别

```text
cut  → 简单切列
awk  → 复杂条件、计算、格式化
```

例如只是取 `/etc/passwd` 第一列：

```bash
cut -d: -f1 /etc/passwd
```

完全没必要为了简单事情写很复杂的 `awk`。

---

# 7.5 ⭐ `sort`

### 作用

排序。

```bash
sort file.txt
```

### 数字排序 `-n`

假设：

```text
2
10
1
```

普通字符串排序可能不是你想要的结果。

使用：

```bash
sort -n file.txt
```

### 反向 `-r`

```bash
sort -nr numbers.txt
```

### 按指定列 `-k`

例如：

```text
Tom 80
Jack 95
Alice 70
```

按照第二列数字排序：

```bash
sort -k2,2n score.txt
```

降序：

```bash
sort -k2,2nr score.txt
```

### 按分隔符

```bash
sort -t: -k3,3n /etc/passwd
```

### 唯一 `-u`

```bash
sort -u file.txt
```

排序后去掉重复行。

### 易读数字 `-h`

处理类似：

```text
1K
100M
2G
```

可以：

```bash
sort -h file.txt
```

### 常见组合

```bash
du -h --max-depth=1 /var | sort -h
```

---

# 7.6 `uniq`

### 作用

去掉相邻重复行或统计重复次数。

### 重要认知

`uniq` 只处理**相邻的重复行**。

所以通常和 `sort` 一起：

```bash
sort file.txt | uniq
```

### 统计次数

```bash
sort file.txt | uniq -c
```

### 只看重复项

```bash
sort file.txt | uniq -d
```

### 只看不重复项

```bash
sort file.txt | uniq -u
```

### 最常见组合

统计访问日志中的 IP：

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr
```

这个命令非常值得理解：

```text
awk → 提取 IP
sort → 排序
uniq -c → 统计
sort -nr → 按次数倒序
```

---

# 7.7 `tr`

### 作用

转换或删除字符。

### 字符替换

```bash
echo 'hello' | tr 'a-z' 'A-Z'
```

结果：

```text
HELLO
```

### 删除字符 `-d`

```bash
echo '123-456-789' | tr -d '-'
```

结果：

```text
123456789
```

### 压缩连续字符 `-s`

```bash
echo 'a    b' | tr -s ' '
```

把多个空格压缩成一个。

### 常见字符类

```text
[:upper:]
[:lower:]
[:digit:]
[:space:]
```

例如：

```bash
echo 'hello 123' | tr -d '[:digit:]'
```

---

# 7.8 `xargs`

> `xargs` 的核心理解：**把标准输入中的内容组装成命令行参数。**

### 最简单

```bash
echo 'a b c' | xargs
```

### 传给命令

```bash
printf '%s\n' a.txt b.txt | xargs ls -l
```

### 每次处理一个 `-n 1`

```bash
printf '%s\n' a b c | xargs -n 1 echo
```

### 指定占位符 `-I`

```bash
printf '%s\n' a b c | xargs -I {} echo '文件：{}'
```

### 文件名含空格：`-0`

这是非常重要的安全习惯。

配合 `find`：

```bash
find . -type f -print0 | xargs -0 ls -l
```

因为 `-print0` 使用 NUL 分隔，而不是空白字符。

### 并发 `-P`

```bash
printf '%s\n' 1 2 3 4 | xargs -n 1 -P 4 echo
```

可以让多个任务并发执行。

### 风险

使用 `xargs` 批量执行命令前，先确认输入内容。

特别是：

```bash
find ... | xargs rm
```

处理异常文件名时可能出现问题。

优先考虑：

```bash
find ... -print0 | xargs -0 ...
```

---

# 7.9 ⭐ `tee`

> `tee` 非常适合运维脚本、日志记录、调试管道。

### 作用

把标准输入：

```text
同时写到文件 + 输出到终端
```

### 基本用法

```bash
echo 'hello' | tee output.txt
```

你会同时看到：

```text
hello
```

并且文件中也有：

```text
hello
```

### 追加 `-a`

```bash
echo 'next' | tee -a output.txt
```

注意：

```text
tee 默认覆盖
tee -a 追加
```

### 实际工作中非常常见

安装命令同时保存日志：

```bash
some_command 2>&1 | tee install.log
```

### 在需要 root 权限的场景非常有价值

例如：

```bash
echo 'nameserver 8.8.8.8' | sudo tee -a /etc/resolv.conf
```

原因是：

```bash
sudo echo '...' >> /etc/resolv.conf
```

并不会让 `>>` 本身获得 root 权限。

而：

```bash
echo '...' | sudo tee -a /etc/resolv.conf
```

真正负责写文件的 `tee` 是 root 权限。

这属于 Shell 中非常经典的实战技巧。

### 调试管道

```bash
cat access.log | tee /tmp/debug.log | grep '500'
```

这样既可以继续传给 `grep`，又把中间输入保存下来排查。

---

# 八、日志系统

# 8.1 `journalctl`

### 作用

查看 systemd journal 日志。

### 查看全部日志

```bash
journalctl
```

### 查看某个服务

```bash
journalctl -u nginx
```

### 实时跟踪

```bash
journalctl -u nginx -f
```

### 最近 100 行

```bash
journalctl -u nginx -n 100
```

### 指定时间

```bash
journalctl --since "1 hour ago"
```

```bash
journalctl --since "2026-10-08 10:00:00" --until "2026-10-08 12:00:00"
```

### 只看错误级别

```bash
journalctl -p err
```

### 本次开机日志

```bash
journalctl -b
```

### 当前启动后的 nginx 日志

```bash
journalctl -b -u nginx
```

### 不分页

```bash
journalctl --no-pager
```

脚本或导出日志时很常见。

### 工作中常见组合

```bash
journalctl -u nginx -n 100 --no-pager
```

实时看：

```bash
journalctl -u nginx -f
```

排查最近启动失败：

```bash
journalctl -u nginx -b -p err --no-pager
```

---

# 九、压缩与归档

# 9.1 `tar`

> `tar` 是 Linux 服务器打包、备份、发布文件时非常核心的工具。

### 先理解一个概念

```text
tar      → 归档/打包
 gzip     → 压缩
```

两者经常组合：

```text
.tar       → 只打包
.tar.gz    → 打包 + gzip 压缩
```

### 创建归档

```bash
tar -cf backup.tar project/
```

### 查看归档内容

```bash
tar -tf backup.tar
```

### 解包

```bash
tar -xf backup.tar
```

### gzip 压缩

```bash
tar -czf backup.tar.gz project/
```

含义：

```text
-c → create
-z → gzip
-f → 指定文件名
```

### 解压 `.tar.gz`

```bash
tar -xzf backup.tar.gz
```

### bzip2

```bash
tar -cjf backup.tar.bz2 project/
tar -xjf backup.tar.bz2
```

### xz

```bash
tar -cJf backup.tar.xz project/
tar -xJf backup.tar.xz
```

### 查看归档内容但不解压

```bash
tar -tzf backup.tar.gz
```

非常实用。

### 指定目录解压

```bash
tar -xzf backup.tar.gz -C /opt/
```

### 排除目录

```bash
tar -czf project.tar.gz project/ --exclude='project/node_modules'
```

### 高频组合

```bash
tar -czvf backup-$(date +%F).tar.gz /etc/nginx
```

生成类似：

```text
backup-2026-10-09.tar.gz
```

---

# 9.2 `gzip`

### 作用

gzip 压缩文件。

```bash
gzip file.log
```

结果：

```text
file.log.gz
```

### 解压

```bash
gzip -d file.log.gz
```

也可以：

```bash
gunzip file.log.gz
```

### 保留原文件 `-k`

```bash
gzip -k file.log
```

### 指定压缩级别

```bash
gzip -1 file
```

压缩快，压缩率较低。

```bash
gzip -9 file
```

压缩更积极，速度可能更慢。

### 输出到标准输出 `-c`

```bash
gzip -c file > file.gz
```

### 注意

`gzip` 本身主要压缩单个文件流，不负责像 `tar` 那样把多个目录文件组织成一个归档。

所以：

```text
多个文件/目录 → tar → 再 gzip
```

很常见。

---

# 十、几个非常值得掌握的“命令组合”

Linux 实际工作中，真正强大的往往不是某个单独命令，而是命令组合。

## 10.1 找错误日志

```bash
tail -n 200 app.log | grep -i error
```

理解：

```text
tail → 取最后 200 行
grep → 找 error
```

---

## 10.2 实时查看错误

```bash
tail -f app.log | grep --line-buffered -i error
```

---

## 10.3 统计日志中状态码

假设某列是状态码：

```bash
awk '{print $9}' access.log | sort | uniq -c | sort -nr
```

---

## 10.4 找磁盘中最大的文件

```bash
find /var -type f -printf '%s %p\n' | sort -nr | head
```

说明：

```text
find   → 找文件
printf → 输出大小和路径
sort   → 按大小排序
head   → 取前几名
```

> `-printf` 是 GNU find 的常见能力，不是所有非 GNU 环境都保证支持。

---

## 10.5 找最近一天修改过的日志

```bash
find /var/log -type f -name '*.log' -mtime -1
```

---

## 10.6 查看哪个目录最占空间

```bash
du -h --max-depth=1 /var | sort -h
```

---

## 10.7 查看 nginx 错误日志

```bash
tail -n 100 /var/log/nginx/error.log
```

再进一步：

```bash
grep -in 'error' /var/log/nginx/error.log
```

---

## 10.8 搜索配置项

```bash
grep -Rni 'server_name' /etc/nginx
```

---

## 10.9 查找进程

```bash
ps aux | grep nginx
```

更推荐：

```bash
pgrep -af nginx
```

---

## 10.10 查找并处理日志文件

先找：

```bash
find /var/log -type f -name '*.log'
```

确认无误后，再考虑：

```bash
find /var/log -type f -name '*.log' -mtime +30
```

实际删除前最好先确认列表。

---

# 十一、重点命令之间的区别

## 11.1 `find` vs `locate`

```text
find   → 实时、条件丰富
locate → 快速、依赖数据库
```

---

## 11.2 `du` vs `df`

```text
du → 某目录/文件用了多少
 df → 某个文件系统用了多少/还剩多少
```

排查“磁盘满了”时通常两者一起用：

```bash
df -h

du -h --max-depth=1 / | sort -h
```

---

## 11.3 `cat` vs `less`

```text
cat  → 直接全部输出
less → 分页查看
```

大文件优先：

```bash
less file.log
```

---

## 11.4 `grep` vs `awk` vs `sed`

可以先这么记：

```text
grep → 找
awk  → 分析/计算/取列
sed  → 修改/替换/删除/筛选
```

例如：

```bash
grep 'ERROR' app.log
```

```bash
awk '{print $1}' access.log
```

```bash
sed 's/old/new/g' file.txt
```

---

## 11.5 `cut` vs `awk`

```text
cut → 简单切列
awk → 复杂字段处理
```

简单场景优先 `cut`。

复杂统计或判断优先 `awk`。

---

## 11.6 `sort` vs `uniq`

`uniq` 不负责完整排序。

所以很常见：

```bash
sort file | uniq
```

或者：

```bash
sort file | uniq -c | sort -nr
```

---

## 11.7 `kill` vs `killall` vs `pkill`

```text
kill PID       → 按 PID
killall name   → 按进程名
pkill 条件      → 按规则匹配进程
```

---

## 11.8 `jobs` vs `ps`

```text
jobs → 当前 Shell 的作业
ps   → 系统进程快照
```

---

# 十二、Shell 管道必须掌握

很多运维命令都依赖：

```bash
命令1 | 命令2 | 命令3
```

其中 `|` 的意义是：

> 把前一个命令的标准输出，交给下一个命令的标准输入。

例如：

```bash
ps aux | grep nginx
```

可以理解为：

```text
ps aux
  ↓
产生全部进程文本
  ↓
grep nginx
  ↓
只保留包含 nginx 的行
```

更复杂：

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
```

这就是典型的 Linux 文本处理流水线。

---

# 十三、重定向也必须掌握

## `>`

覆盖写入：

```bash
echo hello > file.txt
```

## `>>`

追加：

```bash
echo hello >> file.txt
```

## `2>`

重定向标准错误：

```bash
command 2> error.log
```

## `2>&1`

标准错误跟随标准输出：

```bash
command > all.log 2>&1
```

## `&>`

Bash 中还常见：

```bash
command &> all.log
```

---

# 十四、学习顺序建议

根据你目前学习 Linux 运维、Shell 脚本的阶段，不建议把所有命令同时硬背。

## 第一阶段：文件基础

优先掌握：

```text
pwd
ls
cd
cp
mv
rm
mkdir
touch
find
```

尤其是：

```bash
ls -lah
cp -r
mv
rm -r
mkdir -p
find ... -name ...
```

---

## 第二阶段：权限

```text
chmod
chown
chgrp
umask
```

重点做到可以看懂：

```text
-rwxr-xr--
```

并知道：

```text
chmod 755
chmod +x
chown user:group
```

---

## 第三阶段：进程

```text
ps
top
pgrep
pkill
kill
jobs
bg
fg
nohup
```

优先掌握：

```bash
ps aux
pgrep -af
kill PID
nohup command > log 2>&1 &
```

---

## 第四阶段：文本处理

这是后续写运维脚本最重要的阶段之一：

```text
grep
awk
sed
cut
sort
uniq
tr
xargs
tee
```

建议先按这个顺序：

```text
grep → cut → sort → uniq → awk → sed → xargs → tee
```

其中 `grep`、`awk`、`sed` 尤其值得重点学习。

---

## 第五阶段：日志与压缩

```text
journalctl
less
tail
head
tar
gzip
```

---

# 十五、重点命令速查表

| 命令 | 核心作用 | 最值得记的参数/写法 |
|---|---|---|
| ⭐ `ls` | 看目录 | `-lah`、`-lt` |
| ⭐ `cp` | 复制 | `-r`、`-a`、`-i` |
| ⭐ `mv` | 移动/重命名 | `-i`、`-v` |
| ⭐ `rm` | 删除 | `-r`、`-f`、`-i` |
| ⭐ `mkdir` | 创建目录 | `-p` |
| ⭐ `touch` | 创建/更新时间 | `-a`、`-m` |
| ⭐ `find` | 查找 | `-name`、`-type`、`-size`、`-mtime`、`-exec` |
| ⭐ `chmod` | 改权限 | `755`、`644`、`+x`、`-R` |
| ⭐ `chown` | 改所有者 | `user:group`、`-R` |
| ⭐ `ps` | 看进程 | `aux`、`-ef`、`-p` |
| ⭐ `top` | 动态看进程 | `-b -n 1`、`P`、`M` |
| ⭐ `kill` | 发信号 | `-15`、`-9` |
| ⭐ `killall` | 按名字发信号 | `-TERM`、`-9` |
| ⭐ `cat` | 输出文件 | `-n`、`-A` |
| `less` | 分页查看 | `-N`、`-S` |
| `tail` | 看末尾 | `-n`、`-f`、`-F` |
| `head` | 看开头 | `-n`、`-c` |
| ⭐ `grep` | 搜索文本 | `-i`、`-n`、`-v`、`-r`、`-E`、`-w`、`-C` |
| ⭐ `awk` | 按字段分析 | `-F`、`-v`、`NR`、`NF`、`$1`、`$2` |
| ⭐ `sed` | 替换/修改 | `s///g`、`-n`、`p`、`d`、`-i.bak` |
| ⭐ `cut` | 切字段 | `-d`、`-f`、`-c` |
| ⭐ `sort` | 排序 | `-n`、`-r`、`-k`、`-t`、`-h` |
| `uniq` | 去重/统计 | `-c`、`-d`、`-u` |
| `tr` | 字符转换/删除 | `-d`、`-s` |
| `xargs` | 组装参数 | `-n`、`-I`、`-0`、`-P` |
| ⭐ `tee` | 输出同时写文件 | `-a` |
| `journalctl` | systemd 日志 | `-u`、`-f`、`-n`、`-b`、`-p` |
| `tar` | 打包/解包 | `-c`、`-x`、`-t`、`-z`、`-f`、`-C` |
| `gzip` | gzip 压缩 | `-d`、`-k`、`-c`、`-1..-9` |

---

# 十六、最终形成你的 Linux 运维命令体系

可以把这些命令记成下面这张“脑图”：

```text
Linux 常用命令
│
├── 文件管理
│   ├── pwd
│   ├── ls
│   ├── cd
│   ├── cp
│   ├── mv
│   ├── rm
│   ├── mkdir
│   ├── touch
│   ├── find
│   ├── locate
│   ├── file
│   ├── stat
│   ├── du
│   ├── df
│   └── tree
│
├── 权限管理
│   ├── chmod
│   ├── chown
│   ├── chgrp
│   └── umask
│
├── 进程管理
│   ├── ps
│   ├── top
│   ├── htop
│   ├── pgrep
│   ├── pkill
│   ├── kill
│   ├── killall
│   ├── jobs
│   ├── bg
│   ├── fg
│   └── nohup
│
├── 文本与日志
│   ├── cat
│   ├── less
│   ├── head
│   ├── tail
│   ├── grep
│   ├── awk
│   ├── sed
│   └── journalctl
│
├── 文本流水线
│   ├── cut
│   ├── sort
│   ├── uniq
│   ├── tr
│   ├── xargs
│   └── tee
│
└── 打包压缩
    ├── tar
    └── gzip
```

---

# 十七、最值得先练的 20 条命令

如果你现在准备真正上手，而不是只看笔记，建议先反复敲下面这些：

```bash
pwd
ls -lah
cd /var/log
cp -av test.txt /tmp/
mv old.txt new.txt
mkdir -p project/{code,log,backup}
touch project/log/app.log
find project -type f -name '*.log'
chmod +x script.sh
chmod 755 script.sh
chown user:group file
ps aux | grep nginx
pgrep -af nginx
kill PID
tail -f app.log
grep -in 'error' app.log
awk '{print $1}' access.log
sed -n '1,20p' file.txt
sort file.txt | uniq -c | sort -nr
tar -czf backup.tar.gz project/
```

---

# 十八、学习这些命令时的最终目标

不要追求“把参数全部背下来”。

真正应该达到的是：

### 1. 看见需求，能马上想到命令

例如：

```text
“查找最近一天改过的日志”
        ↓
find
```

```text
“查日志里的 ERROR”
        ↓
grep
```

```text
“取日志第 1 列并统计排名”
        ↓
awk | sort | uniq
```

```text
“实时看日志”
        ↓
tail -f
```

```text
“看 nginx 是否在运行”
        ↓
pgrep / ps
```

```text
“结束一个进程”
        ↓
kill
```

```text
“给脚本执行权限”
        ↓
chmod +x
```

### 2. 能把多个命令串起来

真正的 Linux 运维经常不是：

```bash
只执行一个命令
```

而是：

```bash
命令 | 命令 | 命令
```

例如：

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
```

### 3. 能写成 Shell 脚本

最终你前面学习的：

```text
read
getopts
tee
条件判断
循环
函数
```

会和这里的命令结合起来，最终形成：

```text
Shell 脚本
   ↓
调用 Linux 命令
   ↓
获取结果
   ↓
判断
   ↓
处理
   ↓
输出日志
```

这才是这些命令真正的学习目的。

---

# 十九、一句话记忆版

```text
pwd    → 我在哪
ls     → 这里有什么
cd     → 去哪里
cp     → 复制
mv     → 移动/改名
rm     → 删除
mkdir  → 建目录
touch  → 建文件/更新时间
find   → 深度查找
locate → 快速查找
file   → 判断文件类型
stat   → 看文件详细状态
du     → 谁占空间
df     → 磁盘还剩多少

chmod  → 改权限
chown  → 改所有者
chgrp  → 改组
umask  → 控制新建权限

ps     → 看进程快照
top    → 动态看进程
pgrep  → 找 PID
pkill  → 按规则结束进程
kill   → 给 PID 发信号
killall→ 按名称发信号
jobs   → 看当前 Shell 作业
bg     → 放后台
fg     → 拉回前台
nohup  → 退出终端后继续跑

cat    → 直接看
less   → 分页看
head   → 看开头
tail   → 看结尾/实时跟踪
grep   → 找文本
awk    → 按字段分析
sed    → 按规则改文本
cut    → 切字段
sort   → 排序
uniq   → 去重/计数
tr     → 字符转换
xargs  → 文本变命令参数
tee    → 一边看一边写
journalctl → 看 systemd 日志

tar    → 打包/解包
gzip   → 压缩/解压
```

---

# 二十、重点学习建议

当前阶段建议优先把以下命令真正练熟：

```text
第一优先级：
ls / cp / mv / rm / mkdir / find
chmod / chown
ps / top / kill
cat / tail / grep

第二优先级：
awk / sed / cut / sort / uniq
tee / xargs
journalctl / tar

第三优先级：
locate / file / stat / du / df / tree
pgrep / pkill / jobs / bg / fg / nohup
tr / gzip
```

尤其需要形成下面四条“运维肌肉记忆”：

```bash
# 1. 查
find ... | grep ...

# 2. 看日志
tail -f logfile | grep ...

# 3. 做文本统计
awk ... | sort | uniq -c | sort -nr

# 4. 批量处理
find ... -print0 | xargs -0 ...
```

这四类组合掌握后，你会开始真正理解 Linux 运维中“命令行工具为什么强大”。
