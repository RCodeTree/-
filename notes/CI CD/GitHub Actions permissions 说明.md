下面是一份可直接保存为 `github-actions-permissions.md` 的文档：

---

# GitHub Actions `permissions` 说明

## 一、作用

`permissions` 用于控制 workflow 运行时自动生成的 `GITHUB_TOKEN` 的权限范围。

- 该令牌供 workflow 调用 GitHub API（创建 Release、评论 PR、推送镜像到 GHCR、读取代码等）。
- `permissions` 决定该令牌在每个 scope 上是 `read` / `write` / `none`。
- 不影响自定义 PAT、SSH Key、云厂商凭证的权限。

**核心价值：最小权限原则，按需提权，降低供应链攻击面。**

## 二、基本语法

```yaml
# workflow 级别：影响所有 job
permissions:
  contents: read
  pull-requests: write

jobs:
  build:
    runs-on: ubuntu-latest
    # job 级别：覆盖 workflow 级别（整体替换，不是合并）
    permissions:
      contents: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
```

简写形式：

```yaml
permissions: read-all    # 所有 scope 只读
permissions: write-all   # 所有 scope 可写（不推荐）
permissions: {}          # 全部设为 none（最严格）
```

## 三、常用权限 scope

| scope | 常见用途 |
|---|---|
| `contents` | 读代码、创建 Release、打 tag、提交 |
| `pull-requests` | 评论、打标签、合并 PR |
| `issues` | 创建/评论 issue |
| `packages` | 推送/拉取 GHCR 镜像 |
| `id-token` | OIDC 无密码登录 AWS/GCP/Azure/Vault |
| `security-events` | 上传 SARIF、CodeQL 结果 |
| `actions` | 管理 workflow run、artifact、cache |
| `checks` | 创建 check run |
| `deployments` | 创建 deployment status |
| `pages` | 部署 GitHub Pages |
| `statuses` | 提交 commit status |
| `attestations` | 生成构建来源证明（provenance） |
| `models` | 访问 GitHub Models |

## 四、为什么重要

1. **最小权限原则**：避免默认 `write-all` 被恶意脚本或恶意 PR 利用。
2. **符合 SLSA / 供应链安全审计要求**：CI 令牌权限显式可查。
3. **防止误操作**：只读 job 中误写 `git push` 会直接失败。

## 五、典型配置示例

### 1. 发布 Release

```yaml
permissions:
  contents: write   # 创建 release / tag 必需
```

### 2. PR 自动评论 / 打标签

```yaml
permissions:
  contents: read
  pull-requests: write
```

### 3. 推送镜像到 GHCR

```yaml
permissions:
  contents: read
  packages: write
```

### 4. OIDC 登录云厂商（推荐替代长期 AK）

```yaml
permissions:
  id-token: write   # 申请 OIDC token
  contents: read
```

### 5. 推荐骨架：默认只读，按需提权

```yaml
permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test

  release:
    needs: test
    permissions:
      contents: write   # 仅此 job 提权
    steps:
      - uses: actions/checkout@v4
      - run: gh release create ...
```

## 六、常见坑

1. **job 级别覆盖而非合并 workflow 级别**：需写全该 job 所需 scope，否则 checkout 可能失败。
2. **fork PR 中的 token 天然只读**：即使声明 `write` 也不生效（`pull_request_target` 除外）。
3. **`pull_request_target` + checkout PR 代码**：典型供应链攻击入口，务必谨慎。
4. **不要使用 `write-all`**：放弃最小权限，审计不通过。
5. **`permissions: {}` 是全部禁用**：部分 action 内部隐式调用 API 会失败。
6. **OIDC 必须显式声明 `id-token: write`**：否则报错 `Unable to get ACTIONS_ID_TOKEN_REQUEST_URL`。

## 七、一句话总结

`permissions` 为 CI 自动生成的 `GITHUB_TOKEN` 设置最小权限白名单，通过 job 级覆盖实现“默认只读、按需提权”，是 GitHub Actions 安全实践的第一道防线。

---

需要我把它补充成带目录的版本，或者加上 `pull_request` 与 `pull_request_target` 的安全对比章节吗？