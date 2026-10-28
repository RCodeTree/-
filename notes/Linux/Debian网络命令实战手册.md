# Debian 网络命令实战手册

> 理论部分（OSI 七层、ARP/IP/ICMP、封装解封装、子网划分、静态/动态路由、TCP 三次握手/四次挥手、UDP、HTTP/HTTPS）已完整掌握，见《计算机网络》笔记。
> 本手册**只聚焦 Debian 命令实操**，每条命令都挂回理论概念，方便「用命令验证原理」。

---

## 0. 工具安装

```bash
sudo apt update
sudo apt install -y iproute2 dnsutils netcat-openbsd traceroute curl
```

| 包 | 提供的命令 | 说明 |
| -- | -- | -- |
| `iproute2` | `ip`、`ss` | Debian 一般自带，现代标准工具 |
| `dnsutils` | `dig`、`nslookup`、`host` | DNS 查询 |
| `netcat-openbsd` | `nc` | 端口探测 |
| `traceroute` | `traceroute` | 路由路径追踪 |
| `net-tools`（旧） | `ifconfig`、`netstat`、`route`、`arp` | 旧工具，老教程常见，不推荐 |

---

## 1. 现代 vs 旧命令对照（避免被老教程带偏）

| 功能 | ❌ 旧（net-tools） | ✅ 新（iproute2） |
| -- | -- | -- |
| 看 IP | `ifconfig` | `ip addr` |
| 看网卡 / MAC | `ifconfig` | `ip link` |
| 路由表 | `route -n` | `ip route` |
| ARP 表 | `arp -n` | `ip neigh` |
| 端口 / 连接 | `netstat -tlnp` | `ss -tlnp` |

---

## 2. 第 2 层（数据链路层）

### `ip link` — 网卡 & MAC 地址

**对应概念**：网卡只认 MAC 地址（ARP 存在的意义就在这）。

```bash
ip link show
```

```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 ... state UNKNOWN
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 ... state UP
    link/ether 52:54:00:12:34:56 brd ff:ff:ff:ff:ff:ff
```

- `lo`：回环接口（`127.0.0.1` 那块「虚拟网卡」）。
- `eth0` 的 `link/ether 52:54:...`：这块网卡的 **MAC 地址**。
- `UP`：网卡已开启；`LOWER_UP`：物理链路通（网线插着）。
- 常用参数：`ip link set eth0 up/down` 开关网卡。

---

## 3. 第 3 层（网络层）

### 3.1 `ip addr` — IP + 子网掩码

**对应概念**：IP 地址 = 网络号 + 主机号；子网掩码决定划分。

```bash
ip addr show
```

```
inet 192.168.1.100/24 brd 192.168.1.255 scope global eth0
```

- `/24` = 子网掩码 `255.255.255.0` → 网络号 `192.168.1.0`，主机号 `.100`。
- `brd`：广播地址。
- `scope global`：对外通信地址；`scope link`：只在本网段有效。

### 3.2 `ip route` — 路由表

**对应概念**：静态路由 / 默认路由 / 下一跳网关。

```bash
ip route show
```

```
default via 192.168.1.1 dev eth0                    # 默认路由：跨网段先交给网关
192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.100   # 本网段直连
```

- 第一行 `default via ...` 就是「默认路由（特殊静态路由）」，跨网段通信时数据包先交给这个网关。

### 3.3 `ip neigh` — ARP 缓存表

**对应概念**：ARP「查缓存 → 广播请求 → 单播应答 → 缓存」。

```bash
ip neigh show
```

```
192.168.1.1 dev eth0 lladdr 52:54:00:aa:bb:cc REACHABLE
192.168.1.50 dev eth0 lladdr 52:54:00:xx:yy:zz STALE
```

- `lladdr`：IP → MAC 的映射（即 ARP 缓存表内容）。
- `REACHABLE`：刚确认过；`STALE`：过期待刷新。

### 3.4 `ping` — ICMP 诊断

**对应概念**：ICMP Echo Request / Echo Reply。

