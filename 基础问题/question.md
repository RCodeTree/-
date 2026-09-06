**1. root 用户和普通用户最大的区别是什么？**

* **权限级别**：`root` 是超级管理员（UID 为 0），拥有对系统的最高可读、可写、可执行权限，可以绕过几乎所有文件权限限制；普通用户（UID 通常 $\ge 1000$）权限受到受限，仅能在授权范围内或自己的家目录（`/home/username`）操作。

---

**2. `/etc/passwd` 和 `/etc/shadow` 分别保存什么信息？**

* **`/etc/passwd`**：保存系统所有用户的基本账户信息（用户名、UID、GID、用户主目录、默认 Shell 等），所有人均可读取。
* **`/etc/shadow`**：保存加密后的用户密码以及密码过期、更换时间等安全相关参数，仅 `root` 用户有权限读取。

---

**3. `ps aux` 主要是查看什么？**

* 查看当前系统中**所有运行进程的静态快照**（包含所有用户启动的进程、CPU/内存占用率、进程 PID、启动命令及运行状态等）。

---

**4. `kill` 和 `kill -9` 有什么区别？**

* **`kill`（默认发送 `SIGTERM / 15` 信号）**：请求进程终止，进程可以捕获该信号，在退出前完成保存数据、清理临时文件等“优雅退出”操作。
* **`kill -9`（发送 `SIGSIGKILL / 9` 信号）**：由内核直接将进程强制杀死，进程无法捕获或忽略，可能会导致数据丢失或文件损坏。

---

**5. 分区、格式化、挂载，这三步分别是什么意思？**

* **分区（Partition）**：将一块物理硬盘划分为一个或多个独立的逻辑区域（如 `/dev/sdb1`）。
* **格式化（Format）**：在分区上创建指定的文件系统（如 ext4、xfs），以便操作系统能够管理和存储文件。
* **挂载（Mount）**：将创建好文件系统的分区关联到 Linux 目录树中的某个指定目录，使该分区可以通过该目录被访问。

---

**6. `df -h` 和 `du -sh` 的区别是什么？**

* **`df -h`**：基于文件系统级别统计，查看**已挂载磁盘分区的整体容量及使用情况**（以易读格式如 GB/MB 显示）。
* **`du -sh`**：基于文件/目录级别统计，计算**指定目录或文件实际占用的磁盘空间总大小**。

---

**7. `ip addr` 主要用来看什么？**

* 查看当前系统所有网络接口（网卡）的配置信息，包括 IP 地址（IPv4/IPv6）、MAC 地址、网卡状态（UP/DOWN）等。

---

**8. `ping` 能说明什么，不能说明什么？**

* **能说明**：本网卡工作正常，与目标主机的**网络层（IP 层）连通性正常**，以及网络往返时延（RTT）和丢包率。
* **不能说明**：目标主机的应用层服务（如 HTTP 80 端口、MySQL 3306 端口）是否正常运行，也无法说明防火墙是否拦截了具体的 TCP/UDP 流量。

---

**9. `systemctl status nginx` 的作用是什么？**

* 查看 Nginx 服务的**运行状态**（Active/Inactive/Failed）、是否已设为开机自启、主进程 PID 以及近期运行日志摘要。

---

**10. `enable` 和 `start` 的区别是什么？**

* **`start`**：**立即启动**服务（只影响当前状态，重启服务器后失效）。
* **`enable`**：设置服务**开机自启**（创建软链接，不影响当前服务运行状态）。

---


### 场景 1：权限迷云

**1. 检查该文件权限的命令**
```bash
# 最常用，查看详细权限和所有者
ls -l /opt/backup.sh

# 更详细的查看（包括修改时间、属性等）
stat /opt/backup.sh
```
`-rw-r--r--` 解读：`root` 可读写，`root` 组可读，其他人（`student`）**只可读，不可执行**。

**2. 让 student 用户能够执行的两种方案**

- **方案一（推荐，最小权限原则）：仅添加执行权限**
  ```bash
  # 给其他用户（o）增加执行权限（x）
  sudo chmod o+x /opt/backup.sh
  ```
  执行后权限变为 `-rw-r--r-x`。此时 `student` 可以执行脚本，但需要留意：如果脚本内部有写日志、改系统文件等操作，`student` 可能因权限不够而报错（需要看方案二）。

