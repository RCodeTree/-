### 1. CPU：负载（load average）是核心指标

```bash
nproc        # CPU 核心数
uptime       # 看 "load average: 0.00, 0.01, 0.05"
```

`load average` 后面三个数，分别是**过去 1 分钟 / 5 分钟 / 15 分钟**的平均负载。

**⭐ 面试必考判断标准：**
- 负载 = "正在运行 + 等待运行"的任务数
- **负载 > CPU 核心数** = 系统过载（任务排队了）
- 单核机器负载持续 >1、4核机器负载持续 >4，就要警惕

### 2. 内存：`available` 和 `free` 的区别（高频坑）

```bash
free -m        # 重点看 available 这一列，不是 free
```

```
              total   used   free   ...  available
Mem:          3915    1230   512    ...  2100
```

**⭐ 关键认知**：`free` 显示的"空闲"很小不代表内存不够，因为 Linux 会用空闲内存做缓存（page cache）。**真正能分配给新进程的是 `available`**。判断内存是否紧张，用 `available/total`。

### 3. 磁盘：空间 + inode 都要看（最容易漏）

```bash
df -h        # 看空间使用率 Use%
df -i        # 看 inode 使用率（文件数量是否耗尽）
```

**⭐ 常见事故**：磁盘空间明明还有，但报"磁盘已满"——往往是 **inode 耗尽**（小文件太多）。所以巡检要两个都看。

### 4. 网络：IP + 监听端口 + 连接数

```bash
hostname -I        # 本机所有 IP
ss -tlnp           # 看监听中的 TCP 端口（-t tcp -l 监听 -n 数字 -p 进程）
ss -s              # 连接数汇总
```

---
