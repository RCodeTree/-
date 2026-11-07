# CI/CD 入门与 GitHub Actions 实战总结

> 阶段定位：一年推进计划 **C 阶段 W15–16（Docker + CI/CD）**
> 前接 W6 Docker 容器化，后接 D 阶段 Kubernetes
> 关联专文：同目录 [《GitHub Actions permissions 说明》](<./GitHub Actions permissions 说明.md>)

---

## 一、路线定位：为什么 Docker 之后是 CI/CD，而不是 K8s

```
C 阶段：Docker + CI/CD（W11–16）
   W11–13  Dockerfile / 网络存储 / Compose   ← 已完成
   W14      排障 / 资源限制 / 镜像瘦身        ← 已完成
   W15      CI：测试 + 构建 + 推镜像          ← 本阶段
   W16      CD：自动部署 + 回滚 + Secret
D 阶段：Kubernetes（W17 起）
```

**一句话理由：CI 是「产线」，K8s 是「交付目的地」。**

先把「代码 → 测试 → 构建镜像 → 推送 Registry」这条产线打通（CI），后面 K8s 只负责「把镜像跑起来」——届时 CD 只需更换部署目标，产线无需推倒重来。

且 CI/CD 会立刻复用 Docker 阶段的知识：Dockerfile、多阶段构建、分层缓存、Registry 概念，全部原样登场。

---

## 二、技术选型（本项目）

| 项 | 选择 | 理由 |
|---|---|---|
| 代码托管 | GitHub | 路线图首选，Actions 免费额度友好 |
| CI 引擎 | GitHub Actions | 与仓库零距离，`ubuntu-latest` 自带 Docker，无需自建环境 |
| 镜像仓库 | GHCR（`ghcr.io`） | 与 GitHub 账号绑定，免额外注册 Docker Hub |

> **关键认知**：CI 流水线跑在 GitHub 的托管机器上，**不需要本地 Debian 虚拟机一直开机**。这是 CI 与「本地手动 build」最本质的区别。

---

## 三、CI/CD 在解决什么问题（世界观）

手动模式：

```text
改代码 → 手动 docker build → 手动起容器 → 手动看结果
```

每一步都靠人：容易漏、不可复现、无法审计。

CI 模式：

```text
git push 到 GitHub
      ↓ 自动触发
【一台干净的 GitHub 机器】拉代码 → 装依赖 → 跑测试 → docker build → push Registry
      ↓
只看流水线的 ✅ / ❌
```

**一句话：把「构建/测试」从「人做的动作」变成「代码提交自动触发、可重复、可审计」的流水线。**
对运维的意义：任何一次变更都有机器兜底验证，全程留痕，天然可回滚。

---

## 四、GitHub Actions 的 5 个核心概念

| 概念 | 是什么 | 类比 |
|---|---|---|
| **Workflow** | 一个 `.yml` 文件 = 一条流水线 | 总调度计划 |
| **Trigger** (`on:`) | 什么时候触发 | 触发条件（push / PR / 手动） |
| **Job** | 流水线里的独立执行单元 | 一个车间（多 job 默认并行） |
| **Step** | Job 里的最小执行单元 | 车间里的一道工序 |
| **Runner** | 真正执行命令的机器 | 工人（GitHub 托管 `ubuntu-latest`） |

层级关系：

```text
workflow (ci.yml)
   └─ trigger: on push
        └─ job: build
             ├─ step 1: checkout 代码
             ├─ step 2: 装 Python
             ├─ step 3: 装依赖
             ├─ step 4: 跑测试
             ├─ step 5: 登录 GHCR
             ├─ step 6: docker build
             └─ step 7: docker push
```

---

## 五、核心心智模型：runner 是一台「全新、无记忆」的干净机器

> 它不知道你本地装过什么 Python、装过什么依赖、有没有登录过 docker。
> **本地靠「环境记忆」，CI 靠「流水线声明」**——每一步都要显式写进 yaml。

这也是新手最常见的翻车点：本地能跑，CI 一跑就报 `command not found` / `No module named ...`，根因几乎都是「忘了在流水线里声明这一步」。

