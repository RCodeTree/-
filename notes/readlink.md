# readlink 命令详解

> 本文以 GNU coreutils 的 `readlink` 为主，兼顾 BSD/macOS 差异。

## 1. 简介

`readlink` 用于读取符号链接（symbolic link）的目标路径，也可以配合选项对路径进行规范化处理。

默认情况下，`readlink` 只读取符号链接本身存储的目标字符串，**不会递归解析**后续符号链接。  
加上 `-f`、`-e`、`-m` 等选项后，它可以像 `realpath` 一样输出规范化后的绝对路径。

---

## 2. 语法

```bash
readlink [选项]... [文件]...
```

常见形式：

```bash
readlink symlink
readlink -f path
readlink -e path
readlink -m path
```

---

## 3. 核心概念

### 3.1 符号链接

符号链接是一种特殊文件，它保存的是另一个路径的字符串。

例如：

```bash
ln -s /usr/bin/python3 /tmp/python
```

此时 `/tmp/python` 是一个符号链接，指向 `/usr/bin/python3`。

### 3.2 默认行为

```bash
readlink /tmp/python
```

输出：

```text
/usr/bin/python3
```

如果参数不是符号链接，默认通常不输出内容，并返回非零状态。

---

## 4. 常用选项

| 选项 | 说明 |
| --- | --- |
| `-f, --canonicalize` | 递归解析所有符号链接，输出规范绝对路径；除最后一个组件外，其余组件必须存在 |
| `-e, --canonicalize-existing` | 类似 `-f`，但所有组件都必须存在 |
| `-m, --canonicalize-missing` | 不要求路径组件存在，直接输出规范化路径 |
| `-n, --no-newline` | 不输出末尾换行 |
| `-q, --quiet` | 抑制错误信息 |
| `-s, --silent` | 同 `-q` |
| `-v, --verbose` | 显示错误信息 |
| `-z, --zero` | 以 NUL 字符结尾，而不是换行 |
| `--help` | 显示帮助 |
| `--version` | 显示版本 |

> 注意：`-e`、`-m`、`-q`、`-s`、`-v`、`-z` 等通常是 GNU 扩展。  
> macOS/BSD 上的 `readlink` 选项可能较少，行为也可能不同。

---

## 5. 工作原理

### 5.1 默认模式

```bash
readlink link
```

只读取 `link` 这个符号链接中保存的目标字符串。

如果 `link` 指向另一个符号链接，默认不会继续解析。

### 5.2 `-f` 模式

```bash
readlink -f link
```

会：

1. 从根目录开始规范化路径；
2. 递归解析每一级符号链接；
3. 处理 `.` 和 `..`；
4. 输出绝对路径；
5. 除最后一个组件外，其余组件必须存在。

### 5.3 `-e` 模式

```bash
readlink -e path
```

要求路径中所有组件都必须存在，否则失败。

### 5.4 `-m` 模式

```bash
readlink -m path
```

不要求任何组件存在，只做规范化计算。

---

## 6. 常见示例

### 6.1 查看符号链接目标

```bash
ln -s /usr/bin/python3 /tmp/python
readlink /tmp/python
```

输出：

```text
/usr/bin/python3
```

### 6.2 递归解析符号链接

```bash
ln -s /tmp/python /tmp/python2
readlink /tmp/python2
```

输出：

```text
/tmp/python
```

继续使用 `-f`：

```bash
readlink -f /tmp/python2
```

输出：

```text
/usr/bin/python3
```

### 6.3 获取绝对路径

```bash
readlink -f ./some/relative/path
```

即使参数是相对路径，也会输出规范化后的绝对路径。

### 6.4 存在性要求

```bash
readlink -e /tmp/nonexistent
```

如果路径不存在，会失败，通常无输出。

```bash
readlink -m /tmp/nonexistent
```

输出：

```text
/tmp/nonexistent
```

### 6.5 在脚本中获取自身路径

