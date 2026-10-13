# 每日 Shell 运维实战练习 · 2026-09-25

## 题目：系统资源巡检报告（sysreport.sh）

### 题目背景
前几题你已经把「巡检 → 告警」的链路走通（`healthcheck.sh` + `watchdog.sh`），也做过日志治理（`log_clean.sh`）。今天换一个视角：**不做"修复"，只做"体检报告"**。

生产上，一台服务器"快不行了"，往往不是突然挂掉，而是**内存吃紧、磁盘涨满、负载飙升**这些指标先露出苗头。SRE 要做的第一件事，是**定期生成一份可读、可落盘、可给机器判断的系统资源快照**，而不是等人喊"服务器卡了"才去查。

> 本题危险等级 ★（只读采集，不修改系统），但仍遵循一条铁律：**采集到的阈值、路径、输出都走参数或配置，不硬编码**。

---

## 脚本编写要求

编写 `sysreport.sh`，实现：

1. **命令行**：`./sysreport.sh [-o <报告文件>] [-t <阈值配置>] [-h]`
   - `-o`：报告输出文件（默认 `/tmp/sysreport.txt`）
   - `-t`：阈值配置文件（可选；不传则用内置默认值）
   - `-h`：打印用法

2. **采集四项指标**：
   - **运行时长**：主机名 + `uptime` 运行时长
   - **负载**：`/proc/loadavg` 的 1 分钟负载 + CPU 核数（`nproc`），对比「负载阈值」
   - **内存**：`free -m` 的 总量 / 已用 / 可用 / 使用率，对比「内存阈值」
   - **磁盘**：`df` 遍历各挂载点使用率，对比「磁盘阈值」

3. **阈值判断**：
   - 内置默认：内存 `80`(%)、磁盘 `85`(%)、负载 `4.0`
   - `-t` 传入配置文件可覆盖，格式为每行 `键=值`：
     ```
     MEM_THRESHOLD=80
     DISK_THRESHOLD=85
     LOAD_THRESHOLD=4.0
     ```
   - 超阈值 → 对应行标 `[WARN]`；未超 → 标 `[OK]`；报告末尾给出「结论：N 项告警」

4. **报告落盘 + 屏幕**：报告**同时**打印到屏幕**和**写入 `-o` 指定的文件（提示用 `tee` 或先拼字符串再两处输出）

5. **退出码**：`0` 报告生成成功；`1` 运行错误（如 `-t` 文件不存在/格式错误）；`2` 用法错误

---

## 测试步骤

```bash
# 1. 基本运行（不传任何参数）
./sysreport.sh
echo $?                  # 期望 0
cat /tmp/sysreport.txt   # 能看到完整报告

# 2. 指定输出文件
./sysreport.sh -o /tmp/my_report.txt
cat /tmp/my_report.txt

# 3. 阈值文件不存在 → 运行错误
./sysreport.sh -t /tmp/nonexist.conf
echo $?                  # 期望 1

# 4. 触发内存/负载告警（阈值压到极低，必然超）
cat > /tmp/thresh.conf <<'EOF'
MEM_THRESHOLD=1
DISK_THRESHOLD=85
LOAD_THRESHOLD=0.01
EOF
./sysreport.sh -t /tmp/thresh.conf   # 内存、负载应标 [WARN]

# 5. 触发磁盘告警（磁盘阈值压到 1%）
cat > /tmp/thresh2.conf <<'EOF'
DISK_THRESHOLD=1
MEM_THRESHOLD=99
LOAD_THRESHOLD=100
EOF
./sysreport.sh -t /tmp/thresh2.conf  # 磁盘应标 [WARN]

# 6. 用法错误
./sysreport.sh -x ; echo $?          # 期望 2（非法参数）
./sysreport.sh -o ; echo $?          # 期望 2（缺参数值）
```

---

## 输出示例

```
==================== 系统资源巡检报告 ====================
生成时间: 2026-09-25 08:00:00
主机: web-01
运行时长: up 3 days, 2 hours, 15 minutes

[负载] 1min=0.52 (核数=4)                            [OK]
[内存] 总量=7983MB 已用=3210MB 可用=4773MB 使用率=40.2%  [OK]
[磁盘] /dev/sda1 /        使用率=62%                 [OK]
[磁盘] /dev/sdb1 /data    使用率=91%                 [WARN]

结论: 1 项告警
=========================================================
```

---

## 考察知识点

