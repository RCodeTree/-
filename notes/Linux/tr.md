`tr` 是 Linux coreutils 里的字符级流处理工具，名字来自 **translate**。它从标准输入读数据，向标准输出写结果，主要做三件事：

1. **替换字符**：把 `SET1` 中的字符映射为 `SET2` 中对应字符；
2. **删除字符**：删除 `SET1` 中的字符；
3. **压缩重复字符**：把连续重复的字符压成一个。

它**不直接接收文件名**，也不修改原文件，通常配合重定向或管道使用：

```bash
tr [选项] SET1 [SET2] < 输入文件 > 输出文件
cat file | tr [选项] SET1 [SET2]
```

---

## 一、常用选项

| 选项 | 含义 |
|---|---|
| `-c` / `-C` / `--complement` | 取 `SET1` 的补集 |
| `-d` / `--delete` | 删除 `SET1` 中的字符 |
| `-s` / `--squeeze-repeats` | 压缩连续重复字符 |
| `-t` / `--truncate-set1` | 将 `SET1` 截断为 `SET2` 的长度 |
| `--help` | 帮助 |
| `--version` | 版本 |

组合含义要特别注意：

- `tr -d SET1`：删除 `SET1` 中的字符；
- `tr -s SET1`：压缩 `SET1` 中连续重复字符；
- `tr SET1 SET2`：把 `SET1` 替换为 `SET2`；
- `tr -s SET1 SET2`：先替换，再压缩 `SET2` 中连续重复字符；
- `tr -ds SET1 SET2`：先删除 `SET1`，再压缩 `SET2` 中连续重复字符；
- `tr -cd SET1`：删除 `SET1` 的补集，也就是“只保留 `SET1`”。

---

## 二、SET 字符集写法

`SET1`、`SET2` 可以包含以下形式：

| 写法 | 含义 | 示例 |
|---|---|---|
| 普通字符 | 单个字符 | `abc` |
| 范围 | 连续字符范围 | `a-z`、`0-9`、`A-Z` |
| 转义字符 | 特殊字符 | `\n`、`\t`、`\r`、`\\` |
| 八进制 | 字符编码 | `\012` 表示换行 |
| 字符类 | POSIX 字符类 | `[:digit:]`、`[:space:]` |
| 等价类 | 等价字符 | `[=c=]` |
| GNU 重复 | 重复字符填充 | `[x*]`、`[x*5]` |

常见转义：

| 转义 | 含义 |
|---|---|
| `\n` | 换行 |
| `\t` | 制表符 |
| `\r` | 回车 |
| `\b` | 退格 |
| `\f` | 换页 |
| `\v` | 垂直制表 |
| `\\` | 反斜杠 |
| `\ooo` | 八进制字符，如 `\012` 是换行 |
| `\a` | 响铃 |

常见 POSIX 字符类：

| 字符类 | 含义 |
|---|---|
| `[:alnum:]` | 字母和数字 |
| `[:alpha:]` | 字母 |
| `[:blank:]` | 水平空白：空格、Tab |
| `[:cntrl:]` | 控制字符 |
| `[:digit:]` | 数字 |
| `[:graph:]` | 可打印且非空白 |
| `[:lower:]` | 小写字母 |
| `[:print:]` | 可打印字符 |
| `[:punct:]` | 标点符号 |
| `[:space:]` | 空白：空格、Tab、换行、回车等 |
| `[:upper:]` | 大写字母 |
| `[:xdigit:]` | 十六进制数字 |

注意：**不要给整个 SET 加外层方括号**。  
正确：

```bash
tr 'a-z' 'A-Z'
tr '[:lower:]' '[:upper:]'
```

错误：

```bash
tr '[a-z]' '[A-Z]'
```

因为 `tr` 会把 `[`、`]` 也当成普通字符处理。

---

## 三、常见用法示例

### 1. 大小写转换

```bash
echo 'Hello World' | tr 'a-z' 'A-Z'
# HELLO WORLD

echo 'Hello World' | tr '[:lower:]' '[:upper:]'
# HELLO WORLD

echo 'HELLO' | tr 'A-Z' 'a-z'
# hello
```

### 2. 删除字符

删除 Windows 换行中的回车符：

```bash
tr -d '\r' < dos.txt > unix.txt
```

删除数字：