```bash
SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
echo "$SCRIPT_DIR"
```

如果脚本是通过 `PATH` 执行的，`$0` 可能只是脚本名，此时 `readlink -f "$0"` 可能不可靠。可以结合 `command -v`：

```bash
SCRIPT_PATH=$(readlink -f "$(command -v "$0")")
```

### 6.6 处理多个文件

```bash
readlink -f link1 link2 link3
```

每个结果输出一行。

### 6.7 NUL 分隔输出

```bash
readlink -z link1 link2 | xargs -0 -n1 echo
```

适合文件名中包含空格或换行的情况。

### 6.8 静默与详细模式

```bash
readlink -q /etc/passwd
readlink -v /etc/passwd
```

`-v` 可能输出类似：

```text
readlink: /etc/passwd: Invalid argument
```

---

## 7. 与 realpath 对比

| 命令 | 默认行为 | 是否允许路径缺失 | 备注 |
| --- | --- | --- | --- |
| `readlink` | 只读取符号链接目标 | 默认不处理非链接 | 选项因平台而异 |
| `readlink -f` | 规范化并递归解析 | 最后组件可缺失 | GNU 扩展 |
| `readlink -e` | 规范化并递归解析 | 所有组件必须存在 | GNU 扩展 |
| `readlink -m` | 规范化并递归解析 | 所有组件都可缺失 | GNU 扩展 |
| `realpath` | 输出规范绝对路径 | 默认所有组件必须存在 | 更现代 |
| `realpath -m` | 输出规范绝对路径 | 所有组件都可缺失 | 类似 `readlink -m` |

简单理解：

- `readlink` 默认：看链接指向哪里。
- `readlink -f`：解析成最终绝对路径。
- `realpath`：更偏向直接获取规范绝对路径。

---

## 8. 跨平台注意事项

### 8.1 GNU/Linux

GNU coreutils 提供的 `readlink` 功能较完整，支持 `-f`、`-e`、`-m`、`-n`、`-q`、`-v`、`-z` 等。

### 8.2 macOS / BSD

macOS/BSD 的 `readlink` 选项通常较少，某些 GNU 选项可能不存在或行为不同。

如果需要 GNU 行为，可以安装 coreutils：

```bash
brew install coreutils
```

然后使用：

```bash
greadlink -f path
```

### 8.3 可移植替代方案

如果只想获取绝对路径，可以用：

```bash
abs=$(cd "$(dirname "$file")" && pwd -P)/$(basename "$file")
```

或者使用 Python：

```bash
python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$file"
```

---

## 9. 安全与陷阱

1. **TOCTOU 竞争条件**  
   先用 `readlink` 检查路径，再使用该路径，期间链接可能被替换。对安全敏感场景要小心。

2. **符号链接循环**  
   如果符号链接形成循环，`readlink -f` 通常会报错，例如 `Too many levels of symbolic links`。

3. **权限问题**  
   解析路径需要相应目录的执行权限。

4. **`$0` 的不可靠性**  
   脚本通过 `PATH` 执行时，`$0` 可能不是完整路径，建议结合 `command -v`。

5. **不要过度依赖 GNU 扩展**  
   如果脚本需要跨 Linux、macOS、BSD 运行，应避免直接使用 `readlink -f`，或提供兼容函数。

---

## 10. 总结

`readlink` 是处理符号链接和路径规范化的常用命令。

- 默认：读取符号链接目标，不递归。
- `-f`：递归解析并输出规范绝对路径，最后组件可不存在。
- `-e`：要求所有组件存在。
- `-m`：不要求任何组件存在。
- `-n`：不输出换行。
- `-z`：输出 NUL 分隔，适合脚本处理特殊文件名。

在 Linux 上非常实用，但在 macOS/BSD 上要注意兼容性。脚本中如需跨平台，建议使用 `realpath`、`greadlink` 或自行实现兼容逻辑。

---

参考：

- `man readlink`
- GNU coreutils 文档
- `man realpath`