---

## 六、测试：CI 的灵魂

**没有测试的 CI 只是「自动 build」，不算「持续集成」。** 测试把「靠肉眼看日志验证」升级为「靠断言机器化验证」。

### 6.1 依赖必须分离

```
requirements.txt      → aiohttp, requests   （运行时需要，进镜像）
requirements-dev.txt  → pytest              （只测试需要，不进镜像）
```

CI 的测试阶段装 dev 依赖，构建镜像只装 runtime 依赖。否则生产镜像里会白带一个 pytest（镜像变胖、攻击面变大）。

### 6.2 测试设计（贴着 `prob_tcp` 的三个分支写）

| 测试 | 场景 | 断言 | 对应验收标准 |
|---|---|---|---|
| `test_prob_tcp_alive` | 本地起临时 TCP 服务，端口可达 | `alive=True`，host/port 一致 | 并发探活正确 |
| `test_prob_tcp_refused` | 端口无服务 | `alive=False` + 有 `error`，不抛异常 | 故障隔离 |
| `test_prob_tcp_timeout` | 地址不可达（`192.0.2.1`，TEST-NET-1） | `alive=False` + `TimeoutError`/`OSError` | 故障隔离 + 超时兜底 |

两个刻意的设计决策：

- **用 `asyncio.run()` 包装异步场景，而非引入 `pytest-asyncio` 插件** → 少一个依赖、少一个踩坑点，标准库够用。
- **`pyproject.toml` 里配 `pythonpath = ["."]`** → 让 `tests/` 能 `import probe`（否则 CI 里报模块找不到）。
- 不可达地址在不同网络环境下可能表现为 `TimeoutError` 或 `OSError`，断言兼容两者，避免 flaky。

> **当前状态：测试文件已产出，尚未实跑**（约定后续真正测试时再验证）。预期目标 `3 passed`。

---

## 七、完整 `ci.yml` 与逐段拆解

```yaml
name: CI

on:
  push:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 安装 Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.14"

      - name: 安装依赖
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: 运行测试
        run: pytest

      - name: 登录 GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: 构建镜像
        run: docker build -t ghcr.io/${{ github.repository }}:${{ github.sha }} .

      - name: 推送镜像
        run: docker push ghcr.io/${{ github.repository }}:${{ github.sha }}
```

### 7.1 `on:` —— 触发开关

只有 `main` 分支 push 才触发，feature 分支不触发（省额度、避免无效构建）。
**PR 合入本质上就是「push 到 main」**，所以这一行已覆盖「PR 合入 → 自动构建」的里程碑；若想「合入前先验证」，再补 `pull_request:` 触发即可。

### 7.2 `permissions:` —— GHCR 推送的总闸

`packages: write` 不写，`docker build` 会成功但 `push` 必 403。
完整语法、scope 清单、job 级覆盖、最小权限原则 → 见专文 [《GitHub Actions permissions 说明》](<./GitHub Actions permissions 说明.md>)。

### 7.3 `uses:` vs `run:`

| 写法 | 含义 |
|---|---|
| `uses: actions/checkout@v4` | 调用别人封装好的**预制步骤（Action）**，`@v4` 是版本号 |
| `run: pip install ...` | 自己直接敲 shell 命令 |

`checkout` / `setup-python` / `login-action` 都是官方 Action，一行替代一堆脚本。

### 7.4 `${{ }}` —— 运行时才求值的上下文变量

| 变量 | 值 | 用途 |
|---|---|---|
| `github.repository` | `用户名/仓库名` | 拼镜像名 `ghcr.io/rong/probe` |
| `github.sha` | 本次 commit 的 40 位 SHA | 作为镜像 tag |
| `github.actor` | 触发者登录名 | GHCR 登录用户名 |
| `secrets.GITHUB_TOKEN` | GitHub 自动签发的**临时**令牌 | 登录密码 |

> `${{ secrets.GITHUB_TOKEN }}` 是平台自动注入、单次运行即失效的临时令牌，属于安全实践；
> **绝不要把 PAT、云厂商 AccessKey、kubeconfig、私钥、明文密码写进 yaml 或提交进仓库**，一律走 Repository Secrets 或 OIDC。

