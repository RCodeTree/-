# 每日 Shell 运维实战练习 · 2026-09-22

## 题目：服务健康巡检脚本（healthcheck.sh）

### 题目背景

至此你已经打通了"备份 → 恢复"的闭环（`backup.sh` + `restore.sh`）。但在真实生产里，SRE 每天最常干的事不是备份，而是**巡检**：定时确认关键服务（Web、数据库、SSH）是否还活着，一旦掉线立刻告警。

今天写 `healthcheck.sh`：读一份**巡检清单**，对里面的每类目标做探测——HTTP 探活、TCP 端口探活、进程探活，失败时**重试 N 次**才判定 DOWN，最后输出汇总，并用**退出码**驱动监控告警（全 UP 返回 0，有 DOWN 返回 1）。

这道题会把你前面学的东西**综合起来**：选项解析 + 函数 + 循环 + 重定向 + 退出码，并引入两个新技能：**读配置文件**和**带重试的探测逻辑**。

---

## 脚本编写要求

编写 `healthcheck.sh`，实现：

1. **命令行**：`./healthcheck.sh -c <配置文件> [-r <重试次数>] [-t <超时秒>] [-h]`
   - `-c`：巡检清单文件路径（**必填**）
   - `-r`：每个目标失败后的重试次数，默认 `3`
   - `-t`：单次探测超时秒数，默认 `3`
   - 用 `getopts` 解析（注意 `c`/`r`/`t` 都**要带参数值**，后面加 `:`）
2. **读取清单**：清单每行格式 `<类型> <名称> <目标>`，用 `while IFS= read -r line ... done < 配置文件` 逐行读；
   - 跳过**空行**和以 `#` 开头的**注释行**
   - 字段缺失（类型或名称为空）则 `log_warn` 跳过该行，不中断整体巡检
3. **三种探测类型**（成功返回 0，失败返回非 0）：
   - `http`：用 `curl -s -o /dev/null -w '%{http_code}' --max-time "$TIMEOUT" <url>`，期望返回 `200`
   - `tcp`：目标形如 `host:port`，用 bash 的 `/dev/tcp` + `timeout` 探测端口是否可连
   - `proc`：用 `pgrep -x <进程名>` 判断进程是否存在（目标列即进程名，可留空）
4. **带重试的探测**：单个目标失败后，间隔 2 秒重试，最多 `-r` 次；**重试全部失败才判 DOWN**
5. **输出与汇总**：每个目标打印 `[UP]`/`[DOWN]`，最后打印 `共 N 项，UP=x，DOWN=y`
6. **退出码**：全部 UP → `exit 0`；只要有 DOWN → `exit 1`（这样 cron/monitoring 能直接据此告警）
7. **用法/配置错误** → `exit 2`

---

## 配置清单示例（/tmp/healthcheck.conf）

```bash
# 健康巡检清单：<类型> <名称> <目标>

http web   http://127.0.0.1:8080/health
tcp  ssh   127.0.0.1:22
tcp  mysql 127.0.0.1:3306
proc sshd
```

---

## 测试步骤

```bash
# 1. 准备一个本地 HTTP 探测目标（仅作为测试夹具，起一个静态服务）
mkdir -p /tmp/webroot && echo ok > /tmp/webroot/health
(cd /tmp/webroot && nohup python3 -m http.server 8080 >/dev/null 2>&1 &)

# 2. 写巡检清单
cat > /tmp/healthcheck.conf <<'EOF'
# 健康巡检清单
http web   http://127.0.0.1:8080/health
tcp  ssh   127.0.0.1:22
tcp  mysql 127.0.0.1:3306
proc sshd
EOF

# 3. 跑巡检
./healthcheck.sh -c /tmp/healthcheck.conf
echo "退出码: $?"

# 4. 故意加一个探测不到的目标（观察重试后判 DOWN、退出码变 1）
echo "tcp dead 127.0.0.1:9999" >> /tmp/healthcheck.conf
./healthcheck.sh -r 3 -t 1 -c /tmp/healthcheck.conf
echo "退出码: $?"

# 5. 参数错误（缺 -c）应打印用法并 exit 2
./healthcheck.sh
echo "退出码: $?"
```

---

## 输出示例

