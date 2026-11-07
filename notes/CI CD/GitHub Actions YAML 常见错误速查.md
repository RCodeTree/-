# GitHub Actions YAML 常见错误速查

> 来源：Hello Note CI（前后端双 job）练习评审时踩到的坑，提炼成通用规则。
> 关联：[《CI CD 入门与 GitHub Actions 实战总结》](<./CI CD 入门与 GitHub Actions 实战总结.md>) ｜ [《GitHub Actions permissions 说明》](<./GitHub Actions permissions 说明.md>)

---

## 零、先记死 job 的正确结构

```yaml
jobs:
  <job_id>:            # job 名（自己起，如 build / test / deploy）
    runs-on: ...       # 直接就是 job 的配置键
    permissions: ...   # 可选
    steps:             # 工序列表
      - name: ...
        uses: ...      # 或 run: ...
```

> **`jobs.<job_id>` 下面直接就是配置键**（`runs-on` / `steps` / `permissions` / `needs` / `env` …），
> **不能再嵌套一层 `build:` 之类的"阶段名"**。`job_id` 本身就是 job 的名字。

---

## 一、硬伤：push 上去直接 `Invalid workflow file`

| # | 错误 | 现象 / 报错 | 改法 |
|---|---|---|---|
| 1 | `jobs.<id>` 下多套一层 `build:` | `Unexpected value 'build'`，且 job 缺必填 `runs-on` | 删掉 `build:`，配置键提级 |
| 2 | `permissons` 拼错 | 未知键，权限不生效 | `permissions` |
| 3 | `package: write`（单数） | scope 不存在 | `packages: write`（复数） |
| 4 | 一个 step 写两个 `run:` | YAML 重复键，只执行一个或直接报错 | 合并成一个多行 `run: \|` |

### 1. 层级错误（最高频）

```yaml
# ❌ 错误：多套了一层 build
jobs:
  myjob:
    build:
      runs-on: ubuntu-latest
    steps: ...

# ✅ 正确
jobs:
  myjob:
    runs-on: ubuntu-latest
    steps: ...
```

### 2 / 3. 拼写与单复数

```yaml
# ❌ permissons（多打 s）
# ❌ package: write（scope 名是复数）
permissions:
  contents: read
  packages: write   # ✅ 正确写法
```

### 4. 一个 step 只有一个 `run`

```yaml
# ❌ 重复键
- name: 装依赖
  run: npm i -g pnpm
  run: pnpm i

# ✅ 合并成多行（| 表示块级字符串，按行执行）
- name: 装依赖
  run: |
    npm i -g pnpm
    pnpm i
```

---

## 二、隐患：能跑但埋雷

### 5. `python-version` 的引号陷阱（float）

```yaml
# ❌ 3.14 不加引号 → YAML 解析成浮点数 3.14，action 拿到的是数字不是字符串
python-version: 3.14

# ✅ 含小数点的版本号一律加引号
python-version: "3.14"
```

> 对比 `node-version: 20`——`20` 是整数、没有小数点，不加引号也安全。
> **稳妥做法：所有版本号统一加引号**，不纠结"这个有没有小数点"。

### 6. 版本不显式 = 不可复现

```yaml
# ❌ 不写 python-version → 用平台默认版本，随时间漂移，今天能跑、半年后可能崩
- uses: actions/setup-python@v5

# ✅ 显式指定，且与 Dockerfile 的 FROM python:3.14-slim 保持一致
- uses: actions/setup-python@v5
  with:
    python-version: "3.14"
```

### 7. 半成品骨架：CI 三环缺了两环

```text
CI 三环：
  ① 装环境  checkout → setup-python/node → install
  ② 验证    跑测试（pytest）/ 构建（pnpm build）
  ③ 产物    docker build → docker push 镜像
```

只搭了 ① 的流水线不是 CI，只是"自动装了个环境"。三环齐全才算闭环。

---

## 三、最小权限提醒

- `packages: write` 是给「推 GHCR 镜像」准备的——流水线里还没有 push 步骤时，这个权限**其实用不上**。
- 原则是**按需提权**：需要哪一步再加哪个 scope（完整 scope 清单见 permissions 专文）。

---

## 四、正确骨架模板（前后端双 job）

```yaml
name: CI

on:
  push:
    branches: ["main"]

jobs:
  backend:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest

  frontend:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: |
          npm i -g pnpm
          pnpm i
      - run: pnpm build
```

> 两个 job 无依赖时默认**并行**；若前端产物要给后端用，才用 `needs:` 串行。

---

## 五、做对的点（保留这些习惯）

| 做对 | 价值 |
|---|---|
| `name / on / jobs / steps` 骨架层级 | 整体结构意识 |
| 前后端拆成独立 job | 不同技术栈隔离，默认并行 |
| 用官方 action（`checkout` / `setup-python` / `setup-node`） | 不重复造轮子 |
| `permissions: contents: read` 最小权限意识 | 安全意识已就位 |

---

## 六、一句话总结

> **层级、拼写、重复键的错（多套 `build`、`permissons`、双 `run`）会让流水线当场报错；**
> **版本、显式声明的错（`3.14` 没引号、不写 `python-version`）会让它"今天能跑、以后崩"。**
> 前一类靠「记死 job 结构」避免，后一类靠「一切显式声明」避免。
