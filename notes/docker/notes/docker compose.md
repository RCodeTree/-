# Docker Compose 常用命令

> 💡 **说明**：Docker Compose V2 已集成到 Docker CLI 中，命令格式为 `docker compose`（中间是空格）。老版本 V1 使用 `docker-compose`（带连字符）。以下以 V2 为准，V1 用法一致，只需替换命令前缀。

---

## 目录

- [一、启动与停止（最常用）](#一启动与停止最常用)
- [二、查看状态与日志](#二查看状态与日志)
- [三、进入容器与执行命令](#三进入容器与执行命令)
- [四、构建与镜像](#四构建与镜像)
- [五、配置与校验](#五配置与校验)
- [六、清理与扩缩容](#六清理与扩缩容)
- [七、全局常用参数](#七全局常用参数)
- [八、典型日常工作流](#八典型日常工作流)

---

## 一、启动与停止（最常用）

| 命令 | 说明 |
|------|------|
| `docker compose up` | 创建并启动所有服务（前台运行，日志输出到终端） |
| `docker compose up -d` | 后台启动所有服务 |
| `docker compose up -d --build` | 重新构建镜像后后台启动 |
| `docker compose up <服务名>` | 只启动指定服务（含依赖服务） |
| `docker compose down` | 停止并删除容器、网络（**不删卷和镜像**） |
| `docker compose down -v` | 同时删除数据卷 |
| `docker compose down --rmi all` | 同时删除所有镜像 |
| `docker compose start` | 启动已存在的容器 |
| `docker compose stop` | 停止容器（不删除） |
| `docker compose restart` | 重启容器 |
| `docker compose pause` | 暂停容器 |
| `docker compose unpause` | 恢复容器 |

---

## 二、查看状态与日志

| 命令 | 说明 |
|------|------|
| `docker compose ps` | 列出项目中的容器状态 |
| `docker compose ps -a` | 包括已停止的容器 |
| `docker compose logs` | 查看所有服务日志 |
| `docker compose logs -f` | 实时跟踪日志（类似 `tail -f`） |
| `docker compose logs -f <服务名>` | 查看指定服务实时日志 |
| `docker compose logs --tail=100` | 只看最后 100 行 |
| `docker compose top` | 查看容器内运行的进程 |
| `docker compose images` | 列出项目使用的镜像 |

---

## 三、进入容器与执行命令

| 命令 | 说明 |
|------|------|
| `docker compose exec <服务> bash` | 进入运行中容器的交互式 shell |
| `docker compose exec <服务> <命令>` | 在运行中容器执行命令，如 `ls -l` |
| `docker compose exec -u root <服务> bash` | 以 root 用户进入 |
| `docker compose run <服务> <命令>` | 启动一个**新的一次性容器**执行命令 |
| `docker compose run --rm <服务> <命令>` | 执行完自动删除该临时容器 |
| `docker compose cp <容器>:<路径> <本地路径>` | 容器与主机间复制文件 |

---

## 四、构建与镜像

| 命令 | 说明 |
|------|------|
| `docker compose build` | 构建/重新构建服务镜像 |
| `docker compose build --no-cache` | 不使用缓存构建 |
| `docker compose build <服务名>` | 只构建指定服务 |
| `docker compose pull` | 拉取服务依赖的镜像 |
| `docker compose push` | 推送服务镜像 |
| `docker compose create` | 创建容器但不启动 |

---

## 五、配置与校验

| 命令 | 说明 |
|------|------|
| `docker compose config` | 校验并输出合并后的最终配置 |
| `docker compose config --services` | 列出所有服务名 |
| `docker compose ls` | 列出本机所有 Compose 项目 |
| `docker compose version` | 查看版本 |

---

## 六、清理与扩缩容

| 命令 | 说明 |
|------|------|
| `docker compose rm` | 删除已停止的容器 |
| `docker compose rm -f` | 强制删除（含运行中的） |
| `docker compose up -d --scale web=3` | 将 web 服务扩展到 3 个实例 |
| `docker compose down --remove-orphans` | 同时删除未在 compose 文件中定义的孤儿容器 |

---

## 七、全局常用参数

这些参数可加在大部分子命令后：

```bash
-f, --file <文件>        # 指定 compose 文件（可多个）
-p, --project-name <名>  # 指定项目名（默认取目录名）
--profile <名称>         # 启用指定 profile 的服务
--env-file <文件>        # 指定环境变量文件
--dry-run               # 试运行，只打印不执行
```

示例：

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose --env-file .env.prod up -d
```

---

## 八、典型日常工作流

```bash
# 1. 首次启动
docker compose up -d --build

# 2. 查看运行状态
docker compose ps

# 3. 跟踪日志
docker compose logs -f

# 4. 进入某个容器排查
docker compose exec app bash

# 5. 修改代码后重启单个服务
docker compose restart app

# 6. 修改配置/镜像后重建
docker compose up -d --build app

# 7. 收工清理（保留数据卷）
docker compose down
```

---

## 记忆技巧

日常操作记住以下五个命令，就能覆盖大部分场景：

```bash
docker compose up -d
docker compose down
docker compose ps
docker compose logs -f
docker compose exec
```

需要更细的命令说明时，可使用：

```bash
docker compose <命令> --help
```