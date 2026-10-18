# read

`read` 是 Bash 的**内建命令**（不是外部二进制），作用是**从标准输入（键盘、管道、文件、命令输出）读取一行/一段内容，并赋给变量**。

在运维脚本里，它几乎出现在每一个需要**交互确认、逐行处理文件、读取配置**的场景中。尤其是 `while read` 循环，是处理日志和列表文件的“标准姿势”。

> 注意：`read` 是 shell 内建命令，用 `type read` 可以确认，而 `man read` 通常查不到（要用 `help read`）。

***

### **1. 基本语法**

```bash
read [选项] 变量1 变量2 变量3 ...
```

- 从标准输入读取一行，按 **IFS**（默认是空格/Tab/换行）切分成多个“词”。
- 依次赋给后面的变量。

```bash
read name
# 输入：tom
echo "$name"      # tom
```

***

### **2. 核心选项详解**

| 选项 | 作用 | 说明 |
| :--- | :--- | :--- |
| **`-p "提示语"`** | 显示提示符 | 交互式输入必备，等价于先 `echo -n` 再 `read` |
| **`-s`** | 静默模式（不回显） | 输入密码用，屏幕不显示输入内容 |
| **`-r`** | 不把 `\` 当转义符 | **几乎必加**，防止反斜杠被吞掉（见坑点） |
| **`-t 秒数`** | 超时 | 超时后 `read` 返回非 0，常用于给默认值或防止卡死 |
| **`-n 字符数`** | 读够 N 个字符立即返回 | 无需按回车，用于“按任意键继续” |
| **`-N 字符数`** | 读满 N 个字符才返回 | 比 `-n` 严格，会等满 N 个字符（含换行） |
| **`-d 分隔符`** | 自定义结束符 | 默认遇到换行结束，可改成别的（如 `-d ''` 读整个文件） |
| **`-a 数组名`** | 按词存入数组 | 每个词是数组一个元素 |
| **`-u 文件描述符`** | 从指定 fd 读取 | 用于从 `3<` 等重定向的额外文件描述符读 |
| **`-e`** | 启用 readline | 支持方向键、退格、行编辑、历史 |
| **`-i 文本`** | 预填默认值 | 必须配合 `-e`，用户可直接回车采用默认值 |

#### 交互输入示例

```bash
# 提示 + 读取
read -p "请输入主机名: " host
echo "主机名是 $host"

# 密码静默输入
read -s -p "请输入密码: " passwd
echo        # 补一个换行
echo "密码已读取（不显示）"

# 带默认值
read -e -i "/usr/local" -p "安装路径 [回车用默认]: " dir
echo "路径: $dir"
```

#### 超时与“按任意键”

```bash
# 5 秒超时，未输入则用默认值
if read -t 5 -p "是否继续？(y/N) " ans; then
    echo "你输入了: $ans"
else
    echo "超时，采用默认值 N"
fi

# 按任意键继续
read -n 1 -s -p "按任意键继续..."
echo
```

#### 数组读取

```bash
read -a arr <<< "nginx mysql redis"
echo "${arr[0]}"    # nginx
echo "${#arr[@]}"   # 3（元素个数）
```

***

### **3. 变量赋值规则（重点）**

`read a b c` 读入一行后，赋值遵循两条规则：

1. **词比变量多** → 最后一个变量“吃掉”剩余所有内容。
2. **词比变量少** → 多余的变量被赋值为空。

```bash
read a b c
# 输入：one two three four five
echo "$a"   # one
echo "$b"   # two
echo "$c"   # three four five   ← 剩余全部塞进最后一个变量

read x y
# 输入：hello
echo "$x"   # hello
echo "$y"   # (空)
```

**IFS 的影响**：`read` 靠 `IFS` 来切分，默认 IFS 是空格、Tab、换行。连续多个空白会被合并，行首尾空白会被剥离。

```bash
read a b <<< "  hello    world  "
echo "$a"   # hello
echo "$b"   # world
```

***

### **4. 与 while 循环配合（SRE 核心技能）**

`while read` 是逐行处理文本/日志/列表的**标准写法**，注意 `-r` 几乎必加。

```bash
while IFS= read -r line; do
    echo "处理行: $line"
done < /etc/hosts
```

三个细节拆解：

- **`IFS=`**：临时清空 IFS，防止每行的前导/尾随空格被剥掉（读配置文件或路径时很重要）。
- **`-r`**：防止行内的反斜杠被当成转义符吃掉。
- **`< file`**：重定向，让 `read` 从文件逐行读，而不是键盘。

#### 结合管道处理命令输出

```bash
df -h | awk 'NR>1 && +$5 > 80 {print $1, $5}' | while read -r fs usage; do
    echo "告警：分区 $fs 使用率 $usage"