- `free -m` 与 `df -hP` 的**字段解析**（`awk` 取列）
- `/proc/loadavg`、`nproc`、`uptime -p` 的采集方式
- **bash 浮点运算的坑**（`(( ))` 只能整数 → 百分比/负载比较用 `awk` 或 `bc`）
- `df` 长设备名换行 → `-P` 保证一行一条记录；过滤 `tmpfs` 等伪文件系统
- **阈值配置分离**（不硬编码，`-t` 覆盖）+ 安全解析（不直接 `source` 陌生配置）
- `tee` 实现"屏幕 + 文件"双输出
- 报告结构化落盘 + 退出码语义

---

## 验收标准

1. 不传任何参数时，生成默认报告到 `/tmp/sysreport.txt` 并打印到屏幕，`exit 0`。
2. `-o` 指定文件时，报告写入该文件。
3. `-t` 文件不存在时，报错并 `exit 1`。
4. 超阈值的指标行标 `[WARN]`，未超的标 `[OK]`，报告末尾有「结论：N 项告警」。
5. 阈值配置里出现未知键（如 `FOO=1`）时，报错并 `exit 1`。
6. 非法参数 / 缺参数值 → 打印用法并 `exit 2`。
7. 报告包含：时间戳、主机名、运行时长、负载、内存、磁盘、结论。

---

## 参考答案（写完后对照）

```bash
#!/bin/bash
set -euo pipefail

# ---- 默认值（可被 -t 覆盖）----
MEM_THRESHOLD=80
DISK_THRESHOLD=85
LOAD_THRESHOLD=4.0
REPORT_FILE="/tmp/sysreport.txt"
THRESHOLD_FILE=""

log_error() { echo -e "\033[31m[ERROR] $(date '+%F %T') $*\033[0m" >&2; }

usage() {
    log_error "用法: $0 [-o <报告文件>] [-t <阈值配置>] [-h]"
    log_error "  -o 报告输出文件(默认 /tmp/sysreport.txt)"
    log_error "  -t 阈值配置文件(格式: MEM_THRESHOLD=80 等)"
    exit 2
}

while getopts ":o:t:h" opt; do
    case "$opt" in
        o) REPORT_FILE="$OPTARG" ;;
        t) THRESHOLD_FILE="$OPTARG" ;;
        h) usage ;;
        \?) log_error "非法参数: $OPTARG"; usage ;;
        :)  log_error "选项 -$OPTARG 需要参数值"; usage ;;
    esac
done

# ---- 读阈值配置（安全解析，不 source，避免执行任意代码）----
if [ -n "$THRESHOLD_FILE" ]; then
    if [ ! -f "$THRESHOLD_FILE" ]; then
        log_error "阈值配置文件不存在: $THRESHOLD_FILE"; exit 1
    fi
    while IFS='=' read -r key val; do
        [ -z "$key" ] && continue          # 跳过空行
        case "$key" in
            MEM_THRESHOLD)   MEM_THRESHOLD="$val" ;;
            DISK_THRESHOLD)  DISK_THRESHOLD="$val" ;;
            LOAD_THRESHOLD)  LOAD_THRESHOLD="$val" ;;
            *) log_error "未知阈值项: $key"; exit 1 ;;
        esac
    done < "$THRESHOLD_FILE"
fi

# ---- 采集 ----
HOST=$(hostname)
UPTIME=$(uptime -p 2>/dev/null || echo "未知")
NCORE=$(nproc)
LOAD1=$(cut -d' ' -f1 /proc/loadavg)

# 内存：free -m 的 Mem 行，使用率 = (total - available) / total
read -r mem_total mem_used mem_avail mem_percent < <(
    free -m | awk '/^Mem:/ {
        total=$2; used=$3; avail=$7;
        pct = (total>0) ? (total-avail)*100/total : 0;
        printf "%d %d %d %.1f", total, used, avail, pct
    }'
)

alarm_count=0
report_body=""

# 负载判定（awk 做浮点比较）
if awk -v l1="$LOAD1" -v nc="$NCORE" -v th="$LOAD_THRESHOLD" \
   'BEGIN{ exit (nc>0 && l1>th) ? 1 : 0 }'; then
    report_body+="[负载] 1min=${LOAD1} (核数=${NCORE})    [OK]\n"
else
    report_body+="[负载] 1min=${LOAD1} (核数=${NCORE})    [WARN]\n"
    alarm_count=$((alarm_count+1))
fi

# 内存判定
if awk -v p="$mem_percent" -v th="$MEM_THRESHOLD" \
   'BEGIN{ exit (p>th) ? 1 : 0 }'; then
    report_body+="[内存] 总量=${mem_total}MB 已用=${mem_used}MB 可用=${mem_avail}MB 使用率=${mem_percent}%  [OK]\n"
else
    report_body+="[内存] 总量=${mem_total}MB 已用=${mem_used}MB 可用=${mem_avail}MB 使用率=${mem_percent}%  [WARN]\n"
    alarm_count=$((alarm_count+1))
fi

# 磁盘判定（df -P 防换行，跳过伪文件系统）
while read -r fs size used avail pct mount; do
    [ "$fs" = "Filesystem" ] && continue
    case "$fs" in tmpfs|devtmpfs|proc|sysfs|udev|overlay) continue ;; esac
    pctnum="${pct%\%}"
    if awk -v p="$pctnum" -v th="$DISK_THRESHOLD" \
       'BEGIN{ exit (p>th) ? 1 : 0 }'; then
        report_body+="[磁盘] $fs $mount 使用率=${pct}  [OK]\n"
    else
        report_body+="[磁盘] $fs $mount 使用率=${pct}  [WARN]\n"
        alarm_count=$((alarm_count+1))
    fi
done < <(df -hP | tail -n +2)

# ---- 组装报告（先拼字符串，再 tee 双输出）----
report=$(cat <<EOF
==================== 系统资源巡检报告 ====================
生成时间: $(date '+%F %T')
主机: ${HOST}
运行时长: ${UPTIME}

$(echo -e "$report_body")
结论: ${alarm_count} 项告警
=========================================================
EOF
)

echo "$report" | tee "$REPORT_FILE"
exit 0
```

