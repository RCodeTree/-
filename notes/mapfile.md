# mapfile 命令详解

> 本文以 Bash 内建命令 `mapfile` 为主，兼顾与 `readarray` 的关系、版本差异及实战陷阱。

## 1. 简介

`mapfile` 是 Bash 4.0 引入的内建命令，用于将标准输入或文件描述符中的行读取到索引数组中。它比传统的 `while read` 循环读取文件并填充数组的方式更高效，因为它以内建方式实现，且使用块缓冲 I/O，避免了逐行调用外部命令或子 shell 的开销。

`readarray` 是 `mapfile` 的同义词，二者功能完全一致。命令的默认数组变量名为 `MAPFILE`，如果不指定数组名，读取的内容会存入该变量。

---

## 2. 语法

```bash
mapfile [选项]... [array]

# 或使用同义词
readarray [选项]... [array]
```

`array` 是可选参数，指定用于接收数据的数组名称。如果省略，则使用默认数组 `MAPFILE`。

---

## 3. 选项详解

| 选项 | 说明 | 备注 |
| --- | --- | --- |
| `-d delim` | 将 `delim` 的第一个字符作为行分隔符，代替默认的换行符 | Bash 4.4+ 支持；若 `delim` 为空字符串，则以 NUL 字符（`\0`）分隔 |
| `-n count` | 最多读取 `count` 行；`count` 为 `0` 时读取全部 | |
| `-O origin` | 从数组下标 `origin` 处开始赋值，默认从 0 开始 | 使用 `-O` 时不会自动清空数组 |
| `-s count` | 跳过前 `count` 行再开始读取 | |
| `-t` | 移除每行末尾的分隔符（默认移除换行符） | 使用 `-d` 时则移除指定的分隔符 |
| `-u fd` | 从文件描述符 `fd` 读取，而不是从标准输入 | |
| `-C callback` | 每读取 `quantum` 行后，执行 `callback` 语句 | 与 `-c` 配合使用 |
| `-c quantum` | 指定调用 `callback` 的行数间隔，默认值为 5000 | 仅在使用 `-C` 时有效 |

选项详细信息参考。

---

## 4. 工作原理

### 4.1 默认行为

```bash
mapfile < file.txt
```

从标准输入逐行读取，每行作为一个数组元素存入默认数组 `MAPFILE`。数组下标从 0 开始。

### 4.2 指定数组名

```bash
mapfile myArray < file.txt
```

将读取的行存入名为 `myArray` 的数组。数组名必须是 `mapfile` 的**最后一个参数**。

### 4.3 数组清空规则

如果**未使用** `-O` 选项，`mapfile` 会在赋值前自动清空目标数组。如果使用了 `-O`，则不会清空数组，而是在指定下标处开始覆盖或追加。

### 4.4 回调机制

使用 `-C callback -c quantum` 时，每读取 `quantum` 行，Bash 会执行一次 `callback`。执行时，会向 `callback` 传递两个额外参数：下一个要赋值的数组下标，以及即将赋给该元素的行内容。`callback` 在行读取之后、赋值之前执行。

---

## 5. 常见示例

### 5.1 将文件读入数组

```bash
mapfile -t lines < file.txt
echo "${#lines[@]}"        # 输出行数
echo "${lines[0]}"         # 输出第一行
```

`-t` 移除每行末尾的换行符，这是最常用的组合。

### 5.2 从命令输出读取

```bash
mapfile -t files < <(ls -1)
```

使用进程替换 `< <(command)` 而不是管道 `|`。管道会使 `mapfile` 在子 shell 中执行，导致数组无法传递到当前 shell。

### 5.3 只读取前 N 行

```bash
mapfile -n 5 -t first5 < file.txt
```

### 5.4 跳过前 N 行

```bash
mapfile -s 3 -t lines < file.txt
```

### 5.5 从指定下标开始赋值

```bash
mapfile -O 2 -t arr < file.txt
```

从 `arr[2]` 开始存放，原有 `arr[0]` 和 `arr[1]` 保持不变。

### 5.6 自定义分隔符

```bash
# 以 NUL 字符分隔（适用于 find -print0 等）
mapfile -d '' -t files < <(find . -name "*.sh" -print0)

# 以制表符分隔
mapfile -d $'\t' -t fields < file.txt
```

`-d ''`（空字符串）表示以 NUL 字符作为分隔符，这在 Bash 4.4+ 中可用。

