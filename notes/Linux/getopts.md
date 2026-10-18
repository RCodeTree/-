# Shell `getopts` 命令学习笔记

## 1. 什么是 `getopts`

`getopts` 是 Shell 中用于**解析命令行参数**的内置命令。

例如，我们写一个脚本：

```bash
./test.sh -n rong -a 20
```

这里：

* `-n` 是一个选项
* `rong` 是 `-n` 对应的参数
* `-a` 是另一个选项
* `20` 是 `-a` 对应的参数

如果不用 `getopts`，我们就需要自己处理 `$1`、`$2`、`$3`……

而使用 `getopts` 后，就可以比较规范地处理：

```bash
-n rong
-a 20
-v
-h
```

所以，`getopts` 非常适合用于编写带有命令行选项的 Shell 脚本。

---

# 2. 最基本的使用格式

基本语法：

```bash
getopts "选项字符串" 变量名
```

最常见的写法：

```bash
while getopts "n:a:v" opt
do
    case "$opt" in
        n)
            echo "name: $OPTARG"
            ;;
        a)
            echo "age: $OPTARG"
            ;;
        v)
            echo "verbose"
            ;;
    esac
done
```

其中：

```bash
"n:a:v"
```

是最重要的部分。

---

# 3. 选项字符串是什么意思

例如：

```bash
getopts "n:a:v" opt
```

表示：

* `n:` → `-n` 后面必须跟一个参数
* `a:` → `-a` 后面必须跟一个参数
* `v` → `-v` 本身就是一个开关，不需要参数

因此可以这样使用：

```bash
./test.sh -n rong -a 20 -v
```

不能把 `v` 写成：

```bash
getopts "n:a:v:" opt
```

因为这样就代表：

```text
-v 也必须带一个参数
```

---

# 4. `:` 的作用

这是学习 `getopts` 最重要的知识之一。

## 4.1 没有冒号

例如：

```bash
getopts "v" opt
```

表示：

```text
-v
```

是一个不需要参数的选项。

调用：

```bash
./test.sh -v
```

---

## 4.2 有冒号

例如：

```bash
getopts "n:" opt
```

表示：

```text
-n
```

后面必须有参数。

例如：

```bash
./test.sh -n rong
```

这里：

```text
-n
```

是选项。

```text
rong
```

是参数。

---

# 5. `OPTARG` 变量

`OPTARG` 是 `getopts` 提供的一个重要变量。

当某个选项需要参数时，参数会自动保存到：

```bash
$OPTARG
```

例如：

```bash
#!/bin/bash

while getopts "n:" opt
do
    case "$opt" in
        n)
            echo "name = $OPTARG"
            ;;
    esac
done
```

执行：

```bash
./test.sh -n rong
```

输出：

```text
name = rong
```

执行过程可以理解成：

```text
-n
 ↓
getopts 识别到 n
 ↓
发现 n 后面有 :
 ↓
获取参数 rong
 ↓
保存到 OPTARG
```

所以：

```bash
$OPTARG
```

就是当前选项对应的参数。

---

# 6. `OPTIND` 变量

`OPTIND` 也是 `getopts` 中非常重要的变量。

它表示：

> 下一个要处理的命令行参数的位置。

默认情况下：

```bash
OPTIND=1
```

例如：

```bash
./test.sh -n rong -a 20 abc
```

大致可以理解成：

```text
$1   -n
$2   rong
$3   -a
$4   20
$5   abc
```

当 `getopts` 把选项解析完成以后：

```bash
OPTIND
```

会指向剩余参数的位置。

因此经常会看到：

```bash
shift $((OPTIND - 1))
```

---

# 7. 为什么经常使用 `shift`

假设执行：

```bash
./test.sh -n rong abc
```

其中：

```text
-n rong
```

是选项参数。

而：

```text
abc
```

是普通参数。

代码：

```bash
while getopts "n:" opt
do
    case "$opt" in
        n)
            echo "name=$OPTARG"
            ;;
    esac
done

shift $((OPTIND - 1))

echo "剩余参数：$@"
```

