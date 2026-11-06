以下内容可直接保存为 `docker-compose-yaml-guide.md`。

# Docker Compose YAML 文件编写指南

> Docker Compose 的 YAML 文件本质上是一份**声明式的“环境蓝图”**：你用 YAML 描述“想要哪些服务、它们如何连接、数据存在哪里”，Compose 负责把这份描述翻译成底层的 Docker API 调用，最终拉起整套容器环境。本文从结构拆解到生产实践，完整说明如何编写这份文件。

---

## 目录

- [一、文件结构与核心概念](#一文件结构与核心概念)
  - [1.1 services：服务定义](#11-services服务定义)
  - [1.2 networks：网络定义](#12-networks网络定义)
  - [1.3 volumes：命名卷定义](#13-volumes命名卷定义)
- [二、实际运维开发中的常用模式](#二实际运维开发中的常用模式)
  - [2.1 基础 + 环境覆盖](#21-基础--环境覆盖最核心的模式)
  - [2.2 环境变量与敏感信息管理](#22-环境变量与敏感信息管理)
  - [2.3 运维向配置清单](#23-运维向配置清单)
- [三、生产级完整示例](#三生产级完整示例)
- [四、总结](#四总结)

---

## 一、文件结构与核心概念

一个标准的 Compose 文件（`compose.yaml` 或 `docker-compose.yml`）由**三个顶级块**构成：

```yaml
services:        # 核心：定义每个服务（容器）怎么跑
  web:
    ...
networks:        # 可选：自定义网络，控制服务间通信
  ...
volumes:         # 可选：命名卷，用于有状态数据的持久化
  ...
```

### 1.1 services：服务定义（文件的核心）

`services` 下每个键（如 `web`、`db`）就是一个**服务**，代表一类容器。Compose V2 中，同一项目内的服务默认加入同一个桥接网络，**服务名就是 DNS 主机名**，服务间可以直接用服务名互访（例如 `web` 连数据库写 `mysql:3306`，而不是 `127.0.0.1`）。

每个服务下的常用字段分为几类：

#### 镜像与构建

| 字段 | 说明 |
|------|------|
| `image` | 指定镜像，如 `mysql:8.0` |
| `build` | 从 Dockerfile 构建，可指定 `context`（构建上下文）和 `dockerfile` 路径 |

#### 网络与端口

| 字段 | 说明 |
|------|------|
| `ports` | 端口映射，格式 `宿主机:容器`，如 `"8080:80"` |
| `networks` | 将服务挂到指定网络 |
| `expose` | 仅对**同一网络内**的其他服务暴露端口，不映射到宿主机 |

#### 存储

| 字段 | 说明 |
|------|------|
| `volumes` | 挂载。两种形式：**绑定挂载**（`./src:/app`，宿主机路径直接映射）和**命名卷**（`db_data:/var/lib/mysql`，由 Docker 管理，适合数据库等有状态服务） |

#### 环境与配置

| 字段 | 说明 |
|------|------|
| `environment` | 直接写环境变量（键值对或列表形式） |
| `env_file` | 从 `.env` 文件加载，**敏感信息推荐用这种方式，不要硬编码在 YAML 里** |
| `command` / `entrypoint` | 覆盖镜像默认的启动命令 |

#### 生命周期与依赖

| 字段 | 说明 |
|------|------|
| `depends_on` | 声明启动顺序。**注意：它只保证“先启动容器”，不保证“容器内的服务已就绪”**。MySQL 容器起来了但数据库还没准备好接受连接，依赖它的服务一样会失败。生产环境应配合 `healthcheck` 使用 `condition: service_healthy` |
| `restart` | 重启策略。`always` 或 `unless-stopped` 是生产环境的标配，保证宿主机重启或容器异常退出后自动拉起 |
| `healthcheck` | 定义健康检查命令和参数（`interval`、`timeout`、`retries`），配合 `depends_on` 的 `condition` 实现“真正就绪后再启动依赖方” |

### 1.2 networks：网络定义

如果不显式定义，Compose 会自动创建一个默认网络，所有服务都在其中。需要**隔离**时（例如让前端和数据库不在同一网段，或让某些服务只能通过反向代理访问），可以定义多个自定义网络，用 `driver` 指定驱动（常用 `bridge`）。

> 🔒 生产环境中，**只暴露必要端口到宿主机**，其余服务间通信走内部网络，是基本的安全习惯。

### 1.3 volumes：命名卷定义

在顶级 `volumes` 下声明命名卷后，服务中才能引用。命名卷由 Docker 管理，**容器删除后数据仍然保留**，适合数据库、消息队列等有状态服务。绑定挂载则适合开发时将本地代码挂进容器实现热更新。

---

## 二、实际运维开发中的常用模式

实际生产中，Compose 文件很少“一份走天下”，更常见的是一套**分层的、按环境拆分的组合**。

### 2.1 基础 + 环境覆盖（最核心的模式）

将**与环境无关的公共配置**放在 `compose.yaml`，开发和生产各自用独立的覆盖文件追加差异：

#### 基础文件：`compose.yaml`

```yaml
services:
  app:
    build: ./app
    restart: unless-stopped
    environment:
      - NODE_ENV=production
```

#### 开发覆盖：`compose.override.yaml`（`docker compose up` 自动加载）

```yaml
services:
  app:
    build:
      target: development
    volumes:
      - ./app/src:/app/src:cached   # 开发时挂载源码热更新
    ports:
      - "9229:9229"                 # 调试端口
    environment:
      - NODE_ENV=development
      - DEBUG=*
```

#### 生产覆盖：`compose.prod.yaml`（显式指定）

```yaml
services:
  app:
    build:
      target: production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

#### 使用方式

```bash
# 开发：自动合并 compose.yaml + compose.override.yaml
docker compose up

# 生产：显式叠加 prod 覆盖
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

> 覆盖文件**只需写与基础文件的差异**，Compose 会将它们逐层合并。

### 2.2 环境变量与敏感信息管理

**永远不要把密码、密钥硬编码在 YAML 里**。推荐用 `.env` 文件 + 环境变量插值：

#### Compose 文件中的引用

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASS}
      MYSQL_DATABASE: ${DB_NAME}
```

#### `.env` 文件（不提交到 Git）

```bash
MYSQL_ROOT_PASS=StrongPass!2025
DB_NAME=myapp
```

#### 按环境启动

```bash
docker compose --env-file .env.prod up -d
```

> 📌 **提交一个 `.env.template` 到仓库**，只写变量名不写值，方便团队协作时知道需要配置哪些变量。

### 2.3 运维向配置清单

在实际运维中，以下几类配置几乎是“标配”：

| 类别 | 关键配置 | 作用 |
|------|----------|------|
| **重启** | `restart: unless-stopped` | 异常退出或宿主机重启后自动拉起，避免人工介入 |
| **健康检查** | `healthcheck` + `depends_on.condition` | 确保依赖服务**真正就绪**后再启动，而非仅“容器已启动” |
| **资源限制** | `deploy.resources.limits`（cpus / memory） | 防止单个服务耗尽宿主机资源 |
| **安全加固** | `user: "1000:1000"`、`read_only: true`、`cap_drop: [ALL]` | 以非 root 运行、只读文件系统、丢弃多余能力，最小化攻击面 |
| **日志** | `logging.options.max-size` / `max-file` | 防止日志无限膨胀占满磁盘 |
| **网络隔离** | 多自定义网络 + 仅必要端口映射 | 数据库等内部服务不暴露到宿主机 |
| **代码保护** | 生产环境**移除源码绑定挂载** | 代码固化在镜像内，外部不可篡改 |

> ⚠️ **一个容易忽略的点：`version` 字段已过时**
> 在 Compose V2（特别是 v2.42+）中，顶级 `version` 字段**已不再需要**，写了也不会报错但属于冗余。直接以 `services:` 开头即可。

---

## 三、生产级完整示例

下面这份 `compose.prod.yaml` 展示了运维中常见的组合：Web 应用 + 数据库 + 缓存，带健康检查、资源限制、安全配置和健康依赖：

```yaml
services:
  app:
    build:
      context: .
      target: production
    restart: unless-stopped
    ports:
      - "80:3000"
    environment:
      DB_HOST: db
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_HOST: cache
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    networks:
      - backend
      - frontend
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  db:
    image: mysql:8.0
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - backend
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - backend
    command: redis-server --requirepass ${REDIS_PASSWORD}

networks:
  frontend:        # app 对外，db/cache 不在其中
  backend:         # 内部通信网络

volumes:
  db_data:
```

### 关键设计点解读

- 🛡️ **网络隔离**：`db` 和 `cache` 只挂在 `backend` 网络，**不暴露到宿主机**，只有 `app` 同时挂在 `frontend` 和 `backend`，充当唯一入口。
- 🩺 **健康依赖**：`app` 通过 `condition: service_healthy` 等待 `db` 真正就绪，而不是仅仅容器启动。
- 🔐 **敏感信息**：所有敏感值通过 `${...}` 从 `.env` 注入，YAML 本身不包含明文密码。
- 💾 **数据持久化**：`db_data` 命名卷保证 MySQL 数据在容器重建后不丢失。

---

## 四、总结

**`services` 定义“跑什么”，`networks` 和 `volumes` 定义“怎么连、怎么存”；实际运维中，用“基础 + 覆盖”拆分环境，用 `.env` 管理敏感信息，用 `healthcheck` 和 `restart` 保证可用性，用多网络隔离和安全配置收敛攻击面。**