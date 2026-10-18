# Python Logging 完整笔记

> 涵盖：Logger 层级、有效级别、三条最佳实践、控制台 + 文件双输出、文件轮转、异常记录、dictConfig、常见坑与速查。一份笔记覆盖日常全部场景。

---

## 目录

1. [核心模型：Logger 层级树](#一核心模型logger-层级树)
2. [有效级别：一条日志"出不出得来"](#二有效级别一条日志出不出得来)
3. [三条最佳实践](#三三条最佳实践)
4. [常见误区：模块里写 `logging.info`](#四常见误区模块里写-logginginfo)
5. [惰性格式化](#五惰性格式化)
6. [异常记录](#六异常记录)
7. [控制台 + 文件双输出](#七控制台--文件双输出)
8. [文件轮转](#八文件轮转)
9. [进阶：dictConfig](#九进阶dictconfig)
10. [必须避开的坑](#十必须避开的坑)
11. [完整可运行 Demo（双输出版）](#十一完整可运行-demo双输出版)
12. [速查表](#十二速查表)

---

## 一、核心模型：Logger 层级树

`logging.getLogger(name)` 用**点分名称**构造一棵树，`__name__` 天然就是模块的完整路径。

```
root
└── mypkg                    ← getLogger("mypkg")
    ├── mypkg.db             ← getLogger("mypkg.db")
    └── mypkg.service        ← getLogger("mypkg.service")
```

**为什么必须用 `__name__`？**

| 写法 | `%(name)s` 显示 | 问题 |
|---|---|---|
| `getLogger(__name__)` | `mypkg.db` | ✅ 可分层控制 |
| `getLogger("db")` | `db` | ❌ 与 `mypkg` 无父子关系，无法按包控制 |
| `logging.info(...)` | `root` | ❌ 丢失模块信息，无法分层 |

分层带来的好处——**一行控制整个库**：

```python
logging.getLogger("mypkg").setLevel(logging.WARNING)  # mypkg 下所有子模块 INFO 全压掉
```

---

## 二、有效级别：一条日志"出不出得来"

### 判定链路

```
① logger 的有效级别  ──┐
                       ├──► 两者都要放行（取更严格者），才输出
② handler 的级别     ──┘
```

### 有效级别怎么算

logger 的 `level` 可能是 `NOTSET`（=0），含义是**"我不设，沿层级往上找"**：

```
mypkg.db (NOTSET) → mypkg (NOTSET) → root (DEBUG) → 有效级别 = DEBUG
```

只要中途某个父级显式设了 level，就用它。

### `basicConfig` 做了什么

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

1. 给**根 logger** 设 `level = DEBUG`；
2. 创建 `StreamHandler`（其 level 默认 `NOTSET`，全放行）；
3. 设 format、输出流。

> ⚠️ `basicConfig` **默认只生效一次**。根 logger 已有 handler 时，再调会**静默失败**（除非 `force=True`）。这就是库不能乱调它的原因。

### 关键结论

| 问题 | 结论 |
|---|---|
| 调用 `logging.info()` 会改级别吗？ | **不会**。级别只由 `basicConfig` / `setLevel` 决定 |
| `basicConfig(level=DEBUG)` 下 `logging.debug()` 出得来吗？ | **会**，门槛是 DEBUG，全级别放行 |
| 根设成 `WARNING` 后 `logging.debug()` 出得来吗？ | **不会**，门槛拦住就出不来 |

**"调用的方法名"决定事件级别，"配置的 level"决定门槛，二者完全独立。**

---

## 三、三条最佳实践

### ✅ 实践 1：每个模块用 `getLogger(__name__)`

```python
# mypkg/db.py
import logging
logger = logging.getLogger(__name__)   # → "mypkg.db"
```

- 日志里 `%(name)s` 自动显示模块路径，**一眼定位哪行代码打的**；
- 保留层级，可按包/子模块精细调级别、加 handler。

### ✅ 实践 2：库代码不调 `basicConfig`，只发日志

**库的职责**：报告"发生了什么"。  
**应用的职责**：决定"怎么记"（level、format、输出到哪）。

**反例（库擅自配置）：**

```python
# mypkg/db.py —— 错误示范
import logging
logging.basicConfig(level=logging.INFO)   # ❌ 占用了"唯一一次配置"机会
logger = logging.getLogger(__name__)
```

后果——应用的配置被吞：

```python
# main.py
logging.basicConfig(filename="app.log", level=logging.DEBUG)  # 静默失效！
```

库应做到：**只 get logger、只调 `logger.xxx()`，不 `basicConfig`、不自 `addHandler`、不 `setLevel`。**

### ✅ 实践 3：异常堆栈用 `logger.exception(...)`，且必须在 `except` 块内

详见[第六节](#六异常记录)。

---

## 四、常见误区：模块里写 `logging.info`

```python
# mypkg/db.py
logging.info("hi")     # 等价于 logging.getLogger().info("hi")
```

**两个问题：**

| 现象 | 说明 |
|---|---|
| `%(name)s` 显示 `root` | 用的是**根 logger**，丢失模块信息 |
| 无法分层控制 | `getLogger("mypkg").setLevel(...)` 对它无效 |

**它影响级别吗？不会。** 级别是配置属性，调 `logging.info` 只是给**这一条事件**打 INFO 标签。

**它能出来吗？能**——取决于根 level 放不放行，与写法无关。

**验证代码：**

```python
import logging, sys
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    datefmt="%H:%M:%S", stream=sys.stdout)

logger = logging.getLogger("mypkg.db")
print("根级别:", logging.getLogger().level)   # 10
print("子级别:", logger.level)               # 0 (NOTSET，靠继承)

logging.info("根 logger 发 info")     # ✅ 名字 root
logger.info("模块 logger 发 info")    # ✅ 名字 mypkg.db

logging.getLogger().setLevel(logging.WARNING)   # 现在才真改级别
logging.info("这句不出了")              # ❌ 被 WARNING 拦住
logger.warning("这句出")                # ✅ 继承 WARNING
```

---

## 五、惰性格式化

**用 `%s` 占位符，别用 f-string：**

```python
logger.debug("SQL: %s", sql)     # ✅ 只有级别放行才拼字符串
logger.debug(f"SQL: {sql}")      # ❌ 即使 DEBUG 关着也会先算 f-string
```

高频率日志 + 昂贵参数时差距明显。logger 内部把 `%` 运算延迟到真正要输出时。

---

## 六、异常记录

### 核心规则

| 场景 | 写法 |
|---|---|
| `except` 块内记录 | `logger.exception("msg")` |
| 想用非 ERROR 级别 | `logger.xxx("msg", exc_info=True)` |
| 无活跃异常、有异常对象 | `logger.error("msg", exc_info=exc)` |
| 不要这样做 | `logger.error(str(e))`（丢堆栈）、`except` 外调 `exception` |

### 为什么必须在 `except` 内？

`logger.exception` 依赖"当前线程正在处理的异常"（`sys.exc_info()`）。出块后异常信息是空的：

```python
try:
    risky()
except Exception:
    pass

logger.exception("这行在外面")   # ❌ 输出: NoneType: None
```

### 三种写法对比

```python
# ❌ 丢堆栈，只剩一句话
except Exception as e:
    logger.error(f"出事了: {e}")

# ✅ 最简洁
except Exception:
    logger.exception("出事了")

# ✅ 想用别的级别时
except Exception:
    logger.warning("出事了", exc_info=True)
```

### 记录后是否继续抛？

`exception()` 只记录，不改变异常状态：

```python
except PermissionError:
    logger.exception("拦截")
    raise              # 记录后继续上抛（上层决定处理）
# 或
except PermissionError:
    logger.exception("拦截")
    # 不 raise，表示"已安全处理"
```

---

## 七、控制台 + 文件双输出

### ⚠️ 第一个大坑：`basicConfig` 的 `filename` 和 `stream` 互斥

```python
logging.basicConfig(
    filename="app.log",
    stream=sys.stdout,   # ❌ 完全没作用，不报错，但文件独占
)
```

`basicConfig` 内部是 `if filename: ... elif stream: ...`，**`filename` 优先，`stream` 被静默忽略**。

> **想"控制台 + 文件"双输出，必须手动加第二个 handler（或用 `dictConfig`）。**

### 方案 A：`basicConfig` 配控制台 + 手动加文件 handler（最常用）

```python
import logging
import os
import sys

LOG_FILE = "logs/app.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)   # 目录不存在会报错，先建

# ① 配置根 logger：控制台输出
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

# ② 手动加 FileHandler
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")   # ⚠️ 中文必须 utf-8
file_handler.setLevel(logging.INFO)                               # 文件只记 INFO 以上
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",                                  # 文件里用完整日期
))
logging.getLogger().addHandler(file_handler)                      # 挂到根 logger

# ---- 业务 ----
logger = logging.getLogger("mypkg.db")
logger.debug("这条只在控制台")       # DEBUG < INFO，被文件 handler 过滤
logger.info("这条控制台和文件都有")   # 两边都出
```

**效果：**

| 输出 | 门槛 | DEBUG | INFO | WARNING+ |
|---|---|---|---|---|
| 控制台（stream） | DEBUG | ✅ | ✅ | ✅ |
| 文件（file） | INFO | ❌ | ✅ | ✅ |

**两个 handler 各自有独立的 level 和 formatter**——这就是"控制台看细节、文件只留重要信息"的实现方式。

**关键点：**

1. **`encoding="utf-8"`**：`FileHandler` 默认用系统编码（Windows 上 GBK），中文会乱码或抛 `UnicodeEncodeError`。**必加。**
2. **目录先建**：`FileHandler` 不自动建父目录，路径不存在直接 `FileNotFoundError`。
3. **`addHandler` 加在根 logger 上**：子模块 logger `propagate=True`，日志冒泡到根，两个 handler 都处理。**不要在子模块里 `addHandler`**（会导致重复输出，见[第十节](#十必须避开的坑)）。
4. **`basicConfig` 只调一次**：重复调静默失效。交互环境反复执行时加 `force=True`。

### 方案 B：`dictConfig`（推荐，正规且可扩展）

复杂点（多 handler、按 logger 分配、轮转）用 `dictConfig` 一次定义清楚：

```python
import logging.config
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,        # ⚠️ 别设 True

    "formatters": {
        "console": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "file": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "console",
            "stream": "ext://sys.stdout",     # ext:// 从外部模块取对象
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "file",
            "filename": f"{LOG_DIR}/app.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },

    "loggers": {
        "mypkg": {"level": "WARNING"},        # 库整体压到 WARNING
    },

    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],      # 关键：两个 handler 都挂到根
    },
}

logging.config.dictConfig(LOGGING)
```

**方案 A vs B：**

| | 方案 A | 方案 B |
|---|---|---|
| 可读性 | 配置散在代码里 | 一处集中，像配置文件 |
| 轮转 | 自己 new handler | `class` 直接指定 |
| 多 logger 分 handler | 手动循环 | 声明式 |
| 从文件/YAML 加载 | 麻烦 | 直接吃 dict |

---

## 八、文件轮转

生产环境**一定要轮转**，否则 `app.log` 无限增长。两种常用：

### 1. 按大小轮转 `RotatingFileHandler`

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10 * 1024 * 1024,   # 单文件 10MB
    backupCount=5,               # 保留 app.log.1 ~ app.log.5
    encoding="utf-8",
)
```

写满 10MB 就改名 `app.log.1`，新的继续写 `app.log`，超过 5 个的旧文件删除。

### 2. 按时间轮转 `TimedRotatingFileHandler`

```python
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler(
    "logs/app.log",
    when="midnight",       # 每天 0 点切；"H"每小时 / "D"每天 / "W0"周一
    interval=1,
    backupCount=30,        # 保留 30 天
    encoding="utf-8",
)
```

适合"按天归档"：`when="midnight"` + `backupCount=30` = 留 30 天。

> ⚠️ **多进程写同一文件不安全**：切分时可能互相踩。多进程/多 worker（gunicorn、celery）要用 `QueueHandler` + `QueueListener` 集中写，或每进程独立文件。单进程不用管。

---

## 九、进阶：dictConfig

见[第七节方案 B](#方案-bdictconfig推荐正规且可扩展)。补充要点：

- `disable_existing_loggers: False` **必须写**，否则先 `getLogger` 再 `dictConfig` 的模块会静默丢日志。
- `ext://sys.stdout` 里的 `ext://` 表示"从外部模块取对象"，`sys.stdout` 会在配置时被 import 解析。
- `loggers` 里只设 `level`、不挂 handler，让它 `propagate` 到 root，避免重复输出。

**`dictConfig` 的最大价值**——按 `__name__` 分层精确控制：

```python
"loggers": {
    "mypkg":    {"level": "WARNING"},     # 库整体压到 WARNING
    "mypkg.db": {"level": "DEBUG"},       # 但 db 子模块单独开 DEBUG
},
```

只有点分名字的 logger 才能这样精确控制到子模块。

---

## 十、必须避开的坑

### 坑 1：重复输出（日志打两遍）

**原因**：给某个子 logger 加了 handler，同时它 `propagate=True`，日志既被自己的 handler 处理，又冒泡到根的 handler 再处理一次。

```python
# ❌ 重复输出
logger = logging.getLogger("mypkg.db")
logger.addHandler(file_handler)   # 自己加了一个
logger.info("hi")                 # 自己的 handler 输出一次 + 冒泡到 root 再输出一次
```

**正确做法**：**只在根 logger 挂 handler**，子 logger 一律 `propagate=True`（默认），让它冒泡。库代码更不该 `addHandler`。

如果确实要让某个 logger 独立输出、不冒泡：

```python
logger.addHandler(file_handler)
logger.propagate = False          # 阻断冒泡，避免重复
```

### 坑 2：库代码里 `addHandler` / 写死文件路径

库不知道使用者的日志目录、编码、轮转策略。**库只 `getLogger(__name__)` 然后打日志**，文件 handler 由应用层加。否则使用者想改输出位置都改不动。

### 坑 3：`basicConfig` 的 `filename` + `stream` 同时传

如[第七节](#七控制台--文件双输出)所述，`stream` 被静默忽略。**必须手动 `addHandler`**。

### 坑 4：`disable_existing_loggers: True`

`dictConfig` 默认（某些场景）会把配置前已创建的 logger 禁用。**显式写 `False`**，否则先 `getLogger` 再 `dictConfig` 的模块会静默丢日志。

### 坑 5：忘了 `encoding="utf-8"`

`FileHandler` 默认系统编码（Windows GBK），中文乱码或抛异常。**必加。**

### 坑 6：`basicConfig` 重复调用

第二次起静默失效。交互环境/热重载里反复执行时加 `force=True`：

```python
logging.basicConfig(..., force=True)
```

---

## 十一、完整可运行 Demo（双输出版）

### 项目结构

```
demo/
├── main.py                 # 应用入口：唯一配置 logging 的地方
└── mypkg/                  # 模拟第三方库（零配置）
    ├── __init__.py
    ├── db.py
    └── service.py
```

### `mypkg/db.py`

```python
import logging

logger = logging.getLogger(__name__)   # "mypkg.db"


def query(sql):
    logger.debug("执行 SQL: %s", sql)          # 惰性格式化
    if "DROP" in sql.upper():
        raise PermissionError(f"禁止 DROP 操作: {sql}")
    return ["alice", "bob"]
```

### `mypkg/service.py`

```python
import logging
from . import db

logger = logging.getLogger(__name__)   # "mypkg.service"


def get_users():
    logger.info("开始查询用户")
    rows = db.query("SELECT * FROM users")
    logger.info("查询到 %d 个用户", len(rows))
    return rows


def dangerous_op():
    logger.info("准备执行危险操作")
    try:
        db.query("DROP TABLE users")
    except PermissionError:
        logger.exception("危险操作被拦截")   # ✅ except 内，自动带堆栈
```

### `mypkg/__init__.py`

```python
import logging

logger = logging.getLogger(__name__)   # "mypkg"，子模块 logger 的父级


def init():
    logger.info("mypkg 初始化完成")
```

### `main.py`

```python
import logging
import logging.handlers
import os
import sys

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ① 控制台（DEBUG 起，短时间格式）
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

# ② 文件（INFO 起，完整日期，带轮转）
file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"),
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))
logging.getLogger().addHandler(file_handler)

# ③ 业务
from mypkg import service

if __name__ == "__main__":
    service.get_users()
    service.dangerous_op()
```

### 控制台输出

```
10:22:01 [INFO] mypkg.service: 开始查询用户
10:22:01 [DEBUG] mypkg.db: 执行 SQL: SELECT * FROM users
10:22:01 [INFO] mypkg.service: 查询到 2 个用户
10:22:01 [INFO] mypkg.service: 准备执行危险操作
10:22:01 [DEBUG] mypkg.db: 执行 SQL: DROP TABLE users
10:22:01 [ERROR] mypkg.service: 危险操作被拦截
Traceback (most recent call last):
  File "mypkg/db.py", line 9, in query
    raise PermissionError(f"禁止 DROP 操作: {sql}")
PermissionError: 禁止 DROP 操作: DROP TABLE users
```

### `logs/app.log` 内容

```
2026-10-18 10:22:01 [INFO] mypkg.service: 开始查询用户
2026-10-18 10:22:01 [INFO] mypkg.service: 查询到 2 个用户
2026-10-18 10:22:01 [INFO] mypkg.service: 准备执行危险操作
2026-10-18 10:22:01 [ERROR] mypkg.service: 危险操作被拦截
Traceback (most recent call last):
  File "mypkg/db.py", line 9, in query
    raise PermissionError(f"禁止 DROP 操作: {sql}")
PermissionError: 禁止 DROP 操作: DROP TABLE users
```

**观察点：**

- 文件里**没有那两行 DEBUG**（`mypkg.db` 的 SQL 日志），因为文件 handler 门槛是 INFO；
- 文件名 `mypkg.db` / `mypkg.service` 直接告诉你哪行代码打的；
- `logger.exception` 自动追加 Traceback，控制台和文件各带一份；
- **库代码 `mypkg/` 一个字没改**——这就是"库只报事、应用管输出"的收益：加文件输出对库完全透明。

---

## 十二、速查表

### 配置与写法

| 场景 | 做法 | 反例 |
|---|---|---|
| 拿 logger | `logging.getLogger(__name__)` | `getLogger("db")` / `logging.info` |
| 库模块 | 只调 `logger.xxx()` | `basicConfig` / `addHandler` / `setLevel` |
| 应用入口 | `basicConfig` 或 `dictConfig`，**只配一次** | 每个模块都配一遍 |
| 控制台 + 文件 | `basicConfig`（控制台）+ 手动 `addHandler`（文件） | `basicConfig(filename=..., stream=...)` |
| 重复配置根 logger | `basicConfig(..., force=True)` | 直接再调（静默失效） |
| 记录异常 | `logger.exception("msg")`（在 `except` 内） | `logger.error(str(e))` / `except` 外调 `exception` |
| 带参数 | `logger.info("x=%s", x)` | `logger.info(f"x={x}")` |
| 按包控级别 | `getLogger("pkg").setLevel(...)` | 逐个模块设 |

### 文件输出

| 需求 | 做法 |
|---|---|
| 中文正常 | `FileHandler(..., encoding="utf-8")` |
| 目录不存在 | `os.makedirs(dir, exist_ok=True)` 先建 |
| 按大小轮转 | `RotatingFileHandler(maxBytes=10*1024*1024, backupCount=5)` |
| 按时间轮转 | `TimedRotatingFileHandler(when="midnight", backupCount=30)` |
| 多进程 | `QueueHandler` + `QueueListener`，或每进程独立文件 |
| 文件门槛与格式 | 单独 `setLevel` / `setFormatter`，与 stream 独立 |

### 方案选择

| 场景 | 推荐 |
|---|---|
| 脚本、小工具，控制台 + 一个文件 | **方案 A**（basicConfig + addHandler） |
| 生产服务、多 handler、轮转、按模块分配 | **方案 B**（dictConfig） |
| 日志会很大 | `RotatingFileHandler` / `TimedRotatingFileHandler` |
| 交互环境反复执行配置 | `basicConfig(..., force=True)` |

### 日志级别对照

| 级别 | 数值 | 用途 |
|---|---|---|
| `DEBUG` | 10 | 调试细节（SQL、变量） |
| `INFO` | 20 | 正常运行关键节点 |
| `WARNING` | 30 | 异常但可继续（默认根级别） |
| `ERROR` | 40 | 出错，功能受影响 |
| `CRITICAL` | 50 | 严重错误，程序可能退出 |

---

## 一句话记忆

> **库只"报事"，应用才"决定怎么记"；每个模块 `getLogger(__name__)`，handler 只挂根、库永不 `addHandler`；异常堆栈交给 `logger.exception`，务必写在 `except` 里；控制台 + 文件 = `basicConfig` + 手动 `addHandler`（`filename` 和 `stream` 不能同传）；文件必加 `encoding="utf-8"` 并上轮转。**