- **方案二（处理内部需提权）：修改 sudoers，允许 student 无密码执行该脚本**
  ```bash
  # 执行 visudo 编辑配置文件
  sudo visudo
  # 在文件末尾添加一行
  student ALL=(ALL) NOPASSWD: /opt/backup.sh
  ```
  添加后，`student` 只需执行 `sudo /opt/backup.sh` 即可像 root 一样运行该脚本。

- **方案三（备选）：更改所有者**
  如果该脚本只给 `student` 用，直接改所有者。
  ```bash
  sudo chown student:student /opt/backup.sh
  sudo chmod u+x /opt/backup.sh   # 仅给所有者加执行权
  ```

---

### 场景 2：服务起不来

**1. 用 journalctl 查看具体报错原因**
```bash
# 最常用组合：-u 指定服务，-xe 显示详细详情并跳转到末尾
sudo journalctl -u nginx.service -xe

# 只看最近 30 条日志
sudo journalctl -u nginx.service -n 30

# 查看从刚才重启时刻开始的日志（结合 -f 实时追踪）
sudo journalctl -u nginx.service --since "5 minutes ago" -f
```

**2. 日志提示 "Address already in use"（端口被占用）**
通常 Nginx 默认占用 80（HTTP）或 443（HTTPS）端口。用以下命令找出占用的进程：
```bash
# 方法一（最快）：ss 命令查看监听中的端口并显示进程
sudo ss -tlnp | grep :80
sudo ss -tlnp | grep :443

# 方法二（经典）：netstat
sudo netstat -tlnp | grep :80

# 方法三（万能）：lsof 直接列出使用某端口的进程
sudo lsof -i :80
```
执行后，会显示进程 PID 和程序名（比如发现是 `httpd` 或另一个 `nginx` 残留）。可以 `kill -9 PID` 杀掉它，再重启 Nginx。

---

### 场景 3：磁盘报警

**1. 查看哪个分区满了**
```bash
# 查看磁盘分区使用率（人类可读格式）
df -h

# 查看 Inode（文件数）是否满了（有时空间有剩余但无法创建文件）
df -i
```
重点关注 `Use%` 列，找到达到 90% 或 100% 的挂载点（如 `/` 或 `/data`）。

**2. 找出占用空间最大的前 5 个目录或文件**

假设 `df -h` 发现 `/` 根分区满了，进入根目录排查：
```bash
# 进入该分区
cd /

# 组合命令（先查当前目录下各子目录大小，排序取前5）
sudo du -sh * 2>/dev/null | sort -rh | head -5
```
**命令拆解**：
- `du -sh *`：计算当前目录下每个子目录/文件的总大小（-s 汇总，-h 人类可读）。
- `2>/dev/null`：屏蔽因权限不足产生的错误信息（如 `/proc` 目录无法读取）。
- `sort -rh`：按人类可读的数字（-h）进行倒序（-r）排序。
- `head -5`：取前 5 行。

**（进阶）如果第一层目录太多了，想全局找大文件**：
```bash
# 查找 / 下所有大于 100M 的文件，按大小排序取前5
sudo find / -type f -size +100M -exec du -h {} \; 2>/dev/null | sort -rh | head -5
```

---

### 场景 4：安全审计

**1. 查看登录失败的日志文件**
根据系统不同，日志位置有差异：

- **CentOS / RHEL / Fedora（RedHat 系）**：`/var/log/secure`
- **Ubuntu / Debian（Debian 系）**：`/var/log/auth.log`

**2. 查看最近 20 条关于 sshd 的错误日志**
这里提供两种最实用的写法（兼顾新旧系统）：

- **方法一（通用文本过滤，兼容性最好）**：
  ```bash
  # 以 CentOS 为例
  sudo tail -n 20 /var/log/secure | grep sshd
  # 或者精准匹配失败密码（更聚焦暴力破解）
  sudo tail -n 20 /var/log/secure | grep "sshd.*Failed password"
  ```

- **方法二（使用 systemd 的 journalctl，推荐）**：
  不管日志文件在哪，直接查 `sshd` 服务单元。
  ```bash
  # 查看 sshd 服务最近的 20 条日志（自动包含错误和认证信息）
  sudo journalctl -u sshd -n 20

  # 只看优先级为错误（err）级别的日志
  sudo journalctl -u sshd -p err -n 20
  ```

**小贴士**：如果发现大量 `Failed password` 记录，可以使用 `lastb` 命令直接查看所有登录失败的记录（`lastb` 读取的是 `/var/log/btmp` 二进制日志）。