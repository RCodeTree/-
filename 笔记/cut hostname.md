## 一、`cut` 命令

### 1. 作用
`cut` 用于从文本的每一行中“剪切”出指定部分，通常用于：
- 按字节截取
- 按字符截取
- 按字段截取，例如按 `:`、`,`、空格、制表符分割后取某几列

它不会重新排序，也不会做复杂文本处理。适合结构简单、分隔符固定的文本。

### 2. 基本语法
```bash
cut [选项]... [文件]...
```

如果不指定文件，或文件为 `-`，则从标准输入读取。

### 3. 三种主要模式
`cut` 有三个互斥的核心选项：

| 选项 | 含义 |
|---|---|
| `-b LIST` | 按字节位置选择 |
| `-c LIST` | 按字符位置选择 |
| `-f LIST` | 按字段选择，通常配合 `-d` |

`LIST` 可以是：
- `N`：第 N 个
- `N-`：从第 N 个到行尾
- `-N`：从开头到第 N 个
- `N-M`：从第 N 到第 M 个
- `N,M`：第 N 和第 M 个
- `N-M,X`：组合

例如：
```bash
cut -c1-5 file.txt
cut -d: -f1,3 /etc/passwd
cut -d: -f1,7- /etc/passwd
```

### 4. 常用选项

| 选项 | 说明 |
|---|---|
| `-d, --delimiter=CHAR` | 指定字段分隔符，只能是一个字符，默认是 TAB |
| `-f, --fields=LIST` | 选择字段 |
| `-c, --characters=LIST` | 选择字符 |
| `-b, --bytes=LIST` | 选择字节 |
| `-s, --only-delimited` | 只输出包含分隔符的行，常用于 `-f` |
| `--complement` | 反选，输出未被选中的部分 |
| `--output-delimiter=STRING` | 指定输出时的字段分隔符 |
| `-z, --zero-terminated` | 以 NUL 字符作为行分隔符，而不是换行 |
| `-n` | 与 `-b` 一起使用，尽量不拆分多字节字符 |
| `--help` | 显示帮助 |
| `--version` | 显示版本 |

### 5. 常见示例

#### 按字段截取
```bash
cut -d: -f1 /etc/passwd
```
输出 `/etc/passwd` 中每行第一个字段，即用户名。

```bash
cut -d: -f1,3 /etc/passwd
```
输出用户名和 UID。

```bash
cut -d: -f1,7- /etc/passwd
```
输出用户名以及第 7 个字段到行尾。

#### 按字符截取
```bash
cut -c1-10 file.txt
```
输出每行前 10 个字符。

#### 按字节截取
```bash
cut -b1-10 file.txt
```
输出每行前 10 个字节。处理 UTF-8 中文时要小心，因为一个中文字符可能占多个字节。

#### 反选字段
```bash
cut -d: -f2 --complement /etc/passwd
```
输出除了第 2 个字段以外的所有字段。

#### 修改输出分隔符
```bash
cut -d: -f1,3 --output-delimiter=' | ' /etc/passwd
```
输出时用 ` | ` 分隔字段。

#### 只处理有分隔符的行
```bash
cut -d: -f1 -s file.txt
```
没有 `:` 的行不会被输出。

### 6. 注意事项
- `-d` 只能指定单个字符，不能指定字符串或正则表达式。
- 默认字段分隔符是 TAB。
- 多个连续空格会被当成多个分隔符，容易产生空字段，因此不适合处理“空格对齐”的文本，这种情况通常用 `awk`。
- `-b`、`-c`、`-f` 三种模式不能混用。
- `--complement`、`--output-delimiter`、`-z` 多为 GNU 扩展。
- 处理中文时，`-c` 通常比 `-b` 更合适，但仍受 locale 和实现影响。

---

## 二、`hostname` 命令

### 1. 作用
`hostname` 用于：
- 显示当前系统主机名
- 临时设置主机名
- 查看短主机名、FQDN、域名、IP 地址等信息

在 systemd 系统中，永久修改主机名更推荐使用 `hostnamectl`。

### 2. 基本语法
```bash
hostname [选项] [新主机名]
```

常见形式：
```bash
hostname
hostname -s
hostname -f
hostname -I
sudo hostname new-name
```

### 3. 常用显示选项

| 选项 | 说明 |
|---|---|
| 无参数 | 显示当前完整主机名 |
| `-s, --short` | 显示短主机名，即第一个点之前的部分 |
| `-f, --fqdn, --long` | 显示完全限定域名 FQDN |
| `-d, --domain` | 显示 DNS 域名 |
| `-i, --ip-address` | 显示主机名对应的 IP，依赖名称解析 |
| `-I, --all-ip-addresses` | 显示所有非回环 IP 地址，不依赖 DNS |
| `-a, --alias` | 显示主机别名 |
| `-A, --all-fqdns` | 显示所有 FQDN |
| `-y, --yp, --nis` | 显示 NIS/YP 域名 |
| `-v, --verbose` | 详细输出 |
| `-h, --help` | 显示帮助 |
| `-V, --version` | 显示版本 |

### 4. 常见示例

#### 查看当前主机名
```bash
hostname
```

#### 查看短主机名
```bash
hostname -s
```
例如完整主机名是 `web01.example.com`，则输出 `web01`。

#### 查看 FQDN
```bash
hostname -f
```
输出类似：
```text
web01.example.com
```

#### 查看域名
```bash
hostname -d
```
输出：
```text
example.com
```

#### 查看所有 IP
```bash
hostname -I
```
输出类似：
```text
192.168.1.10 10.0.0.5
```

#### 查看主机名解析出的 IP
```bash
hostname -i
```
该选项依赖 `/etc/hosts` 或 DNS 解析，可能返回 `127.0.1.1`，不一定可靠。

### 5. 临时设置主机名
```bash
sudo hostname web01
```
这会立即修改当前内核中的主机名，但通常是临时的，重启后可能恢复。

也可以从文件读取：
```bash
sudo hostname -F /etc/hostname
```

### 6. 永久设置主机名
在 systemd 系统上推荐：
```bash
sudo hostnamectl set-hostname web01
```

如果需要设置完整域名：
```bash
sudo hostnamectl set-hostname web01.example.com
```

查看状态：
```bash
hostnamectl status
```

还可以检查：
```bash
cat /etc/hostname
```

通常还需要更新 `/etc/hosts`，例如：
```text
127.0.1.1 web01.example.com web01
```

### 7. `hostname` 与 `hostnamectl` 的区别

| 命令 | 特点 |
|---|---|
| `hostname` | 显示主机名；设置时通常是临时修改，重启可能丢失 |
| `hostnamectl` | systemd 工具，可管理静态、瞬态、灵活主机名，通常永久生效 |

### 8. 注意事项
- 设置主机名通常需要 `root` 权限。
- 主机名建议遵循 RFC 1123：字母、数字、连字符，点用于分隔域名。
- `hostname -f` 返回异常，常见原因是 `/etc/hosts` 或 DNS 配置不完整。
- `hostname -i` 依赖解析，容器或云主机中可能返回不符合预期的地址。
- 在 Docker/Kubernetes 等容器环境中，主机名可能被隔离，修改效果受容器配置限制。

---

### 简要总结
- `cut`：按字节、字符或字段截取文本，适合分隔符固定的简单文本处理。
- `hostname`：查看或临时设置主机名，查看短名、FQDN、IP 等信息；永久修改建议用 `hostnamectl set-hostname`。