---

## 关键点讲解与最佳实践

1. **bash 没有浮点运算，这是本题最大的坑。** `(( ))` 只能算整数，`0.52 > 4.0` 这种比较必须交给 `awk`（或 `bc`）。上面统一用 `awk 'BEGIN{ exit 条件 ? 1 : 0 }'` 做浮点判定，再在 `if` 里承接退出码——和你在 `watchdog.sh` 里"用 `if` 承接 `healthcheck` 退出码"是同一个套路。

2. **`df -hP` 的 `-P` 别省。** 长设备名（如 `/dev/mapper/xxx`）默认会折行，导致 `while read` 读错字段。`-P` 强制一行一条记录，是解析 `df` 的标准姿势。同时要**过滤 `tmpfs`/`devtmpfs` 等伪文件系统**，否则报告里会冒出一堆没有意义的挂载点。

3. **使用率要用 `(total - available)/total`，而不是 `used/total`。** Linux 会把大量内存挪给 buff/cache，`used` 里包含它们，直接 `used/total` 会虚高。`available` 才是"应用程序真正还能用多少"，用它算使用率最接近真实压力。

4. **阈值配置不要直接 `source`。** `source` 陌生配置文件等价于"执行任意代码"，配置文件里写 `$(rm -rf /)` 就被执行了。用 `while IFS='=' read` 逐行解析 + `case` 白名单，只认已知的键，未知键直接报错——这是"配置与代码分离"的正确姿势，也符合 SRE 安全底线。

5. **报告"先拼字符串，再 `tee`"。** 把 `report_body` 一段段 `+=` 追加，最后一次性 `echo | tee`，既输出屏幕又落盘，也方便将来改成发邮件/推送到监控平台。

6. **`nproc` 是负载的参照系。** 负载 `4.0` 在 2 核机器上是"过载"，在 16 核机器上很轻松。所以判断负载要结合核数，进阶写法是"负载 / 核数 > 阈值"。

---

### 进阶提示（下一阶段再扩展）

- **负载对比核数**：把判断改成 `LOAD1 / NCORE > LOAD_THRESHOLD`，阈值语义更统一。
- **告警时退出码区分**：加 `-s`（strict）参数，有告警时返回非 0，让脚本能被 cron 或监控直接消费。
- **CPU 使用率**：`top -bn1` 或读 `/proc/stat` 两次取差值，补上 CPU 维度的采集。
- **定时执行**：下一题会引入 `cron` 与并发锁，届时把 `sysreport.sh` 挂进定时任务，每天生成快照。
- **与 09-30 综合巡检串联**：`server_check.sh` 会把 `healthcheck` + `watchdog` + `sysreport` 串成一条完整巡检流水线——本题就是那条流水线的"资源维度"拼图。

---

## 一句话记忆锚点

> **巡检报告的三个关键：浮点用 awk、df 要 -P、配置解析别 source。**