```bash
ping -c 4 192.168.1.1   # -c 4 发 4 个包就停；Debian 不 -c 会一直 ping，Ctrl+C 中断
```

### 3.5 `traceroute` — 路由路径（TTL + ICMP）

**对应概念**：TTL 减到 0 触发 ICMP 差错报文。

```bash
traceroute 8.8.8.8
```

原理：TTL 从 1 开始逐步 +1，每到一跳 TTL 归零，该路由器回 ICMP「超时」报文，从而逐跳列出路径——正好用上「TTL 减到 0 生成 ICMP 差错报文」。

---

## 4. 第 4 层（传输层）

### 4.1 `ss` — 监听端口 / 连接状态

```bash
ss -tlnp    # t=TCP l=监听 n=不解析域名 p=显示进程
ss -tunap   # 所有 TCP/UDP 连接
```

```
LISTEN  0  128  0.0.0.0:22  *:*  users:(("sshd",pid=700,fd=3))
```

- `0.0.0.0:22`：sshd 监听**所有网卡**的 22 端口（`0.0.0.0` = 监听本机所有网卡）。
- 起 mock_server 后再跑，能看到 `0.0.0.0:8000` 和 `python3` 进程。

### 4.2 `nc` — 探测端口（= probe.py 的底层）

**对应概念**：TCP 三次握手。

```bash
nc -zv 127.0.0.1 22     # -z 只探测不发数据 -v 打印结果
```

- 返回 success = 三次握手完成，与 `asyncio.open_connection` 是同一件事。
- `nc -u` 走 UDP。

---

## 5. 第 7 层（应用层）

### 5.1 `dig` — DNS 查询

**对应概念**：DNS 协议（走 UDP）。

```bash
dig example.com +short        # 只回 IP
dig example.com               # 完整过程，看 ANSWER SECTION
```

```
;; ANSWER SECTION:
example.com.  3600  IN  A  93.184.216.34
```

- `A` 记录：域名 → IPv4；`3600`：TTL（缓存时长）。
- 之前 `getaddrinfo failed` 就是这一步查不到域名。

### 5.2 `curl` — HTTP 客户端（= upload.py 的底层）

**对应概念**：HTTP 请求行 / 头 / 空行 / 体 + 状态码。

```bash
curl -v http://example.com    # 完整交互：> 是请求，< 是响应
curl -I http://example.com    # 只看响应头
curl -X POST http://127.0.0.1:8000/upload \
     -H "Content-Type: application/json" \
     -d '[{"host":"1.2.3.4","alive":true}]'   # 手动模拟 upload.py
```

`-v` 输出里 `>` 开头是**请求**，`<` 开头是**响应**，能把「请求行 / 响应行、头、空行、体」可视化出来。

---

## 6. 实战练习

1. **第 3 层**：`ip addr` 找本机 IP + 掩码；`ip route` 找默认网关；`ping -c 3` 网关。
2. **第 3 层 ARP 过程**：`sudo ip neigh flush all` 清空 → `ping -c 1` 网关 → 再 `ip neigh show`，观察网关的 IP→MAC「从无到有」（即 ARP 广播 → 应答 → 缓存）。
3. **第 4 层**：起 mock_server，`ss -tlnp` 找到 8000 和 PID；`nc -zv 127.0.0.1 8000` 探测；`kill` 掉服务再探测，对比结果。
4. **第 7 层**：`curl -v` 访问一个网址，在输出里标出请求行、Host 头、响应状态行、Content-Type；再用 curl POST 到 mock_server，看服务端打印。

---

## 附：常用命令速查

| 命令 | 作用 | 层 |
| -- | -- | -- |
| `ip link` | 网卡 / MAC | 2 |
| `ip addr` | IP / 掩码 | 3 |
| `ip route` | 路由表 | 3 |
| `ip neigh` | ARP 缓存 | 3 |
| `ping` | ICMP 连通性 | 3 |
| `traceroute` | 路由路径 | 3 |
| `ss` | 端口 / 连接 | 4 |
| `nc` | 端口探测 | 4 |
| `dig` | DNS 解析 | 7 |
| `curl` | HTTP 客户端 | 7 |
