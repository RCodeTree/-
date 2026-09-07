# Linux uniq 命令详解

`uniq`：**去除文本中连续重复行**，注意：只对**相邻重复行**生效，非相邻重复不会自动去重，所以通常配合 `sort` 使用。

> 
> 核心特性：uniq 不会扫描全文找重复，只对比**上下相邻行**。

## 语法

```
uniq [选项] [输入文件] [输出文件]
```

- 如果不指定文件，读取标准输入（管道 `|`）
- 不指定输出文件，打印到屏幕

## 常用选项汇总

| 参数 | 作用 |
| --- | --- |
| `-c` | 在每行开头，统计该行重复出现次数 |
| `-d` | 只显示**有重复**的行（只输出重复行，不输出唯一行） |
| `-D` | 显示所有重复的行，重复多少次输出多少次 |
| `-u` | 只显示**唯一行**，完全没有重复的行 |
| `-i` | 忽略大小写比较 |
| `-f N` | 跳过前 N 个字段，再比较重复 |
| `-s N` | 跳过前 N 个字符，再比较重复 |
| `-w N` | 只比较每行的前 N 个字符 |

> 
> ⚠️重要坑：**uniq 只消除连续重复**
> 示例文件 test.txt

```
apple
apple
banana
apple
```

直接 `uniq test.txt`

```
apple
banana
apple
```

第三个 apple 和上面不相邻，不会被删掉。
👉想要全局去重：**先排序 sort，再 uniq**

```
sort test.txt | uniq
```

## 实操示例

### 准备测试文本 demo.txt

```
cat > demo.txt <<EOF
aa
aa
bb
cc
bb
CC
dd
dd
dd
EOF
```

### 1. 基础去重（仅连续）

```
uniq demo.txt
```

输出：

```
aa
bb
cc
bb
CC
dd
```

> 
> bb 出现两次但是不相邻，保留。

### 2. 全局去重（sort + uniq，最常用）

sort 先把相同行放到相邻，再 uniq

```
sort demo.txt | uniq
```

输出：

```
aa
bb
CC
cc
dd
```

### 3. `-c` 统计重复次数

```
sort demo.txt | uniq -c
```

输出，左边数字=出现次数

```
      2 aa
      2 bb
      1 CC
      1 cc
      3 dd
```

配合 sort -nr 按次数倒序排序（统计Top）

```
sort demo.txt | uniq -c | sort -nr
```

### 4. `-d` 只输出有重复的行

只显示至少出现2次的行

```
sort demo.txt | uniq -d
```

输出

```
aa
bb
dd
```

### 5. `-D` 输出全部重复行，保留全部副本

```
sort demo.txt | uniq -D
```

```
aa
aa
bb
bb
dd
dd
dd
```

### 6. `-u` 只输出没有重复的行（唯一行）

```
sort demo.txt | uniq -u
```

```
CC
cc
```

### 7. `-i` 忽略大小写

```
sort demo.txt | uniq -i
```

`cc` 和 `CC` 视为相同。

### 8. `-f N` 跳过N列比较

`-f 1`：跳过第1个字段，从第2列开始判断重复

```
100 hello
200 hello
300 world
```

```
uniq -f 1 file
```

> 
> 忽略第一列数字，只对比后面内容，两行 hello 判定为重复。

### 9. `-s N` 跳过N个字符

跳过每行开头N个字符之后再比较。

### 10. `-w N` 只比较前N个字符

只拿每行前4个字符做重复判断。

```
uniq -w 4 file
```

## 高频工作场景

1. **日志统计某个字段出现次数**

```
# 提取第5列，排序统计频次
cat app.log | awk '{print $5}' | sort | uniq -c | sort -nr
```

2. **找出日志中重复的IP**

```
awk '{print $1}' access.log | sort | uniq -d
```

3. **找出只出现一次的IP**

```
awk '{print $1}' access.log | sort | uniq -u
```

## uniq vs sort -u

- `sort -u`：排序并且**全局直接去重**，不需要管道 uniq

```
sort -u demo.txt
```

区别：

1. `sort -u`：直接排序+去重，无法统计次数 `-c`，无法只看重复行 `-d`
2. `sort | uniq`：可以用 `-c/-d/-D/-u` 丰富参数，做统计分析，生产日志分析多用这个组合。