done
```

> 这正是 [system_check.sh](file:///c:/Users/rong/Desktop/云计算运维/scripts/system_check.sh#L41-L43) 里 `check_disk` 用到的模式。

***

### **5. SRE 实战场景**

#### 场景一：破坏性操作前的二次确认（Human-in-the-loop）

```bash
read -p "⚠️ 确认删除命名空间 ${ns} ？输入 YES 才执行: " confirm
if [[ "$confirm" == "YES" ]]; then
    kubectl delete ns "$ns"
else
    echo "已取消"
fi
```

> 生产环境凡是 `rm`、`kubectl delete`、`DROP TABLE` 等**破坏性/修改性**操作，都应该用 `read` 做人工终审闸门。

#### 场景二：逐行读取配置文件（key=value）

```bash
while IFS='=' read -r key value; do
    # 跳过空行和注释行
    [[ -z "$key" || "$key" == \#* ]] && continue
    echo "配置项: $key = $value"
done < /etc/myapp.conf
```

#### 场景三：读取用户/密码用于自动登录（只读示例）

```bash
read -p "数据库用户: " db_user
read -s -p "数据库密码: " db_pass
echo
mysql -u"$db_user" -p"$db_pass" -e "SHOW DATABASES;"
```

> 红线提醒：脚本里**禁止硬编码生产凭证**，密码通过 `read -s` 交互输入或从密钥管理（Vault/KMS）获取，绝不明文写进脚本或日志。

#### 场景四：菜单选择

```bash
echo "1) 查看负载  2) 查看磁盘  3) 退出"
read -p "请选择: " opt
case "$opt" in
    1) uptime ;;
    2) df -h ;;
    3) exit 0 ;;
    *) echo "无效选项" ;;
esac
```

***

### **6. 常见坑点（SRE 避坑）**

1. **管道会让变量在子 shell 中丢失**（最经典、最隐蔽）：

   ```bash
   # ❌ 错误：循环结束后 sum 为空
   echo -e "1\n2\n3" | while read n; do
       sum=$((sum + n))
   done
   echo "$sum"   # 空！因为管道右边跑在子 shell，变量带不出来
   ```

   **解决**：改用进程替换或 here-string：

   ```bash
   # ✅ 方法一：进程替换
   while read n; do sum=$((sum + n)); done < <(echo -e "1\n2\n3")
   echo "$sum"   # 6

   # ✅ 方法二：here-string
   while read n; do sum=$((sum + n)); done <<< $'1\n2\n3'
   ```

2. **不加 `-r` 反斜杠被吞**：文件里路径 `C:\temp\new` 会被 `read` 当转义处理，`\t`、`\n` 变成制表符/换行。**读路径、日志、Windows 路径必须加 `-r`**。

3. **文件最后一行没有换行符会丢**：`while read` 遇到文件末尾没有 `\n` 的最后一行，`read` 会返回非 0，导致该行没被处理。可用：

   ```bash
   while read -r line || [[ -n "$line" ]]; do
       echo "$line"
   done < file
   ```

4. **超时后变量保留旧值**：`read -t` 超时未输入时，变量**不会**被自动清空，可能残留上次的值。超时场景务必先手动清空或走 `else` 分支。

5. **`read` 默认吃行尾空白和反斜杠**：读配置值时，务必 `IFS= read -r`，否则 `VALUE="abc "` 末尾空格会丢。

6. **`-p` 和 `-s` 一起用时提示语不回显**：密码场景正常，但记得后面手动 `echo` 换行，否则下一条输出会粘在提示语后面。

***

### **7. 巩固练习**

1. **基础题**：写一个脚本，用 `read -p` 读入姓名和年龄两个变量，然后 `echo` 打印出来。
2. **交互题**：用 `read -s` 实现一个“输入密码不回显”的小脚本，并打印密码长度（不打印密码本身）。
3. **实战题**：用 `while IFS= read -r line` 逐行读取 `/etc/passwd`，只打印 UID 大于 1000 的普通用户（提示：用 `cut` 或 `awk` 提取第 3 列）。
4. **思考题**：写一段代码验证“管道后 `while read` 变量丢失”的问题，再用进程替换 `< <(...)` 修复它，观察两者 `echo` 输出的差异。

完成后把命令和输出发给我，或把报错贴出来，我帮你分析。
