以下内容可直接保存为 `docker-排障经验总结.md`。

# Docker 部署排障经验总结

> 本文档记录了一次真实部署过程中遇到的四类问题：Dockerfile 被 Vim 加密导致构建失败、容器"启动不了"实为正常退出、`docker start` 无法传参、容器日志时间与宿主机相差 8 小时。每个问题按 **现象 → 根因 → 解决 → 预防** 组织，末尾附速查清单。

---

## 目录

- [问题一：构建报 RST_STREAM，Dockerfile 被 Vim 加密](#问题一构建报-rst_streamdockerfile-被-vim-加密)
- [问题二：容器"启动不了"，实为程序跑完正常退出](#问题二容器启动不了实为程序跑完正常退出)
- [问题三：docker start 加参数报 unknown flag](#问题三docker-start-加参数报-unknown-flag)
- [问题四：容器日志时间与宿主机差 8 小时](#问题四容器日志时间与宿主机差-8-小时)
- [速查清单](#速查清单)
- [总结](#总结)

---

## 问题一：构建报 RST_STREAM，Dockerfile 被 Vim 加密

### 现象

```bash
$ docker build -t probe:1.0 .
ERROR: failed to build: failed to solve: Internal: stream terminated by RST_STREAM with error code: INTERNAL_ERROR
```

```bash
$ cat Dockerfile
VimCrypt~03![x\8EkNj6ah\
9|͙ԤQQ7Snk^SWThraD~AW!\#^HgYe|*O|Ҽ@ċLAV OlG/IZCtss)Q~},w;O>B}Fh:"<=KKf(3E 3;!RÊ6~!
...
```

### 根因

- `VimCrypt~03!` 是 **Vim 加密文件的魔数**，`03` 表示 Vim 9 的 XChaCha20-Poly1305 加密格式，后面全是密文。
- BuildKit 读取 Dockerfile 时拿到的是**二进制密文而非合法文本**，解析异常导致前端 gRPC 流被内部错误终止，表现为 `RST_STREAM INTERNAL_ERROR`。
- **不是 Docker 的问题，是文件本身已不是文本文件。**

### 解决

**知道密码（最常见）：**

```bash
vim Dockerfile
# 提示 Enter encryption key: 输入密码进入

# 进入后取消加密：
:set key=        # 回车后提示新 key，直接留空回车
:wq
```

等价做法：`vim` 中执行 `:X` → 提示新密码 → **直接回车留空** → `:wq`。

**不知道密码：** XChaCha20 无法暴力破解，只能删除重写。

```bash
rm Dockerfile && vim Dockerfile
```

### 验证

```bash
file Dockerfile          # 应为 ASCII text / UTF-8 Unicode text
xxd Dockerfile | head -3 # 开头不应是 56 69 6d 43 72 79 70 74 (VimCrypt)
head -5 Dockerfile       # 能看到 FROM ... 等正常内容
docker build -t probe:1.0 .
```

### 预防

- Dockerfile / compose.yaml / .env 这类**构建和部署文件绝不要用 Vim 加密**——Docker 构建过程必须读明文，加密了必然失败。
- 需要保密的内容（密码、密钥）走 `.env` + 权限控制 + 密钥管理，而不是加密构建文件本身。
- 警惕误触 `:X`（大写 X）、误用 `vim -x`。

---

## 问题二：容器"启动不了"，实为程序跑完正常退出

### 现象

```bash
$ docker ps -a
CONTAINER ID   IMAGE       COMMAND                   STATUS
ee829a2c3c93   probe:1.0   "python main.py --ho…"   Exited (0) 22 seconds ago
```

程序日志完整输出、报告正常落盘，但容器状态是 `Exited (0)`。

### 根因

- **`Exited (0)` 表示进程成功退出，不是报错。**
- 该程序是一次性脚本：探测主机 → 写报告 → 结束。**主进程一结束，容器生命周期即结束**，这是 Docker 的正常行为。
- 容器的存活 = 主进程（PID 1）的存活，进程退出容器就退出。

### 解决

一次性任务就**每次重新 `docker run`**，并加 `--rm` 自动清理：

```bash
docker run --rm \
  --name probe_container \
  -v "$(pwd)/hosts.txt:/app/hosts.txt:ro" \
  -v "$(pwd)/report:/app/report" \
  probe:1.0 --hosts-file hosts.txt --port 22
```

若需容器常驻（调试或服务化），改造方式见问题三方案 4。

### 预防

- 判断容器是否"失败"，**先看退出码**：`Exited (0)` 是正常，非 0 才是异常（`137`=被 kill、`1`=应用错误等）。
- 一次性任务不必执着于"让容器活着"，`--rm` + `docker run` 是标准用法。
- 需要周期性执行：用 `while true; do ...; sleep N; done` 写进 entrypoint，或改用 systemd timer / cron / K8s CronJob。

---

## 问题三：docker start 加参数报 unknown flag

### 现象

```bash
$ docker start probe_container --hosts-file hosts.txt --port 22
unknown flag: --hosts-file
Usage:  docker start [OPTIONS] CONTAINER [CONTAINER...]
```

即使只 `docker start probe_container`，容器跑完依旧 `Exited (0)`。

### 根因

1. **容器的启动命令在创建时就被焊死了**（`docker run` 时写死，`docker ps -a` 的 COMMAND 列就是它）。`docker start` 只是"用原命令再跑一遍"，**不能修改命令**。
2. **`docker start` 不支持给程序传参**，它后面的 `--xxx` 会被当成 `docker start` 自己的选项解析，不认识就报 `unknown flag`。
3. `docker start` 的合法选项只有 `-a`（attach）、`-i`（interactive）这类，**没有 `--hosts-file`、`--port`**。

### 解决

| 需求 | 做法 |
|------|------|
| **换参数重跑（推荐）** | `docker rm -f 容器名` 后重新 `docker run ...` 带新参数 |
| **一次性执行** | `docker run --rm ...`，用完即删 |
| **进容器手动调试** | `docker run --rm -it --entrypoint bash ...`，进去后手动执行命令 |
| **让容器常驻** | `docker run -d --entrypoint sleep 镜像 infinity`，之后 `docker exec -it 容器 python main.py ...` |
| **用 Compose** | `docker compose run --rm probe --hosts-file hosts.txt --port 22`（`run` 支持覆盖命令并传参） |

### 预防

- 牢记：**`docker run` = 创建 + 启动（可传参），`docker start` = 仅重放原命令（不可传参）**。
- 需要频繁换参数运行，优先用 `docker compose run`，比裸 `docker run` 友好。
- 同名容器冲突时先 `docker rm -f`，或全程用 `--rm` 避免残留。

---

## 问题四：容器日志时间与宿主机差 8 小时

### 现象

```text
容器日志：2026-11-06 10:20:11,435 - WARNING - probe - 探测失败: ...
宿主机：  2026年 11月 06日 星期五 18:26:34 CST
```

日志格式 `format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'` 没写错，但时间差正好 8 小时。

### 根因

- `%(asctime)s` 底层调用 `time.localtime()`，取的是**容器内的本地时间**，由 `TZ` 环境变量和 `/etc/localtime` 决定。
- 基础镜像（`python:3.x-slim`、`debian` 等）**默认无 `TZ`、`/etc/localtime` 指向 UTC**。
- **Docker 容器不继承宿主机时区**（设计如此，追求可移植性）。宿主机 CST(UTC+8)，容器 UTC，于是差 8 小时。

### 解决（按推荐程度排序）

**方案 1：运行时传 `TZ`（最推荐，零改动）**

```bash
docker run --rm -e TZ=Asia/Shanghai probe:1.0 ...
```

Compose 写法：

```yaml
services:
  probe:
    environment:
      - TZ=Asia/Shanghai
```

> 前提：镜像内有 tzdata（Debian / python-slim 一般自带；alpine 需 `apk add tzdata`）。

**方案 2：挂载宿主机时区文件**

```bash
docker run --rm \
  -v /etc/localtime:/etc/localtime:ro \
  -v /etc/timezone:/etc/timezone:ro \
  probe:1.0 ...
```

优点是直观，缺点是**依赖宿主机**，可移植性差。

**方案 3：Dockerfile 固化时区（镜像级统一）**

```dockerfile
ENV TZ=Asia/Shanghai
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*
```

适合"同一镜像到处部署"，所有容器免传参。

**方案 4：代码里显式时区（最严谨）**

日志统一 UTC 在多机、多时区部署时其实是好实践，关键是**让读日志的人知道是哪个时区**：

```python
logging.basicConfig(
    format='%(asctime)s UTC - %(levelname)s - %(name)s - %(message)s'
)
```

或在 Formatter 中把时间显式转成带时区的格式。

### 验证

```bash
docker run --rm probe:1.0 date                              # 容器内时间（UTC）
docker run --rm -e TZ=Asia/Shanghai probe:1.0 date          # 加了 TZ 后（CST）
date; cat /etc/timezone; ls -l /etc/localtime               # 宿主机时间/时区
```

### 预防

- 容器时区与宿主机不一致是**常态**，不是 bug，先确认再处理。
- 日志聚合（ELK/Loki）场景下，**统一 UTC 反而更规范**，建议在格式里显式标注时区，而不是盲目改成本地时间。
- 需要本地时间展示的，在展示层做时区转换，而非改动容器时区。

---

## 速查清单

### 排障顺序

```bash
# 1. 容器状态和退出码
docker ps -a                       # 看 STATUS：Exited (0) 是正常退出

# 2. 文件是否是文本
file Dockerfile                    # data / 二进制 → 检查是否被加密

# 3. 容器内时间与时区
docker run --rm 镜像 date
docker run --rm 镜像 sh -c 'cat /etc/timezone; ls -l /etc/localtime'

# 4. 宿主机对照
date; cat /etc/timezone; ls -l /etc/localtime
```

### 核心结论速记

| 现象 | 根因 | 一句话解决 |
|------|------|------------|
| `RST_STREAM INTERNAL_ERROR` + `cat` 乱码 | Dockerfile 被 Vim 加密 | `vim` 输密码 → `:set key=` 留空 → `:wq` |
| `Exited (0)`，日志完整 | 一次性脚本跑完正常退出 | 不是故障，`docker run --rm` 重跑 |
| `docker start` 报 `unknown flag` | 容器命令创建时固定，`start` 不能传参 | `docker rm` 后重新 `docker run` |
| 日志时间差 8 小时 | 容器默认 UTC，不继承宿主机时区 | `-e TZ=Asia/Shanghai` 或 Dockerfile 固化 |

### 常用命令对照

```bash
# 创建 + 启动（可传参）
docker run --rm --name 容器名 -e TZ=Asia/Shanghai -v ... 镜像 参数...

# 仅重放原命令（不可传参）
docker start 容器名

# 覆盖命令 + 传参（Compose）
docker compose run --rm 服务名 参数...

# 进容器调试
docker run --rm -it --entrypoint bash 镜像
```

---

## 总结

1. **构建失败先验文件**：`file` + `head -c 200 | cat -v`，确认 Dockerfile 是文本而非密文；`VimCrypt~` 开头就是被加密了。
2. **退出码定性质**：`Exited (0)` 是正常退出，非 0 才是故障；一次性任务不必让容器常驻。
3. **区分 run 与 start**：`docker run` 可传参，`docker start` 只重放原命令；换参数必须重建容器。
4. **时区是容器与宿主机的天然差异**：容器默认 UTC，按需用 `TZ` 环境变量、挂载时区文件或 Dockerfile 固化；日志统一 UTC 本身是合理实践，关键是**显式标注时区**。
5. **敏感配置不进 YAML/构建文件**：用 `.env` + 权限控制，而不是加密 Dockerfile——那只会让构建直接失败。