# Debian 下配置清华大学镜像源安装 Docker 教程与 Shell 编写解析

本文档旨在提供在 Debian 系统下使用清华大学开源软件镜像站（TUNA）安装 Docker CE 的完整流程，同时结合 Shell 基础，解析其中涉及的高级命令行与脚本编写技巧。

---

## 第一部分：清华源 Docker 安装完整步骤

以下命令包含了完整的注释说明，可直接单行粘贴或写入脚本中运行。

```bash
#!/usr/bin/env bash
# ----------------------------------------------------------------------
# 说明: 在 Debian 系统上配置清华源并安装 Docker CE
# ----------------------------------------------------------------------

set -euo pipefail # 提升脚本安全性：遇到错误退出、变量未定义报错、管道错误传递

# 1. 卸载可能存在的旧版本软件包
echo "==> 1. 正在清理旧版本 Docker..."
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# 2. 安装必要的依赖软件包
echo "==> 2. 安装基础依赖包 (ca-certificates, curl, gnupg)..."
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg

# 3. 准备存放 GPG 密钥的目录，并下载 Docker 官方密钥
echo "==> 3. 配置 Docker GPG 密钥..."
sudo install -m 0755 -d /etc/apt/keyrings

# 下载官方密钥并转换为 gpg 格式存储
curl -fsSL https://download.docker.com/linux/debian/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 赋予所有用户读取密钥的权限
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 4. 配置 APT 软件源为清华大学 Docker 镜像站
echo "==> 4. 添加清华源 Docker 仓库..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. 更新本地软件源索引并安装 Docker 核心组件
echo "==> 5. 更新软件源并安装 Docker..."
sudo apt-get update -y
sudo apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

# 6. 验证安装结果
echo "==> 6. 验证 Docker 是否成功安装..."
sudo docker run --rm hello-world
```

---

## 第二部分：Shell 代码与脚本编写技巧教学

对于有 Shell 基础的技术人员，上述命令中有几个非常经典且高效的语法结构，适合运用到你日常编写的运维脚本中：

### 1. 动态获取系统与架构信息 (命令替换)

```bash
"deb [arch=$(dpkg --print-architecture) signed-by=...] ... $(. /etc/os-release && echo "$VERSION_CODENAME") stable"
```

*   **`$(dpkg --print-architecture)`**：
    *   **原理**：利用 `$()` 进行命令替换，动态打印当前系统的 CPU 架构（如 `amd64`、`arm64`）。
    *   **优点**：编写通用的安装脚本时，无需硬编码架构名称，保证脚本跨平台/跨架构兼容。
*   **`$(. /etc/os-release && echo "$VERSION_CODENAME")`**：
    *   **原理**：`/etc/os-release` 文件定义了 Linux 发行版的版本变量。通过 `.` (即 `source`) 在子 Shell 中加载该文件，直接提取环境变量 `$VERSION_CODENAME`（例如 Debian 12 对应的 `bookworm`），然后将其输出。
    *   **写脚本建议**：在需要根据 Linux 发行版版本进行分支判断或拼接 URL 时，优先使用环境变量文件 `/etc/os-release`。

### 2. 安全写入需要 Root 权限的文件 (`tee` 技巧)

```bash
echo "内容" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

*   **为什么不用 `sudo echo "内容" > /etc/...`？**
    *   在 Shell 中，重定向符号 `>` 是由**当前 Shell 进程**执行的，而不是由 `sudo` 运行的命令执行。因此即使前面加了 `sudo`，当前无权账户同样无法写入 `/etc/` 下的文件。
*   **`tee` 的优势**：
    *   `sudo tee` 会以管理员身份运行并接管标准输入。
    *   末尾加上 `> /dev/null` 是为了屏蔽 `tee` 默认在终端打印内容的行为，保持脚本终端界面的干净干净整洁。

### 3. GPG 密钥格式转换与权限控制

```bash
curl -fsSL https://.../gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

*   **`curl` 参数说明**：
    *   `-f` (--fail)：HTTP 请求报错（如 404）时立刻退出，不输出错误 HTML 页面。
    *   `-s` (--silent)：静音模式，不显示进度条。
    *   `-L` (--location)：如果服务器返回重定向（301/302），自动跟踪重定向。
*   **`gpg --dearmor`**：
    *   将 OpenPGP ASCII Armor 格式（Base64 文本格式）转换为二进制的 OpenPGP 格式。标准的 APT keyrings 目前推荐使用二进制 `.gpg` 扩展名存放。

### 4. 脚本防御性编程规范 (`set -euo pipefail`)

在编写自动化 Shell 安装脚本时，建议在顶部放置如下声明：

```bash
set -euo pipefail
```

*   **`-e` (errexit)**：任何命令执行返回非 0 状态码时，立即终止脚本运行。
*   **`-u` (nounset)`**：尝试使用未声明的变量时报错退出。
*   **`-o pipefail`**：管道中只要有一个子命令失败，整个管道就返回失败状态，防止如 `bad_cmd | tee file` 时掩盖 `bad_cmd` 的错误。