```bash
$ ./healthcheck.sh -c /tmp/healthcheck.conf
[INFO]  2026-09-22 08:30:00 开始健康巡检，配置文件: /tmp/healthcheck.conf
[INFO]  2026-09-22 08:30:00 [UP]   web (http) -> http://127.0.0.1:8080/health
[INFO]  2026-09-22 08:30:00 [UP]   ssh (tcp) -> 127.0.0.1:22
[WARN]  2026-09-22 08:30:02 [DOWN] mysql (tcp) -> 127.0.0.1:3306
[INFO]  2026-09-22 08:30:02 [UP]   sshd (proc) -> sshd
[INFO]  2026-09-22 08:30:02 巡检结束: 共 4 项，UP=3，DOWN=1
$ echo $?
1
```

---

## 考察知识点

- **读配置文件**：`while IFS= read -r line ... done < file`、`read -r a b c <<< "$line"` 字段拆分
- 跳过空行/注释行：`[ -z "$line" ] && continue`、`case "$line" in \#*) continue ;; esac`
- `curl -w '%{http_code}'` 只取 HTTP 状态码、`--max-time` 超时
- bash 内建 `/dev/tcp/<host>/<port>`（**不需要装 netcat**）+ `timeout`
- `pgrep -x` 精确匹配进程名
- **带重试的探测循环**：`for (( i=1; i<=RETRIES; i++ ))`、`sleep`
- **`set -e` 与失败命令的配合**：`$(curl ... || true)` 防止 curl 失败直接杀掉脚本
- **退出码驱动监控**（0=健康 / 1=异常 / 2=用法错误）

---

## 验收标准

1. 不传 `-c` 或配置文件不可读时，打印用法，退出码 `2`。
2. 全部目标 UP 时，退出码 `0`。
3. 存在 DOWN 目标时，退出码 `1`。
4. 失败目标要**重试 `-r` 次**后才判 DOWN（能看到间隔、耗时随重试增加）。
5. `http` / `tcp` / `proc` 三种类型都能正确判定。
6. 清单里的空行和 `#` 注释行被正确跳过，不影响统计。
7. 汇总行的 `UP`/`DOWN`/总数与实际一致。

---

## 参考答案（写完后对照）

```bash
#!/bin/bash
set -euo pipefail

# ==================== 默认参数 ====================
CONFIG=""
RETRIES=3       # 每个目标失败后的重试次数
INTERVAL=2      # 重试间隔（秒）
TIMEOUT=3       # 单次探测超时（秒）

# ==================== 日志函数 ====================
log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m" >&2; }
log_info()  { echo -e "\033[32m[INFO]  $(date '+%F %T') $*\033[0m"; }
log_warn()  { echo -e "\033[33m[WARN]  $(date '+%F %T') $*\033[0m"; }

usage() {
    log_error "用法: $0 -c <配置文件> [-r <重试次数>] [-t <超时秒>]"
    log_error "配置文件每行格式: <类型> <名称> <目标>，类型: http | tcp | proc"
    log_error "示例: $0 -c /tmp/healthcheck.conf -r 3 -t 3"
}

# ==================== 解析选项 ====================
while getopts ":c:r:t:h" opt; do
    case "$opt" in
        c) CONFIG="$OPTARG" ;;
        r) RETRIES="$OPTARG" ;;
        t) TIMEOUT="$OPTARG" ;;
        h) usage; exit 0 ;;
        \?) usage; exit 2 ;;
    esac
done
shift $((OPTIND - 1))

# ==================== 参数校验 ====================
if [ -z "$CONFIG" ]; then
    usage
    exit 2
fi
if [ ! -r "$CONFIG" ]; then
    log_error "配置文件不存在或不可读: $CONFIG"
    exit 2
fi

# ==================== 探测函数（成功 0，失败非 0） ====================
check_http() {
    local url="$1" code
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time "$TIMEOUT" "$url" || true)
    [ "$code" = "200" ]
}

check_tcp() {
    local addr="$1"
    local host="${addr%%:*}"   # 取冒号前
    local port="${addr##*:}"   # 取冒号后
    timeout "$TIMEOUT" bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null
}

check_proc() {
    local name="$1"
    pgrep -x "$name" >/dev/null 2>&1
}

# ==================== 带重试的探测 ====================
check_with_retry() {
    local type="$1" name="$2" addr="$3" i
    for (( i = 1; i <= RETRIES; i++ )); do
        case "$type" in
            http) check_http "$addr" && return 0 ;;
            tcp)  check_tcp  "$addr" && return 0 ;;
            proc) check_proc "$name" && return 0 ;;
            *)    log_warn "未知类型: $type（跳过 $name）"; return 2 ;;
        esac
        if [ "$i" -lt "$RETRIES" ]; then
            sleep "$INTERVAL"
        fi
    done
    return 1
}

# ==================== 主流程 ====================
up=0; down=0; total=0
log_info "开始健康巡检，配置文件: $CONFIG"

while IFS= read -r line || [ -n "$line" ]; do
    # 跳过空行与注释行
    [ -z "$line" ] && continue
    case "$line" in \#*) continue ;; esac

    # 拆字段：类型 名称 目标
    read -r type name addr <<< "$line"

    if [ -z "$type" ] || [ -z "$name" ]; then
        log_warn "配置行格式错误，已跳过: $line"
        continue
    fi

    total=$((total + 1))
    if check_with_retry "$type" "$name" "$addr"; then
        log_info "[UP]   $name ($type) -> $addr"
        up=$((up + 1))
    else
        log_error "[DOWN] $name ($type) -> $addr"
        down=$((down + 1))
    fi
done < "$CONFIG"

log_info "巡检结束: 共 $total 项，UP=$up，DOWN=$down"

# 用退出码表达健康状态，供监控/告警使用
if [ "$down" -gt 0 ]; then
    exit 1
fi
exit 0
```