执行：

```bash
./test.sh -n rong abc
```

输出：

```text
name=rong
剩余参数：abc
```

原因是：

```bash
getopts
```

负责处理：

```text
-n rong
```

然后：

```bash
shift $((OPTIND - 1))
```

把已经处理过的选项从 `$@` 中移除。

这样剩下的就是普通参数。

---

# 8. 第一个基础案例：处理名字和年龄

创建：

```bash
test.sh
```

内容：

```bash
#!/bin/bash

while getopts "n:a:" opt
do
    case "$opt" in
        n)
            echo "姓名：$OPTARG"
            ;;
        a)
            echo "年龄：$OPTARG"
            ;;
    esac
done
```

添加执行权限：

```bash
chmod +x test.sh
```

执行：

```bash
./test.sh -n rong -a 20
```

输出：

```text
姓名：rong
年龄：20
```

---

# 9. 第二个案例：加入 `-v` 开关

现在增加一个：

```text
-v
```

用于表示详细模式。

代码：

```bash
#!/bin/bash

while getopts "n:a:v" opt
do
    case "$opt" in
        n)
            echo "姓名：$OPTARG"
            ;;
        a)
            echo "年龄：$OPTARG"
            ;;
        v)
            echo "开启详细模式"
            ;;
    esac
done
```

执行：

```bash
./test.sh -n rong -a 20 -v
```

输出：

```text
姓名：rong
年龄：20
开启详细模式
```

这里：

```bash
"n:a:v"
```

可以拆成：

```text
n:   -n 必须有参数
a:   -a 必须有参数
v    -v 不需要参数
```

---

# 10. 第三个案例：实现 `-h` 帮助选项

实际脚本中经常会有：

```text
-h
```

显示帮助。

例如：

```bash
#!/bin/bash

while getopts "n:a:vh" opt
do
    case "$opt" in
        n)
            echo "姓名：$OPTARG"
            ;;
        a)
            echo "年龄：$OPTARG"
            ;;
        v)
            echo "开启详细模式"
            ;;
        h)
            echo "用法：$0 [-n name] [-a age] [-v] [-h]"
            exit 0
            ;;
        \?)
            echo "未知选项"
            exit 1
            ;;
    esac
done
```

执行：

```bash
./test.sh -h
```

输出：

```text
用法：./test.sh [-n name] [-a age] [-v] [-h]
```

这里：

```bash
$0
```

代表脚本本身的名称。

例如：

```bash
./test.sh
```

那么：

```bash
$0
```

就是：

```text
./test.sh
```

---

# 11. `case` 是如何配合 `getopts` 使用的

最经典的结构就是：

```bash
while getopts "n:a:vh" opt
do
    case "$opt" in
        n)
            ;;
        a)
            ;;
        v)
            ;;
        h)
            ;;
        \?)
            ;;
    esac
done
```

假设执行：

```bash
./test.sh -n rong -a 20 -v
```

`getopts` 会不断获取选项：

第一次：

```text
opt=n
OPTARG=rong
```

第二次：

```text
opt=a
OPTARG=20
```

第三次：

```text
opt=v
```

因此：

```bash
case "$opt" in
```

就可以根据不同的选项执行不同代码。

---

# 12. 一个更加完整的实战案例

下面写一个比较接近实际运维脚本的例子。

需求：

```text
-n 用户名
-a 年龄
-v 详细模式
-h 帮助
```

代码：

```bash
#!/bin/bash

name=""
age=""
verbose=0

while getopts "n:a:vh" opt
do
    case "$opt" in
        n)
            name="$OPTARG"
            ;;
        a)
            age="$OPTARG"
            ;;
        v)
            verbose=1
            ;;
        h)
            echo "用法：$0 [-n name] [-a age] [-v] [-h]"
            exit 0
            ;;
        \?)
            echo "错误：未知选项 -$OPTARG"
            exit 1
            ;;
    esac
done

echo "姓名：$name"
echo "年龄：$age"

if [ "$verbose" -eq 1 ]; then
    echo "详细模式：开启"
fi
```