### 7.5 为什么 tag 用 `${{ github.sha }}` 而不是 `latest`

| tag | 问题 |
|---|---|
| `latest` | 每次构建被覆盖，**不可追溯**，出故障不知道「上一版」是哪个 commit |
| commit SHA | 镜像 ↔ 代码版本**一一对应** |

SHA tag 是 W16「CD 回滚」的地基：回滚 = 重新部署上一个 SHA 的镜像。

---

## 八、流水线运行时画面

```text
push main
   ↓ 触发
runner (ubuntu-latest) 启动
   ├─ checkout@v4        拉代码
   ├─ setup-python@v5    装 Python 3.14
   ├─ pip install        装 aiohttp/requests + pytest   ← dev 依赖在此
   ├─ pytest             跑 3 个测试
   ├─ login-action       登录 ghcr.io
   ├─ docker build       复用 Dockerfile 构建
   └─ docker push        推 ghcr.io/<owner>/<repo>:<sha>
```

---

## 九、上线前置条件清单（真正跑时逐条核对）

1. probe 项目初始化为 git 仓库：`git init` + 首次提交；
2. GitHub 建同名仓库并 `git push`（`.github/workflows/ci.yml` 随代码一起推上去）；
3. **仓库 Settings → Actions → General → Workflow permissions → 选 `Read and write permissions`**
   （否则仓库级只读设置会压过 workflow 里的 `packages: write`，push 仍 403）；
4. 确认 GHCR 包可见性 / 关联仓库权限（首次推送后检查 Packages 页）。

---

## 十、本阶段产物清单（项目内相对路径）

> probe 项目已单独迁出本工作区，以下均为**项目内相对路径**，不依赖工作区位置。

```
probe/
├── .github/workflows/ci.yml   ← 流水线（W15）
├── tests/test_probe.py        ← 3 个单元测试
├── requirements-dev.txt       ← 测试依赖（不进运行时镜像）
├── pyproject.toml             ← pytest 配置（pythonpath / testpaths）
├── Dockerfile                 ← 构建用（复用 W6 成果）
├── requirements.txt           ← 运行时依赖
└── ...
```

---

## 十一、常见坑速查

| # | 现象 | 根因 | 预防 |
|---|---|---|---|
| 1 | 本地能跑，CI 报 `No module named` / `command not found` | runner 无记忆，没显式声明装 Python/依赖 | 每一步写进 steps |
| 2 | build 成功、push 报 403 | 漏 `permissions: packages: write` | 显式声明（见专文） |
| 3 | 声明了 `packages: write` 仍 403 | 仓库级 Workflow permissions 默认只读 | Settings 改 Read and write |
| 4 | 出故障无法定位「上一版镜像」 | 用了 `latest` tag | 用 `${{ github.sha }}` |
| 5 | 生产镜像莫名变胖 / 多了测试库 | dev 依赖打进了镜像 | `requirements` 与 `requirements-dev` 分离 |
| 6 | 凭证泄露风险 | PAT / AK 明文写进 yaml | Secrets / OIDC，最小权限 |
| 7 | fork 来的 PR 写操作失败 | fork PR 的 token 天然只读 | 见专文「常见坑」章节 |

---

## 十二、一句话总结

**CI 就是把「构建与验证」从人的动作变成代码提交自动触发、可重复、可审计的流水线**；GitHub Actions 用 `workflow → job → step` 三级结构描述它，`${{ }}` 注入上下文，`permissions` 守住最小权限，用 commit SHA 做镜像 tag 为后续 CD 回滚留下可追溯的锚点。

---

## 附：待办状态

- [x] 概念体系、技术选型、ci.yml 编写
- [x] 单元测试文件产出
- [ ] 本地 `pytest` 实跑并确认 `3 passed`
- [ ] git init → 建 GitHub 仓库 → push → 观察首条流水线绿/红
- [ ] W16：CD 自动部署 + 回滚 + Secret
