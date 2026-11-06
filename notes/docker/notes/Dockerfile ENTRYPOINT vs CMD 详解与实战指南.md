# Dockerfile ENTRYPOINT vs CMD 详解与实战指南

## 一、 核心概念速览

在 Dockerfile 中，`ENTRYPOINT` 和 `CMD` 都用于指定容器启动时默认执行的命令，但它们的职责、传参机制以及覆盖方式有明显的区别。

**一句话总结核心关系：**

> **`ENTRYPOINT` 定义容器的“主程序/可执行文件”，而 `CMD` 提供“默认参数”或“默认可替换命令”。**

---

## 二、 详细对比分析

### 1. CMD（默认命令 / 默认参数）

* **主要职责**：为容器启动提供默认的执行命令或参数。
* **覆盖机制**：如果在 `docker run` 命令行后指定了任何新命令或参数，**会完全覆盖** Dockerfile 中定义的 `CMD`。
* **典型场景**：适用于基础镜像的默认行为，或作为 `ENTRYPOINT` 的默认参数补充。

### 2. ENTRYPOINT（固定入口点）

* **主要职责**：将容器配置为一个专门的可执行程序（CLI 工具或服务进程）。
* **覆盖机制**：无论 `docker run` 后面传入什么参数，`ENTRYPOINT` 指定的程序**一定会被执行**。传入的参数会被追加（append）到 `ENTRYPOINT` 命令之后。
* **强制覆盖**：只有在 `docker run` 时显式使用 `--entrypoint` 参数才能将其覆盖。

### 3. 特性对比表

| 特性 | CMD | ENTRYPOINT |
| --- | --- | --- |
| **主要用途** | 提供默认执行命令或默认参数 | 指定容器启动时固定运行的主程序 |
| **`docker run` 行为** | 完全覆盖（替换 CMD） | 参数追加（附加在 ENTRYPOINT 后） |
| **覆盖难度** | 极易（命令行直接传入即可） | 较难（必须使用 `--entrypoint` 标志） |
| **单独使用场景** | 通用基础镜像、可交互 Shell | 单一功能的工具镜像（CLI 容器） |

---

## 三、 执行格式对比：Exec 格式 vs Shell 格式

`CMD` 和 `ENTRYPOINT` 都支持两种书写格式，格式的选择对容器信号传递（如 SIGTERM 优雅退出）至关重要。

### 1. Exec 格式（强烈推荐）

* **语法**：`["executable", "param1", "param2"]`
* **运行原理**：直接调用可执行文件，进程作为容器内 **PID 1** 运行。
* **优点**：能够正确接收和处理 Linux 信号（如 `docker stop` 发送的 SIGTERM 信号），实现优雅停机。

### 2. Shell 格式（不推荐）

* **语法**：`command param1 param2`
* **运行原理**：命令会被包装在 Shell 中执行（实质为 `/bin/sh -c "command param1 param2"`）。
* **缺点**：Shell 进程占据 PID 1，主程序作为子进程运行，无法直接接收 Linux 信号，可能导致 `docker stop` 超时强杀。

---

## 四、 组合使用模式与 Demo 示例

`ENTRYPOINT` 与 `CMD` 最强大的地方在于联合使用：**用 ENTRYPOINT 定义主程序，用 CMD 定义默认参数**。

### Demo 1：基础组合（以 Curl CLI 工具为例）

#### Dockerfile 定义：

```dockerfile
FROM alpine:latest
RUN apk add --no-cache curl

# 固定主程序为 curl，设置默认参数为 --help
ENTRYPOINT ["curl"]
CMD ["--help"]

```

#### 运行效果测试：

1. **直接运行（使用默认 CMD）：**
```bash
docker run my-curl-image
# 实际执行命令：curl --help

```


2. **传入参数运行（覆盖 CMD）：**
```bash
docker run my-curl-image https://api.github.com
# 实际执行命令：curl https://api.github.com

```


3. **传入多参数运行：**
```bash
docker run my-curl-image -I https://google.com
# 实际执行命令：curl -I https://google.com

```



---

### Demo 2：Web 应用镜像（Python Flask 示例）

#### Dockerfile 定义：

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install flask

# 固定运行 python app.py，提供默认端口 --port 8080
ENTRYPOINT ["python", "app.py"]
CMD ["--port", "8080", "--host", "0.0.0.0"]

```

#### 运行效果测试：

1. **按默认配置运行：**
```bash
docker run -p 8080:8080 my-web-app
# 实际执行：python app.py --port 8080 --host 0.0.0.0

```


2. **重写启动端口：**
```bash
docker run -p 9090:9090 my-web-app --port 9090 --host 0.0.0.0
# 实际执行：python app.py --port 9090 --host 0.0.0.0

```



---

## 五、 总结与最佳实践准则

1. **优先使用 Exec 格式**：使用 JSON 数组语法 `["executable", "param"]`，确保 PID 1 信号正确响应。
2. **需要 CLI 行为时**：使用 `ENTRYPOINT` 指定核心程序，使用 `CMD` 指定默认可变参数。
3. **需要灵活覆盖时**：如果镜像仅作为常规运行环境或调试容器，单独使用 `CMD` 更加灵活。
4. **记住解析规则**：当两者同时存在时，Docker 会将 `CMD` 的内容作为参数数组传递给 `ENTRYPOINT`。