执行：

```bash
./test.sh -n rong -a 20
```

输出：

```text
姓名：rong
年龄：20
```

执行：

```bash
./test.sh -n rong -a 20 -v
```

输出：

```text
姓名：rong
年龄：20
详细模式：开启
```

执行：

```bash
./test.sh -h
```

输出：

```text
用法：./test.sh [-n name] [-a age] [-v] [-h]
```

---

# 13. 处理未知选项

例如我们的程序只支持：

```text
-n
-a
-v
-h
```

如果用户执行：

```bash
./test.sh -x
```

那么 `x` 是未知选项。

通常可以这样写：

```bash
\?)
    echo "未知选项：-$OPTARG"
    exit 1
    ;;
```

完整代码：

```bash
while getopts "n:a:vh" opt
do
    case "$opt" in
        n)
            ;;
        a)
            ;;
        v)
            ;;
        h)
            ;;
        \?)
            echo "未知选项：-$OPTARG"
            exit 1
            ;;
    esac
done
```

---

# 14. 处理“选项缺少参数”

例如：

```bash
getopts "n:" opt
```

表示：

```text
-n 必须有参数
```

如果用户只输入：

```bash
./test.sh -n
```

那么 `-n` 后面缺少参数。

这里就涉及 `getopts` 的错误处理模式。

---

# 15. 两种错误处理模式

`getopts` 的选项字符串最前面可以放一个：

```text
:
```

例如：

```bash
getopts ":n:a:" opt
```

这个冒号非常特殊。

它可以让脚本自己处理错误，而不是让 Shell 直接打印错误信息。

---

# 16. 不加前置 `:` 的情况

例如：

```bash
while getopts "n:" opt
do
    case "$opt" in
        n)
            echo "name=$OPTARG"
            ;;
        \?)
            echo "未知选项"
            ;;
    esac
done
```

执行：

```bash
./test.sh -x
```

通常会出现类似：

```text
./test.sh: illegal option -- x
未知选项
```

也就是说：

```text
getopts
```

本身会产生错误提示。

---

# 17. 加前置 `:` 的情况

改成：

```bash
while getopts ":n:" opt
do
    case "$opt" in
        n)
            echo "name=$OPTARG"
            ;;
        \?)
            echo "未知选项：-$OPTARG"
            ;;
        :)
            echo "选项 -$OPTARG 缺少参数"
            ;;
    esac
done
```

这里出现了两个特殊情况：

```bash
\?)
```

表示：

> 出现未知选项

例如：

```bash
-x
```

会进入：

```bash
\?)
```

而：

```bash
:)
```

表示：

> 选项存在，但是缺少参数

例如：

```bash
-n
```

会进入：

```bash
:)
```

---

# 18. 推荐的错误处理写法

实际写 Shell 脚本时，可以使用下面这种模式：

```bash
#!/bin/bash

while getopts ":n:a:vh" opt
do
    case "$opt" in
        n)
            name="$OPTARG"
            ;;
        a)
            age="$OPTARG"
            ;;
        v)
            verbose=1
            ;;
        h)
            echo "用法：$0 [-n name] [-a age] [-v] [-h]"
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
```

这种结构在实际脚本中非常常见。

---

# 19. 同一个选项可以同时写在一起吗？

可以。

例如：

```bash
./test.sh -n rong -a 20
```

也可以写成：

```bash
./test.sh -nrong -a20
```

甚至某些情况下可以组合不需要参数的短选项：

```bash
./test.sh -vh
```

它可以被理解为：

```text
-v
-h
```

但是对于初学阶段，推荐写得清楚一些：

```bash
./test.sh -v -h
```

这样更容易阅读和排错。

---

# 20. `getopts` 和 `$1 $2 $3` 的区别

不用 `getopts`：

