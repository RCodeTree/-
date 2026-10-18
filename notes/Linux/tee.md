# Linux `tee` 命令学习笔记

## 1. 什么是 `tee`

`tee` 用于：

> **将标准输入同时输出到屏幕和文件。**

可以简单理解为：

```text
输入
 ↓
tee
 ↙ ↘
屏幕  文件
```

---

## 2. 基本语法

```bash
command | tee 文件名
```

例如：

```bash
echo "hello" | tee test.txt
```

结果：

```text
hello
```

同时 `test.txt` 中也会保存：

```text
hello
```

---

## 3. 覆盖文件

默认情况下：

```bash
tee test.txt
```

会覆盖原文件内容。

例如：

```bash
echo "hello" | tee test.txt
echo "world" | tee test.txt
```

最终 `test.txt`：

```text
world
```

---

## 4. 追加文件

使用：

```bash
tee -a 文件名
```

例如：

```bash
echo "hello" | tee test.txt
echo "world" | tee -a test.txt
```

最终：

```text
hello
world
```

所以：

```bash
tee 文件
```

表示覆盖。

```bash
tee -a 文件
```

表示追加。

---

## 5. 常见案例

### 案例 1：记录命令输出

```bash
df -h | tee disk.log
```

作用：

```text
df -h 的结果
    ↓
屏幕显示
    +
保存到 disk.log
```

---

### 案例 2：追加日志

```bash
date | tee -a system.log
```

每执行一次，就向 `system.log` 追加一行。

---

### 案例 3：查看并保存脚本输出

```bash
./test.sh | tee test.log
```

非常适合调试脚本。

---

## 6. `tee` 与重定向的区别

普通重定向：

```bash
echo "hello" > test.txt
```

结果：

```text
文件有内容
屏幕没有输出
```

而：

```bash
echo "hello" | tee test.txt
```

结果：

```text
文件有内容
屏幕也有输出
```

可以记成：

```text
>       只写文件
tee     屏幕 + 文件
```

---

## 7. `tee` 的一个重要用途：`sudo`

有时候下面的命令会失败：

```bash
sudo echo "hello" > /root/test.txt
```

因为 `>` 重定向不是由 `sudo` 执行的。

可以改成：

```bash
echo "hello" | sudo tee /root/test.txt
```

追加则：

```bash
echo "hello" | sudo tee -a /root/test.txt
```

---

## 8. 常用选项

| 选项   | 作用     |
| ---- | ------ |
| `-a` | 追加到文件  |
| `-i` | 忽略中断信号 |

最常用的就是：

```bash
tee -a
```

---

## 9. 记忆总结

```bash
command | tee file
```

表示：

> **命令结果同时显示并写入文件。**

```bash
command | tee -a file
```

表示：

> **命令结果同时显示，并追加到文件。**

最核心的两个用法：

```bash
echo "hello" | tee test.txt
echo "hello" | tee -a test.txt
```