### 5.7 读取时显示进度

```bash
mapfile -t -C "echo '读到了第 $((MAPFILE_INDEX + 1)) 行'" -c 1000 bigfile < bigfile.txt
```

实际回调中可以使用传递的参数获取索引和行内容。

### 5.8 遍历数组

```bash
mapfile -t lines < file.txt
for line in "${lines[@]}"; do
    echo "$line"
done
```

或者通过下标遍历：

```bash
for i in "${!lines[@]}"; do
    printf "[%d] %s\n" "$i" "${lines[$i]}"
done
```

示例参考。

---

## 6. 返回值

`mapfile` 返回成功（0），除非出现以下情况之一：

- 使用了非法选项或选项参数无效；
- 目标变量为只读；
- 目标变量不是索引数组（例如是关联数组）；
- 无法为数组赋值。

返回值说明参考。

---

## 7. 与 while read 的对比

| 特性 | `mapfile` | `while read` 循环 |
| --- | --- | --- |
| 性能 | 高，内建块缓冲 I/O | 较低，逐行读取 |
| 子 shell 问题 | 使用进程替换可避免 | 管道会创建子 shell |
| 代码简洁度 | 一行完成 | 需要多行循环 |
| 灵活性 | 适合一次性读取全部行 | 适合逐行处理，可边读边处理 |
| 大文件内存 | 全部加载到内存 | 可流式处理，内存占用低 |
| Bash 版本要求 | 4.0+ | 所有版本 |

`mapfile` 在读取中等大小文件时性能优势明显。但对于非常大的文件（如数百 MB），将所有行加载到内存可能不合适，此时 `while read` 循环是更好的选择。

---

## 8. 版本兼容性

| Bash 版本 | 支持情况 |
| --- | --- |
| Bash 4.0+ | 引入 `mapfile` / `readarray`，但不支持 `-d` 选项 |
| Bash 4.4+ | 新增 `-d` 选项，支持自定义行分隔符和 NUL 分隔 |
| Bash 3.2 | 不支持 `mapfile`（macOS 默认 Bash 版本） |

macOS 系统自带的 `/bin/bash` 是 Bash 3.2，不包含 `mapfile`。如果需要使用，可以通过 Homebrew 安装新版 Bash，或使用兼容的 `while read` 循环替代。

---

## 9. 常见陷阱与注意事项

1. **数组名必须是最后一个参数**  
   ```bash
   mapfile -d $'\0' ARRAY < file   # 正确
   mapfile ARRAY -d $'\0' < file   # 错误
   ```
   参数顺序很重要，数组名必须放在所有选项之后。

2. **管道会导致子 shell 问题**  
   ```bash
   # 错误：数组在当前 shell 中不可见
   cat file.txt | mapfile -t arr

   # 正确：使用重定向或进程替换
   mapfile -t arr < file.txt
   mapfile -t arr < <(cat file.txt)
   ```
   管道中的 `mapfile` 在独立子 shell 进程中运行，数组赋值不会反映到调用 shell。

3. **`-O` 不会清空数组**  
   使用 `-O` 时，`mapfile` 不会清空目标数组，而是在指定下标处开始覆盖或追加。如果需要从特定下标开始但保留原有内容，这个行为符合预期；否则容易造成数据混淆。

4. **`-d ''` 需要 Bash 4.4+**  
   空字符串分隔符（NUL 分隔）是 Bash 4.4 引入的特性。在旧版本中可以使用 `-d $'\0'`，但行为可能不如空字符串可靠。

5. **大文件的内存问题**  
   `mapfile` 会将文件所有行一次性加载到内存。对于超大文件，应考虑使用 `while read` 流式处理。

6. **只读或非索引数组会失败**  
   如果目标变量是只读的，或者声明为关联数组（`declare -A`），`mapfile` 会失败并返回非零状态。

---

## 10. 总结

`mapfile` 是 Bash 4.0+ 提供的高效数组填充工具，适合将文件或命令输出的行快速读入索引数组。核心用法是 `mapfile -t array < file`。需要注意版本要求（`-d` 需要 4.4+）、参数顺序（数组名最后）、以及避免在管道中使用导致子 shell 问题。对于需要流式处理的大文件，`while read` 循环仍是更合适的选择。

---

参考：

- `help mapfile`（Bash 内建帮助）
- Bash 手册页（`man bash`）
- GNU Bash 文档