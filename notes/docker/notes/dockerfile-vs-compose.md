# Dockerfile 与 Docker Compose 详解

> 结论先行：**它们不是"二选一"的两种写法，而是两个不同层次的东西，解决不同的问题，通常配合使用。** Dockerfile 是**构建层**（一个镜像怎么造），Compose 是**编排层**（一组容器怎么跑、怎么连）。

---

## 目录

- [一、Dockerfile 与 Docker Compose 的区别](#一dockerfile-与-docker-compose-的区别)
  - [1.1 对比总表](#11-对比总表)
  - [1.2 Dockerfile：镜像的构建配方](#12-dockerfile镜像的构建配方)
  - [1.3 Docker Compose：运行环境的编排蓝图](#13-docker-compose运行环境的编排蓝图)
  - [1.4 两者的关系：互补而非替代](#14-两者的关系互补而非替代)
  - [1.5 什么时候需要哪个](#15-什么时候需要哪个)
- [二、Compose 的 build 以 Dockerfile 为基础](#二compose-的-build-以-dockerfile-为基础)
  - [2.1 最简写法与完整写法](#21-最简写法与完整写法)
  - [2.2 build 的常用子字段](#22-build-的常用子字段)
  - [2.3 与多阶段构建的配合](#23-与多阶段构建的配合实战重点)
  - [2.4 build 与 image 的关系](#24-build-与-image-的关系)
  - [2.5 Compose build 与 docker build 的对应关系](#25-compose-的-build-与-docker-build-的对应关系)
- [三、总结](#三总结)

---

## 一、Dockerfile 与 Docker Compose 的区别

### 1.1 对比总表

| 维度 | Dockerfile | Docker Compose (compose.yaml) |
|------|-----------|-------------------------------|
| **解决什么问题** | **一个镜像怎么造** | **一组容器怎么跑、怎么连** |
| **作用对象** | 单个镜像（单容器） | 多个服务（多容器编排） |
| **关注点** | 分层、构建步骤、依赖安装、启动命令 | 服务关系、网络、端口、卷、环境变量、启动顺序 |
| **执行阶段** | **构建时**（`docker build`） | **运行时**（`docker compose up`） |
| **能否表达多服务** | ❌ 不能，一个 Dockerfile 只产出一个镜像 | ✅ 能，天然支持多服务 |
| **能否定义网络/卷/依赖顺序** | ❌ 不能 | ✅ 能 |
| **典型命令** | `docker build -t app:1.0 .` | `docker compose up -d` |
| **是否必需** | 只有需要**自建镜像**时才写 | 只有需要**多容器编排**时才写 |

### 1.2 Dockerfile：镜像的构建配方

Dockerfile 回答的是：**"给我一个基础镜像，我要装什么、拷什么、跑什么命令，最终得到一个能用的镜像。"**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV TZ=Asia/Shanghai
CMD ["python", "main.py"]
```

它只关心**一个容器内部**的事。它**无法**表达"我的 app 要连一个 MySQL、一个 Redis，它们分别是什么镜像、怎么组网"——这些不是 Dockerfile 的职责。

### 1.3 Docker Compose：运行环境的编排蓝图

Compose 回答的是：**"我要同时跑哪几个服务，每个服务用什么镜像/怎么构建、端口怎么映射、数据存哪、谁依赖谁、在哪个网络里。"**

```yaml
services:
  app:
    build: .                 # ← 这里引用 Dockerfile 来构建
    ports:
      - "80:3000"
    environment:
      - TZ=Asia/Shanghai
      - DB_HOST=db
    depends_on:
      db:
        condition: service_healthy

  db:
    image: mysql:8.0         # ← 直接用现成镜像，不需要 Dockerfile
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]

volumes:
  db_data:
```

注意：`app` 用 `build` 自建镜像，`db` 用 `image` 直接用官方镜像。**Compose 可以完全不用 Dockerfile（全用现成镜像），Dockerfile 也完全不需要 Compose（手工 `docker build` + `docker run`）。**

### 1.4 两者的关系：互补而非替代

```
┌─────────────────────────────────────────────┐
│  Dockerfile  →  构建出镜像  →  app:1.0        │  ← 构建层
└─────────────────────────────────────────────┘
                    ↓ 被引用
┌─────────────────────────────────────────────┐
│  Compose  →  用镜像 + 现成镜像  →  拉起多容器  │  ← 编排层
└─────────────────────────────────────────────┘
```

- **Dockerfile 管"造"**：镜像怎么来。
- **Compose 管"跑"**：镜像造好后，多个容器怎么组队运行。
- Compose 的 `build` 字段本质就是**在编排层调用构建层**——它内部就是执行 `docker build`。

### 1.5 什么时候需要哪个

| 场景 | 要不要 Dockerfile | 要不要 Compose |
|------|------------------|----------------|
| 只跑一个官方镜像（如 nginx） | ❌ | 可选（单服务用 `docker run` 也行） |
| 自建镜像 + 单容器 | ✅ | 可选 |
| 自建镜像 + 多服务（app + db + redis） | ✅ | ✅ **推荐** |
| 纯编排现成镜像（db + redis + nginx） | ❌ | ✅ |

---

## 二、Compose 的 build 以 Dockerfile 为基础

**Compose 的 `build` 字段就是 `docker build` 命令的声明式封装**——它告诉 Compose："这个服务不要拉现成镜像，去指定目录用 Dockerfile 构建一个。"

### 2.1 最简写法与完整写法

**最简：**

```yaml
services:
  app:
    build: .          # 等价于 docker build .
```

`build: .` 是简写，`.` 表示**构建上下文（context）**，Compose 会在该目录下找名为 `Dockerfile` 的文件。

**完整：**

```yaml
services:
  app:
    build:
      context: .              # 构建上下文目录
      dockerfile: Dockerfile  # Dockerfile 文件名（默认就是 Dockerfile）
```

### 2.2 build 的常用子字段

| 字段 | 对应 `docker build` 参数 | 说明 |
|------|------------------------|------|
| `context` | `docker build <路径>` | 构建上下文，**决定 COPY 能访问哪些文件** |
| `dockerfile` | `-f` | 指定 Dockerfile 文件名，默认 `Dockerfile` |
| `target` | `--target` | **多阶段构建**时指定构建到哪个阶段 |
| `args` | `--build-arg` | 构建参数，可在 Dockerfile 中用 `ARG` 接收 |
| `cache_from` | `--cache-from` | 指定缓存来源镜像，加速 CI 构建 |
| `labels` | `--label` | 给镜像打标签 |
| `network` | `--network` | 构建时使用的网络（如构建时要访问内网源） |
| `shm_size` | `--shm-size` | 共享内存大小 |

**完整示例：**

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
      target: production            # 多阶段构建只取 production 阶段
      args:
        NODE_ENV: production
        BUILD_VERSION: "1.0.0"
      cache_from:
        - app:latest
    image: app:1.0                  # 构建完给镜像命名，便于复用/推送
```

### 2.3 与多阶段构建的配合（实战重点）

Dockerfile 里用多阶段构建分离"开发/生产"：

```dockerfile
# 阶段 1：开发依赖
FROM node:20 AS development
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]

# 阶段 2：构建产物
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 阶段 3：生产运行（只留产物，体积最小）
FROM node:20-slim AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --omit=dev
CMD ["node", "dist/main.js"]
```

Compose 里用 `target` 选阶段，**同一份 Dockerfile 支撑开发和生产**：

```yaml
# compose.override.yaml（开发）
services:
  app:
    build:
      context: .
      target: development        # 取开发阶段

# compose.prod.yaml（生产）
services:
  app:
    build:
      context: .
      target: production         # 只取生产阶段，镜像最小
    image: app:1.0
```

这就是"**Dockerfile 写构建逻辑，Compose 选构建目标**"的典型协作方式。

### 2.4 build 与 image 的关系

两者可以**同时出现**，含义是"构建后命名为该镜像"：

```yaml
services:
  app:
    build: .
    image: app:1.0        # 构建结果命名为 app:1.0
```

| 写法 | 含义 |
|------|------|
| 只写 `build` | Compose 构建出一个匿名镜像（名字形如 `项目名-服务名`） |
| 只写 `image` | 直接拉取该镜像，**不构建** |
| 两个都写 | **构建并命名为 `image` 指定的名字**，便于 `docker push` 或跨环境复用 |

> 💡 **常见误区**：以为写了 `build` 就一定每次重新构建。其实 `docker compose up` 只在镜像不存在或 Dockerfile/上下文变化时才构建，也可用 `docker compose up --build` 强制重建。

### 2.5 Compose 的 build 与 docker build 的对应关系

| Compose 配置 | 等价命令 |
|-------------|---------|
| `build: .` | `docker build .` |
| `build: { context: ./app }` | `docker build ./app` |
| `build: { context: ., dockerfile: Dockerfile.prod }` | `docker build -f Dockerfile.prod .` |
| `build: { context: ., target: production }` | `docker build --target production .` |
| `build: { context: ., args: { NODE_ENV: prod } }` | `docker build --build-arg NODE_ENV=prod .` |
| `build: .` + `image: app:1.0` | `docker build -t app:1.0 .` |

---

## 三、总结

1. **Dockerfile 是构建层，Compose 是编排层**，二者职责不同、层次不同，**不是替代关系而是配合关系**。Dockerfile 说"一个镜像怎么造"，Compose 说"一组容器怎么跑"。

2. **Compose 的 `build` 就是以 Dockerfile 为基础**——它是对 `docker build` 的声明式封装：
   - `context` 指定构建上下文
   - `dockerfile` 指定文件名
   - `target` 选多阶段阶段
   - `args` 传构建参数
   - 一一对应，本质就是"在编排层调用构建层"。

3. **实战中的标准组合**：
   - `Dockerfile` 写多阶段构建逻辑
   - `compose.yaml` 用 `build.target` 区分开发/生产
   - `image` 给构建结果命名
   - 覆盖文件按环境叠加

   这样一份 Dockerfile 既能开发热更新，又能产出最小生产镜像。

4. **什么时候不需要 Dockerfile**：纯用官方/现成镜像编排（如 db + redis + nginx）时，Compose 直接写 `image` 即可。

5. **什么时候不需要 Compose**：只构建、只跑单个容器时，`docker build` + `docker run` 足够。

---

## 附：核心记忆口诀

> **Dockerfile 造镜像，Compose 组容器；**
> **build 字段调 Dockerfile，target 选阶段、args 传参数；**
> **单容器用 run，多服务用 Compose，两者配合是标准姿势。**