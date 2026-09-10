# grep awk sed

## grep 详解

- 作用：文本搜索
- 基本用法
- 常用参数：-i -v -n -c -r -E -o -w
- 正则基础：^ $ . \* \[ ] 等

## sed 详解

- 作用：流编辑器，按行处理
- 基本用法：s/替换/ 等
- 常用操作：p d s a i c
- 地址定位

## awk 详解

- 作用：按列处理文本
- 基本用法：awk '{print $1}'
- 字段分隔符 -F
- 内置变量 NR NF $0 $1
- 条件过滤
- BEGIN END
- 简单计算

***

# 一、grep —— 文本搜索器

**作用**：从文件或输出流中，把"包含指定内容"的行**筛选**出来。

## 1. 基本语法

```bash
grep [选项] "要查找的内容" 文件名
```

## 2. 最常用的选项

| 选项   | 作用       | 示例                                    | <br />              |
| ---- | -------- | ------------------------------------- | :------------------ |
| `-i` | 忽略大小写    | `grep -i "error" samples.txt`         | <br />              |
| `-v` | 反向匹配（排除） | `grep -v "GET" access.txt`            | <br />              |
| `-n` | 显示行号     | `grep -n "Error" samples.txt`         | <br />              |
| `-c` | 只统计匹配行数  | `grep -c "GET" access.txt`            | <br />              |
| `-o` | 只输出匹配的部分 | `grep -o "https://[^ ]*" samples.txt` | <br />              |
| `-w` | 精确匹配整个单词 | `grep -w "GET" access.txt`            | <br />              |
| `-r` | 递归搜索目录   | `grep -r "error" /var/log/`           | <br />              |
| `-E` | 支持扩展正则   | \`grep -E "apple                      | banana" sales.txt\` |

## 3. 基础正则元字符（grep 的灵魂）

| 元字符  | 含义             | 示例                           |
| ---- | -------------- | ---------------------------- |
| `^`  | 行首             | `grep "^192.168" access.txt` |
| `$`  | 行尾             | `grep "200$" access.txt`     |
| `.`  | 任意单个字符         | `grep "1.2.168"`             |
| `*`  | 前一个字符重复 0 次或多次 | `grep "err*or"`              |
| `+`  | 前一个字符重复 1 次或多次 | `grep "err+" samples.txt`    |
| `[]` | 字符集合           | `grep "[0-9]" samples.txt`   |
| `\`  | 转义             | `grep "\.com" samples.txt`   |

***

# 二、sed —— 流编辑器

**作用**：**按行读取**、对文本做"查找**替换、删除、打印、插入**"等操作。它**默认不修改原文件**，只输出结果到屏幕（除非用 `-i`）。

## 1. 基本语法

```bash
sed [选项] '操作命令' 文件名
```

## 2. 最常用的操作

### ① 替换 `s/旧/新/`（最核心）

```bash
sed 's/apple/orange/' sales.txt
```

- `s` = substitute（替换）
- 默认**每行只替换第一个匹配**
- 加 `g` 表示替换一行中的所有匹配：

```bash
sed 's/apple/orange/g' sales.txt
```

### ② 删除 `d`

```bash
sed '1d' sales.txt          # 删除第1行
sed '2,4d' sales.txt        # 删除第2到4行
sed '/apple/d' sales.txt    # 删除包含 apple 的行
```

### ③ 打印 `p`

```bash
sed -n '1,3p' sales.txt     # 只打印第1到3行（-n 抑制默认输出）
sed -n '/Error/p' samples.txt
```

### ④ 在指定位置插入/追加

```bash
sed '1i 这是新加的第一行' samples.txt    # 在第1行前插入
sed '2a 这是追加的行' samples.txt        # 在第2行后追加
```

### ⑤ 真正修改原文件 `-i`

```bash
sed -i 's/apple/orange/g' sales.txt    # 危险，会直接改原文件
```

**风险提醒：`-i`** **会直接覆盖原文件。练习时建议先不加** **`-i`** **预览，确认无误后再加。**

### ⑥ 多命令操作组合：e

```bash
sed -e "s/apple/A/g" -e "s/dog/DOG/g"  samples.txt # 先替换 apple，再替换 dog
```

***

# 三、awk —— 列处理利器

**作用**：按\*\*"字段（列）"\*\*来处理结构化文本，是三者中功能最强的，本质是一门小型编程语言。

## 1. 核心概念：字段

awk 默认用\*\*空白（空格/Tab）\*\*作为分隔符，把每行切分成多个字段：

- `$0`：整行
- `$1`：第 1 列
- `$2`：第 2 列
- `$NF`：最后一列
- `NF`：这一行的字段总数
- `NR`：当前行号（从 1 开始）

## 2. 基本语法

```bash
awk '条件 {动作}' 文件名
```

## 3. 常用示例

### ① 打印指定列

```bash
awk '{print $1, $2}' access.txt        # 打印第1、2列
```

### ② 按条件过滤

```bash
awk '$NF == 200 {print $0}' access.txt   # 打印状态码为200的行
awk '$3 > 60000 {print $1, $3}' employees.txt -F:
```

### ③ 自定义分隔符 `-F`

```bash
awk -F: '{print $2}' employees.txt       # 以冒号分隔，打印姓名
awk -F, '{print $2}' sales.txt           # 以逗号分隔，打印产品名
```

### ④ 内置变量

```bash
awk '{print NR, $0}' access.txt          # 加行号
awk '{print NF}' samples.txt             # 每行有几个字段
```

### ⑤ 统计与计算

```bash
awk '{sum += $NF} END {print sum}' access.txt     # 累加最后一列
```

### ⑥ BEGIN / END 块

```bash
awk 'BEGIN {print "开始处理"} {print $1} END {print "处理结束"}' access.txt
```

- `BEGIN`：处理前执行一次（可用来打印表头）
- `END`：处理完后执行一次（可用来打印合计）

***

# 四、结合你的文件做练习

你的 `/practice` 目录下有这些文件，先记住它们的结构：

| 文件              | 结构               | 关键信息                  |
| --------------- | ---------------- | --------------------- |
| `access.txt`    | Nginx 访问日志（空格分隔） | IP、方法、路径、状态码、字节数      |
| `employees.txt` | 冒号分隔             | ID:姓名:部门:薪资:城市        |
| `sales.txt`     | 逗号分隔 CSV         | 日期,产品,数量,单价           |
| `samples.txt`   | 普通文本             | 含邮箱、URL、Error、重复行、Tab |

***

## 第一部分：grep 练习

### 练习 1-1（基础匹配）

从 `access.txt` 中找出所有 `GET` 请求。

### 练习 1-2（精确匹配）

用 `-w` 从 `access.txt` 中找出 `GET` 这个单词，和上面不加 `-w` 结果有什么不同？

### 练习 1-3（行号 + 统计）

1. 从 `samples.txt` 中找出包含 `Error` 的行，并显示行号。
2. 统计 `samples.txt` 中有多少行包含 `Error`。

### 练习 1-4（正则）

1. 从 `access.txt` 中找出所有以 `192.168` 开头的行。
2. 从 `samples.txt` 中提取出所有邮箱地址（提示：用 `-o` 和正则 `[a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]*`）。

### 练习 1-5（反向过滤）

从 `access.txt` 中排除所有状态码为 `200` 的行（提示：`-v`，并结合 `200$` 或直接 `grep -v " 200 "`）。

***

## 第二部分：sed 练习

### 练习 2-1（替换）

把 `sales.txt` 中的 `apple` 全部替换成 `pear`，但**先不要加** **`-i`**，只预览结果。

### 练习 2-2（删除行）

1. 删除 `sales.txt` 的表头行（第 1 行）。
2. 删除 `access.txt` 中包含 `POST` 的行。

### 练习 2-3（打印指定行）

只打印 `employees.txt` 的第 3 到第 5 行。

### 练习 2-4（多重替换）

在一条 sed 命令中，把 `samples.txt` 里的 `apple` 换成 `A`，同时把 `dog` 换成 `DOG`（提示：用 `-e` 或分号 `;` 连接多个操作）。

***

## 第三部分：awk 练习

### 练习 3-1（打印列）

1. 打印 `access.txt` 的第 1 列（IP 地址）。
2. 打印 `employees.txt` 的第 2 列和第 4 列（姓名和薪资），注意用 `-F:`。

### 练习 3-2（条件过滤）

1. 找出 `employees.txt` 中薪资超过 70000 的员工。
2. 找出 `access.txt` 中状态码为 `404` 的完整行。

### 练习 3-3（统计计算）

1. 统计 `sales.txt` 中所有商品的 `quantity` 总和（注意 CSV 表头，用 `NR>1` 跳过表头）。
2. 计算 `sales.txt` 中每种商品的总销售额（数量 × 单价）。

### 练习 3-4（分组统计，进阶）

用 awk 统计 `employees.txt` 中每个部门（第 3 列）的平均薪资。

***

## 第四部分：三剑客组合（SRE 实战）

### 练习 4-1

从 `access.txt` 中，统计每个 IP 地址访问了多少次（提示：awk 提取第 1 列，`sort` 排序，`uniq -c` 统计）。

### 练习 4-2

找出 `access.txt` 中响应字节数（最后一列）最大的那一条请求。

```bash
#!/bin/bash
awk \
'
BEGIN {
max = 0
}

