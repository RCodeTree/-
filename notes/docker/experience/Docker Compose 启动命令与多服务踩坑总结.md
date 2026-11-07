# Docker Compose 启动命令与多服务踩坑总结

> 本文档记录将 probe 工具（main.py 探活 + mock_server.py 上报接收端）容器化并编排成两个服务时，踩到的坑和学到的核心机制。按 **核心机制 → 踩坑记录 → 速查** 组织。

---

## 目录

- [一、核心机制：容器启动命令 = ENTRYPOINT + command](#一核心机制容器启动命令--entrypoint--command)
- [二、两种 Compose 写法（有 / 无 ENTRYPOINT）](#二两种-compose-写法有--无-entrypoint)
- [三、踩坑记录](#三踩坑记录)
  - [坑 1：mock_server 跑成了 main.py（entrypoint 追加机制）](#坑-1mock_server-跑成了-mainpyentrypoint-追加机制)
  - [坑 2：condition: service_healthy 却无 healthcheck](#坑-2condition-service_healthy-却无-healthcheck)
  - [坑 3：环境变量列表写法里的双引号](#坑-3环境变量列表写法里的双引号)
  - [坑 4：python vs python3](#坑-4python-vs-python3)
  - [坑 5：容器内绑定 127.0.0.1 连不上](#坑-5容器内绑定-127001-连不上)
- [四、速查清单](#四速查清单)

---

## 一、核心机制：容器启动命令 = ENTRYPOINT + command

**这是 Docker 最容易被误解的一条规则：**

> 容器最终执行的命令 = `ENTRYPOINT`（主程序）+ `command`（参数），两者**拼接**而成。

compose 里的两个字段对应镜像里的两个指令：

| compose 字段 | 覆盖镜像里的什么 | 作用 |
| :--- | :--- | :--- |
| `entrypoint:` | 覆盖 `ENTRYPOINT` | 决定「**启动哪个程序**」 |
| `command:` | 覆盖 `CMD` | 决定「**给程序传什么参数**」 |

**关键点：`command` 不是「完整的启动命令」，它的角色取决于镜像里有没有 `ENTRYPOINT`：**

| 镜像里有没有 ENTRYPOINT | `command:` 的角色 |
| :--- | :--- |
| **有** `ENTRYPOINT ["python3","main.py"]` | 只是**参数**，追加在 entrypoint 后面 |
| **没有** ENTRYPOINT | 就是**完整命令**，直接执行 |

---

## 二、两种 Compose 写法（有 / 无 ENTRYPOINT）

### 方案 A：Dockerfile 写 ENTRYPOINT（镜像"自带"启动方式）

```dockerfile
# Dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["python3", "main.py"]      # 固定主程序
```

```yaml
# compose.yaml —— command 只传参数
services:
  mock_server:
    build: .
    entrypoint: ["python3", "mock_server.py"]   # 要换程序，必须覆盖 entrypoint
    command: ["8000"]                           # 追加参数
    ports:
      - "8000:8000"

  probe:
    build: .
    command: ["--hosts-file", "hosts.txt", "--port", "22"]   # 继承默认 entrypoint
    environment:
      - PROBE_API_URL=http://mock_server:8000/upload
    volumes:
      - ./hosts.txt:/app/hosts.txt:ro
      - ./report:/app/report
    depends_on:
      - mock_server
```

- `probe` 想跑 `main.py`，和镜像默认一致 → 只写 `command` 传参即可。
- `mock_server` 想跑 `mock_server.py`，和默认不一致 → 必须 `entrypoint` 换程序 + `command` 传参。

### 方案 B：Dockerfile 不写 ENTRYPOINT（镜像"裸"的）

```yaml
# compose.yaml —— command 写完整命令
services:
  mock_server:
    build: .
    command: ["python3", "mock_server.py", "8000"]   # 完整命令，一步到位
    ports:
      - "8000:8000"

  probe:
    build: .
    command: ["python3", "main.py", "--hosts-file", "hosts.txt", "--port", "22"]
    environment:
      - PROBE_API_URL=http://mock_server:8000/upload
    volumes:
      - ./hosts.txt:/app/hosts.txt:ro
      - ./report:/app/report
    depends_on:
      - mock_server
```

### 怎么选

| 方案 | 特点 | 适合 |
| :--- | :--- | :--- |
| **Dockerfile 写 ENTRYPOINT** | 镜像"自带"启动方式，compose 只传参，简洁 | 一个镜像**只干一件事** |
| **Dockerfile 不写** | 镜像"裸"的，compose 每处写全命令，直观 | **一个镜像多个角色**（如 probe：main.py + mock_server.py 共用一个镜像） |

---

## 三、踩坑记录

### 坑 1：mock_server 跑成了 main.py（entrypoint 追加机制）

**现象：**

```text
mock_server-1 | usage: main.py [-h] ...
mock_server-1 | main.py: error: the following arguments are required: --port
mock_server-1 exited with code 2
Container probe-mock_server-1 Error dependency mock_server failed to start
```

**根因：**

Dockerfile 有 `ENTRYPOINT ["python3", "main.py"]`，而 mock_server 只写了 `command: ["python", "mock_server.py", "8000"]`。`command` 不是覆盖而是**追加**，实际执行：

```text
python3 main.py python mock_server.py 8000
```

`main.py` 收到不认识的参数、又缺 `--port`，于是 argparse 报错退出（exit 2）→ `depends_on` 判定失败 → probe 也起不来。

> **判读技巧**：报错里出现的是 `main.py` 而不是 `mock_server.py`，说明「启动的程序错了」，顺着这个线索查 entrypoint。

**解决：**

给 mock_server 覆盖 `entrypoint`（见方案 A），或用方案 B 直接写完整 `command`。

---

### 坑 2：condition: service_healthy 却无 healthcheck

**现象：**

```yaml
depends_on:
  mock_server:
    condition: service_healthy
```

但 `mock_server` 服务**没有任何 `healthcheck:` 块** → compose 会**永远等它变 healthy**，probe 永远起不来。

**解决：**

- 学习/简单场景：去掉 condition，用 `depends_on: [mock_server]`（只保证启动顺序）。
- 生产场景：给服务补 `healthcheck` 定义，再用 `condition: service_healthy`。

---

### 坑 3：环境变量列表写法里的双引号

**现象：**

```yaml
environment:
  - PROBE_API_URL="http://mock_server:8000/upload"
```

**根因：**

在列表写法（`- KEY=value`）里，双引号会被当成**值的一部分**，requests 拿到的 URL 是带引号的 `"http://..."`，直接报错。

**解决：**

```yaml
# 列表写法：不加引号
- PROBE_API_URL=http://mock_server:8000/upload

# 或 map 写法（这里的引号才是合法的）
PROBE_API_URL: "http://mock_server:8000/upload"
```

> 记忆：**列表写法 `- K=V` 里别加引号；要引号就用 map 写法 `K: V`。**

---

### 坑 4：python vs python3

`python:3.14-slim` 等官方镜像里的标准命令是 **`python3`**（`python` 不一定存在）。

- Dockerfile 里用 `python3` ✅
- compose 的 `command` / `entrypoint` 里也统一用 `python3`

---

### 坑 5：容器内绑定 127.0.0.1 连不上

mock_server.py 若绑定 `127.0.0.1`，在容器里是「容器自己的回环地址」——**其他容器（probe）和宿主机都连不进来**，必须绑 `0.0.0.0`（监听所有网卡）：

```python
HTTPServer(("0.0.0.0", port), Handler).serve_forever()   # 容器化必需
```

> 同理：容器里的 `127.0.0.1` ≠ 宿主机 `127.0.0.1`。容器内探测 `127.0.0.1:22` 探的是容器自己，不是宿主机。

---

## 四、速查清单

### 启动命令机制

| 场景 | compose 写法 |
| :--- | :--- |
| 镜像有 ENTRYPOINT，跑默认程序 | 只写 `command: ["参数..."]` |
| 镜像有 ENTRYPOINT，要换程序 | `entrypoint: ["..."]` + `command: ["参数..."]` |
| 镜像无 ENTRYPOINT | `command: ["完整命令..."]` |

### 排障顺序

```bash
# 1. 看日志报的是哪个程序（判断 entrypoint 对不对）
docker compose logs 服务名

# 2. 看容器退出码
docker compose ps -a            # Exited (0) 正常，非 0 才是异常

# 3. 看实际启动命令
docker inspect 容器名 --format '{{.Config.Entrypoint}} {{.Config.Cmd}}'

# 4. 看环境变量是否注入正确
docker compose exec 服务名 env | grep PROBE_API_URL
```

### 核心结论速记

| 现象 | 根因 | 一句话解决 |
| :--- | :--- | :--- |
| 日志报 `main.py` 而非目标脚本 | ENTRYPOINT 占着主命令，command 被追加 | 覆盖 `entrypoint` 或写完整 `command` |
| probe 永远等 mock_server | `service_healthy` 无 `healthcheck` | 去掉 condition 或补 healthcheck |
| requests 报 URL 非法 | 列表写法里双引号成了值的一部分 | 列表写法别加引号 |
| `python` 命令找不到 | slim 镜像标准是 `python3` | 统一用 `python3` |
| 容器间连不上 | 服务绑了 `127.0.0.1` | 改绑 `0.0.0.0` |

---

## 总结

1. **容器启动命令 = ENTRYPOINT + command**，`command` 是「参数」还是「完整命令」，取决于镜像里有没有 ENTRYPOINT。
2. **一个镜像多角色**（probe 场景）时，Dockerfile 不写 ENTRYPOINT、compose 各自写完整 `command` 更直观；单职责镜像才适合用 ENTRYPOINT。
3. **判读技巧**：报错里的程序名、退出码、`docker inspect` 的启动命令，是定位「启动问题」的三板斧。
