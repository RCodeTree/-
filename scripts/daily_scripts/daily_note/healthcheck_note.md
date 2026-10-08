这份针对你刚才复盘和实践过程中疑惑点的 Shell 脚本技术笔记已经整理完毕，直接复制保存为 `.md` 文件即可：

```markdown
# Linux & Shell 脚本高频实用技术复盘笔记

> 本笔记记录了在实践过程中遇到的后台服务启动、字符串处理、网络探活及进程管理的重点与易错点，方便后续查阅与复盘。

---

## 一、 后台静默启动 HTTP 服务

### 典型命令
```bash
nohup python3 -m http.server 8080 >/dev/null 2>&1 &

```

### 关键要素拆解

* **`nohup`**：忽略挂起信号（SIGHUP），防止关闭终端/连接时进程挂掉。
* **`python3 -m http.server 8080`**：启动 Python 内置 HTTP 服务，监听 8080 端口，根目录为当前工作目录。
* **`>/dev/null`**：标准输出（stdout）重定向到“黑洞”，丢弃正常日志。
* **`2>&1`**：标准错误（stderr）重定向到标准输出，同样丢弃，实现完全无提示输出。
* **`&`**：放到后台运行，释放当前终端控制权。

> **返回示例**：`[1] 1936` （`[1]` 表示任务 ID，`1936` 表示系统进程 PID）。

---

## 二、 Shell 原生字符串截取（参数扩展）

使用原生语法（Parameter Expansion）提取 `IP:PORT` 或 `HOST:PORT` 格式，性能远高于 `cut` / `awk`。

```bash
local host="${addr%%:*}"   # 截取冒号前的 HOST / IP
local port="${addr##*:}"   # 截取冒号后的 PORT

```

### 核心语法记忆口诀

* **`%`**：从**后往前**删（看作尾部/右侧）。
* **`#`**：从**往前删**（看作头部/左侧）。
* **单符号（`%` / `#`）**：**最短匹配**。
* **双符号（`%%` / `##`）**：**最长匹配**。

### 运行逻辑分析（以 `192.168.1.100:8080` 为例）

1. **`${addr%%:*}`**：从右往左寻找最长的 `:*`（即 `:8080`），将其删掉，只保留 `192.168.1.100`。
2. **`${addr##*:}`**：从左往右寻找最长的 `*:`（即 `192.168.1.100:`），将其删掉，只保留 `8080`。

---

## 三、 高效安全的“逐行读取”与“按空格拆分”

### 1. 标准逐行读取（防吃空格、防漏行）

```bash
while IFS= read -r line || [ -n "$line" ]; do
    ...
done < "config.txt"

```

* **`IFS=`**：清空内部字段分隔符，防止 `read` 吃掉行首和行尾的空格/Tab。
* **`-r`**：禁用反斜杠 `\` 的转义作用，保持原始文本。
* **`|| [ -n "$line" ]`**：防止文件的最后一行为非换行符结尾时被 `read` 漏掉。

### 2. 字段拆分（利用默认 IFS）

```bash
read -r type name addr <<< "$line"

```

* 不设置 `IFS=` 时，`read` 恢复**默认分隔符**（空格、Tab、换行）。
* **`<<< "$line"`**：Here-String 语法，将变量 `$line` 的内容当作输入喂给 `read`。
* 依次按空格将文本切割赋给 `type`、`name` 和 `addr` 变量。

---

## 四、 HTTP 与 TCP 服务探活实践

### 1. HTTP 状态码检测

```bash
check_http() {
    local url="$1" code
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time "$TIMEOUT" "$url" || true)
    [ "$code" = "200" ]
}

```

* **`-s`**：静音模式，不显示进度条。
* **`-o /dev/null`**：不保存网页正文内容。
* **`-w '%{http_code}'`**：仅输出 HTTP 返回码（如 `200`）。
* **`|| true`**：规避 `set -e` 脚本在 `curl` 超时报错时直接崩溃。
* **`[ "$code" = "200" ]`**：函数的最后一条命令，成立返回 `0`（True），不成立返回非 `0`（False）。

### 2. 原生 TCP 端口检测（免依赖）

```bash
check_tcp() {
    local addr="$1"
    local host="${addr%%:*}"
    local port="${addr##*:}"
    timeout "$TIMEOUT" bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null
}

```

* **`/dev/tcp/$host/$port`**：Bash 内置的虚拟网络重定向接口，无须安装 `nc` 或 `telnet` 即可通过握手检测 TCP 端口可用性。
* **`timeout "$TIMEOUT"`**：防止防火墙静默丢包时卡死脚本。
* **`bash -c "..."`**：确保始终运行在支持 `/dev/tcp` 的 Bash 解析器中。

---

## 五、 进程查找工具 pgrep 的精准匹配

`pgrep` 默认是**模糊匹配**（包含匹配），易造成误判或误杀。

```bash
pgrep -x "ssh"

```

* **`-x` (`--exact`)**：开启**精准匹配**，进程名必须完全与参数一致（如只匹配 `ssh`，忽略 `sshd` 或 `sshd-session`）。
* **常用组合**：
* **`pkill -x nginx`**：精准杀死目标进程，避免误杀 `nginx_exporter` 等衍生进程。
* **`pgrep -xf "python3 main.py"`**：结合 `-f` 参数精准匹配完整命令行参数。



```

```