$NF > max {
        max = $NF      
}

END {
        print max      
}
' access.txt
```

`1. 如果脚本较长，使用多行时确保每个 { 和 } 正确闭合，并且 BEGIN、END 等关键字与后面的 { 之间不要换行（除非你明确知道 awk 支持）。更推荐使用单引号包裹的多行字符串，保持清晰的缩进。`
`2. 避免将 { 单独放一行，防止某些 awk 版本解析出错。`

### 练习 4-3

把 `employees.txt` 中所有 `New York` 替换成 `NYC`，并且只显示 `Engineering` 部门的员工。
``` bash
#!/bin/bash
sed -i 's/New York/NYC/' employees.txt
awk -F: '$3 == "Engineering" && $NF == "NYC" {print $2} ' employees.txt 
```

### 练习 4-4（日志排障实战）

假设线上报错，请用一条命令找出 `access.txt` 中所有状态码为 `500` 或 `403` 的请求，并显示它们的 IP 和请求路径。
``` bash
awk '$(NF - 1) == 500 || $(NF - 1) == 403  {print $6, $7, $8, $(NF - 1)}' access.txt
```

***

# 五、给你的验收小测验

先别急着全做，先回答下面几道**理解题**，我帮你确认掌握程度：

1. `grep "GET"` 和 `grep -w "GET"` 有什么区别？
2. `sed 's/apple/orange/'` 和 `sed 's/apple/orange/g'` 有什么区别？
3. awk 中 `$0`、`$1`、`$NF`、`NR` 分别代表什么？
4. `awk -F:` 中的 `-F` 是做什么用的？
5. 说出 `grep -v` 的作用，并给一个实际场景。
---

**1. `grep "GET"` 和 `grep -w "GET"` 有什么区别？**  
- `grep "GET"`：匹配**任何包含**子串 `"GET"` 的行，例如 `"GETTING"`、`"FORGET"` 都会被匹配。  
- `grep -w "GET"`：匹配**整个单词** `"GET"`，即只有被非单词字符（如空格、标点、行首行尾）包围的 `"GET"` 才会匹配，`"GETTING"` 或 `"FORGET"` 不会匹配。`-w` 相当于用正则 `\bGET\b` 做边界限定。

---

**2. `sed 's/apple/orange/'` 和 `sed 's/apple/orange/g'` 有什么区别？**  
- `s/apple/orange/`（无 `g`）：只替换**每行第一次**出现的 `apple` 为 `orange`。  
- `s/apple/orange/g`（有 `g`，global）：替换**每行所有**出现的 `apple` 为 `orange`（全局替换）。

---

**3. `awk` 中 `$0`、`$1`、`$NF`、`NR` 分别代表什么？**  
- `$0`：当前**整行**记录（全部字段）。  
- `$1`：当前行的**第一个字段**（默认以空白分隔）。  
- `$NF`：当前行的**最后一个字段**（`NF` 是字段总数，`$NF` 就是最后一个字段的值）。  
- `NR`：当前已读取的**行号**（从 1 开始），即记录序号。

---

**4. `awk -F:` 中的 `-F` 是做什么用的？**  
- `-F` 用于指定**输入字段分隔符**。`awk -F:` 表示以冒号 `:` 作为分隔符来拆分每行记录（常见于处理 `/etc/passwd` 等文件），等价于在 awk 内部设置 `FS=":"`。

---

**5. 说出 `grep -v` 的作用，并给一个实际场景。**  
- `grep -v` 的作用是**反向匹配**（invert match），即输出**不包含**指定模式的行。  
- **实际场景**：查看系统日志时，想过滤掉所有包含 `"DEBUG"` 的调试信息，只关注错误或警告，可以使用：  
  ```bash
  grep -v "DEBUG" /var/log/app.log
  ```  
  或者查看进程列表时排除 `grep` 自身：  
  ```bash
  ps aux | grep python | grep -v grep
  ```

---