```bash
#!/bin/bash

echo "第一个参数：$1"
echo "第二个参数：$2"
echo "第三个参数：$3"
```

执行：

```bash
./test.sh rong 20 male
```

这种方式比较适合固定参数。

例如：

```text
./test.sh 文件名 用户名
```

参数顺序必须固定。

---

使用 `getopts`：

```bash
./test.sh -n rong -a 20
```

则更加灵活。

甚至可以交换顺序：

```bash
./test.sh -a 20 -n rong
```

脚本都可以正常解析。

所以：

```text
$1 $2 $3
```

更适合：

> 普通位置参数

而：

```text
getopts
```

更适合：

> 命令行选项

---

# 21. `getopts` + 普通参数

实际工作中，经常同时存在：

```bash
选项参数
+
普通参数
```

例如：

```bash
./backup.sh -v -d /backup file1.txt file2.txt
```

其中：

```text
-v
-d /backup
```

是选项。

而：

```text
file1.txt
file2.txt
```

是普通参数。

代码：

```bash
#!/bin/bash

verbose=0
directory=""

while getopts "vd:" opt
do
    case "$opt" in
        v)
            verbose=1
            ;;
        d)
            directory="$OPTARG"
            ;;
        \?)
            echo "未知选项"
            exit 1
            ;;
        :)
            echo "选项 -$OPTARG 缺少参数"
            exit 1
            ;;
    esac
done

shift $((OPTIND - 1))

echo "目录：$directory"
echo "详细模式：$verbose"

echo "剩余参数："

for file in "$@"
do
    echo "$file"
done
```

执行：

```bash
./backup.sh -v -d /backup file1.txt file2.txt
```

输出：

```text
目录：/backup
详细模式：1
剩余参数：
file1.txt
file2.txt
```

这里就体现出：

```bash
shift $((OPTIND - 1))
```

的作用。

---

# 22. `OPTIND` + `shift` 的核心理解

可以把整个过程理解成：

```text
命令：

./test.sh -v -d /backup a.txt b.txt
                  ↑
                选项
```

首先：

```bash
getopts
```

处理：

```text
-v
-d /backup
```

然后：

```bash
OPTIND
```

记录已经解析到哪里。

最后：

```bash
shift $((OPTIND - 1))
```

把这些已经处理过的选项移走。

于是：

```bash
$@
```

就只剩：

```text
a.txt b.txt
```

---

# 23. 常用特殊变量总结

| 变量        | 含义                 |
| --------- | ------------------ |
| `$OPTARG` | 当前选项对应的参数          |
| `$OPTIND` | 下一个待解析参数的位置        |
| `$opt`    | 当前 `getopts` 返回的选项 |
| `$@`      | 所有命令行参数            |
| `$#`      | 命令行参数总数            |
| `$0`      | 当前脚本名称             |

其中最重要的是：

```bash
$OPTARG
$OPTIND
```

---

# 24. 一个标准模板

以后写 Shell 脚本，可以直接参考这个模板：

```bash
#!/bin/bash

while getopts ":a:b:vh" opt
do
    case "$opt" in
        a)
            echo "参数 a：$OPTARG"
            ;;
        b)
            echo "参数 b：$OPTARG"
            ;;
        v)
            echo "开启详细模式"
            ;;
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

echo "剩余参数：$@"
```

例如：

```bash
./test.sh -a 100 -b 200 -v file1 file2
```

---

# 25. `getopts` 的使用流程

以后看到 `getopts`，可以按照下面这个思路理解：

```text
1. 定义支持哪些选项
        ↓
2. 使用 getopts 逐个读取
        ↓
3. 当前选项保存到 opt
        ↓
4. 如果选项需要参数
        ↓
5. 参数保存到 OPTARG
        ↓
6. 使用 case 判断 opt
        ↓
7. 处理未知选项和缺少参数
        ↓
8. shift $((OPTIND - 1))
        ↓
9. 继续处理剩余普通参数
```

---