```bash
echo 'a1b2c3' | tr -d '[:digit:]'
# abc
```

删除所有空白：

```bash
tr -d '[:space:]' < file
```

删除换行，把多行合并：

```bash
tr -d '\n' < file
```

### 3. 只保留某些字符

只保留数字：

```bash
echo 'a1b2c3' | tr -cd '[:digit:]'
# 123
```

只保留数字和换行：

```bash
tr -cd '0-9\n' < file
```

只保留可打印字符和换行：

```bash
tr -cd '[:print:]\n' < file
```

### 4. 压缩连续重复字符

多个空格压成一个：

```bash
echo 'a     b' | tr -s ' '
# a b
```

多个空行压成一个：

```bash
printf 'a\n\n\nb\n' | tr -s '\n'
# a
# b
```

把所有空白统一替换为空格并压缩：

```bash
tr -s '[:space:]' ' ' < file
```

把所有空白统一替换为换行并压缩：

```bash
tr -s '[:space:]' '\n' < file
```

经典分词：

```bash
echo 'a,b  c' | tr -cs '[:alnum:]' '\n'
# a
# b
# c
```

### 5. 字符替换

逗号替换为 Tab：

```bash
echo 'a,b,c' | tr ',' '\t'
```

空格替换为换行：

```bash
echo 'a b c' | tr ' ' '\n'
# a
# b
# c
```

换行替换为逗号：

```bash
tr '\n' ',' < file
```

### 6. 删除非字母数字，替换为空格

```bash
echo 'Hello, World!' | tr -c '[:alnum:]\n' ' '
# Hello  World
```

### 7. ROT13 简单加密

```bash
echo 'Hello' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
# Uryyb
```

### 8. SET2 长度规则与 `-t`

```bash
echo 'abc' | tr 'abc' 'x'
# xxx
```

默认情况下，`SET2` 不够长时，会重复最后一个字符。

使用 `-t` 截断 `SET1`：

```bash
echo 'abc' | tr -t 'abc' 'x'
# xbc
```

只把 `a` 映射为 `x`，后面的 `b`、`c` 不变。

GNU 扩展的重复填充：

```bash
echo 'abc' | tr 'abc' '[x*]'
# xxx

echo 'abc' | tr 'abc' '[x*2]y'
# xxy
```

---

## 四、重要注意事项

1. **tr 只处理标准输入和标准输出**  
   不能这样写：
   ```bash
   tr 'a-z' 'A-Z' file.txt   # 错误
   ```
   应写成：
   ```bash
   tr 'a-z' 'A-Z' < file.txt
   cat file.txt | tr 'a-z' 'A-Z'
   ```

2. **不能原地修改文件**  
   要修改原文件，通常用临时文件：
   ```bash
   tr 'a-z' 'A-Z' < file.txt > tmp && mv tmp file.txt
   ```

3. **字符范围受 locale 影响**  
   处理 ASCII 时建议：
   ```bash
   LC_ALL=C tr 'a-z' 'A-Z'
   ```

4. **对 UTF-8 多字节字符支持有限**  
   `tr` 更适合 ASCII/单字节字符处理。中文、emoji 等复杂文本建议用 `sed`、`perl` 或 `awk`。

5. **`-c` 和 `-d` 连用是“保留”**  
   ```bash
   tr -cd '[:digit:]'
   ```
   含义是：删除数字的补集，即只保留数字。

6. **`-s` 压缩的是“最后指定的 SET”**  
   - `tr -s ' '`：压缩连续空格；
   - `tr -s '[:space:]' ' '`：先把所有空白替换为空格，再压缩连续空格；
   - `tr -s '[:space:]' '\n'`：先把所有空白替换为换行，再压缩连续换行。

7. **`tr` 不支持正则表达式和字符串替换**  
   它只做字符级映射、删除、压缩。复杂替换请用：
   ```bash
   sed
   awk
   perl
   ```

---

## 五、总结

`tr` 的核心就是：

```bash
tr [选项] SET1 [SET2]
```

它适合做：

- 大小写转换；
- 删除回车、空白、数字、标点；
- 压缩连续空格、空行；
- 字符替换，如逗号转 Tab、空格转换行；
- 保留或删除某类字符；
- 简单的字符级加密，如 ROT13。

记住一句话：**`tr` 是字符级工具，不是正则工具；它只从 stdin 读，往 stdout 写。**