---

## 关键点讲解与运维最佳实践

1. **配置与代码分离，是运维脚本的第一原则。**
   把"要巡检什么"写进配置文件（清单），脚本本体只负责"怎么巡检"。以后要加减监控项，改清单即可，不用动代码——这也是 Ansible/Nagios/Prometheus 的设计哲学。硬编码目标列表的脚本，最终都会变成没人敢改的"屎山"。

2. **`/dev/tcp` 是 bash 的隐藏武器。**
   `echo > /dev/tcp/127.0.0.1/22` 会尝试建立 TCP 连接，成功即返回 0。**不用装 `netcat`/`telnet` 就能做端口探活**。配合 `timeout` 防止目标端口挂起时脚本卡死。注意它只在 **bash** 下有效（`sh` 不行）。

3. **重试（retry）是"降噪"的第一道防线。**
   网络抖动、瞬时 GC、后端短暂不可用都可能造成"假 DOWN"。一次探测就告警，会制造大量误报（告警疲劳）。**失败后间隔重试、多次都失败才判 DOWN**，是 SRE 告警系统的基本素养。

4. **`$(curl ... || true)` 里的 `|| true` 不是废话。**
   在 `set -e` 下，`code=$(curl ...)` 里 curl 若连不上会返回非 0，赋值语句就失败了，`set -e` 会**当场杀掉整个脚本**。加 `|| true` 让"探测失败"变成一个正常可处理的结果，而不是致命错误。这是"严谨配置 + 网络探测"的经典配合陷阱。

5. **退出码就是给机器的接口。**
   脚本对人类来说靠 `[UP]/[DOWN]` 日志，对机器（cron、Zabbix、Prometheus textfile collector）来说靠**退出码**：0 正常、非 0 异常。所以你最后一定要用 `exit 0/1` 明确表达结果，而不是默认退出。

### 进阶提示（下一阶段再扩展）

- 加 `-w`（watch）模式：`while true; do 巡检; sleep 60; done`，做成常驻探针。
- 失败时发**通知**：webhook（钉钉/企微）或 `mail`，把 DOWN 的目标推给人。
- 把每次巡检结果追加到 CSV（`日期,目标,状态`），日后用你第三题的 `log_analyzer.sh` 思路统计**可用率 / 抖动次数**（SLA 报表的基础）。
- **并发探测**：目标多时串行太慢，用后台任务 `check &` + `wait` 并行，注意汇总计数要用临时文件或 `wait -n` 收集结果。
- 接入真实监控：把结果写成 Prometheus `textfile` 格式（`healthcheck_up{target="web"} 1`），让 Prometheus 采集。