# 26. 最重要的记忆点

学习 `getopts` 时，先记住下面几个东西就够了。

## ① 选项字符串

```bash
"n:a:v"
```

表示：

```text
-n 需要参数
-a 需要参数
-v 不需要参数
```

---

## ② `OPTARG`

```bash
-n rong
```

那么：

```bash
$OPTARG
```

就是：

```text
rong
```

---

## ③ `case`

通常这样处理：

```bash
case "$opt" in
    n)
        ;;
    a)
        ;;
    v)
        ;;
esac
```

---

## ④ 前置冒号

```bash
":n:a:v"
```

让我们自己处理错误。

其中：

```bash
\?)
```

表示：

```text
未知选项
```

而：

```bash
:)
```

表示：

```text
缺少参数
```

---

## ⑤ `OPTIND`

```bash
shift $((OPTIND - 1))
```

用于把已经被 `getopts` 处理过的选项移走，从而继续处理剩余普通参数。

---

# 27. `getopts` 常见应用场景

在 Linux 运维和 Shell 脚本中非常常见，例如：

```bash
./backup.sh -d /data -v
```

```bash
./monitor.sh -h -t 10
```

```bash
./install.sh -p /usr/local -y
```

```bash
./user.sh -u root -g wheel
```

其中：

```text
-h
-v
-y
```

通常属于“开关型选项”。

而：

```text
-d /data
-t 10
-p /usr/local
-u root
-g wheel
```

通常属于“带参数的选项”。

---

# 28. `getopts` 和 `getopt` 的区别

特别注意：

```text
getopts
```

和：

```text
getopt
```

不是一回事。

### `getopts`

是 Shell 内置命令：

```bash
help getopts
```

就可以查看帮助。

主要用于 Shell 脚本内部解析命令行选项。

---

### `getopt`

通常是 Linux 系统中的一个外部命令：

```bash
getopt
```

它的功能更加复杂，常用于参数重新排列和更复杂的参数解析场景。

初学 Shell 时，优先掌握：

```bash
getopts
```

即可。

---

# 29. 最终实战模板

可以把下面代码作为自己以后写脚本时的基础模板：

```bash
#!/bin/bash

name=""
age=""
verbose=0

while getopts ":n:a:vh" opt
do
    case "$opt" in
        n)
            name="$OPTARG"
            ;;
        a)
            age="$OPTARG"
            ;;
        v)
            verbose=1
            ;;
        h)
            echo "用法：$0 [-n name] [-a age] [-v] [-h]"
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

echo "===================="
echo "姓名：$name"
echo "年龄：$age"
echo "详细模式：$verbose"
echo "剩余参数：$@"
echo "===================="
```

测试：

```bash
./test.sh -n rong -a 20 -v file1.txt file2.txt
```

最终可以形成这样的结构：

```text
                Shell脚本
                    │
              ┌─────┴─────┐
              │           │
           getopts      普通参数
              │           │
       ┌──────┼──────┐    │
       │      │      │    │
      -n     -a     -v   file
       │      │      │
     OPTARG OPTARG  开关
```

---

# 30. 一句话总结

`getopts` 可以简单理解为：

> **专门帮助 Shell 脚本解析 `-a`、`-b value`、`-v` 这类命令行选项的工具。**

最核心的代码结构就是：

```bash
while getopts ":a:b:vh" opt
do
    case "$opt" in
        a)
            ;;
        b)
            ;;
        v)
            ;;
        h)
            ;;
        \?)
            ;;
        :)
            ;;
    esac
done

shift $((OPTIND - 1))
```

只要把这套结构真正理解了，后面写各种运维 Shell 脚本时就可以直接套用。

这份笔记的重点是先把 **`getopts`、`OPTARG`、`OPTIND`、`case`、`shift`** 这几个核心概念串起来。后面你学习 Shell 脚本时，可以继续把它扩展到“带默认值、参数校验、帮助函数、日志参数、配置文件参数”等更实用的写法。
