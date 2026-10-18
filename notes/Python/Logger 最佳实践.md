# Python Logging 完整笔记

> 涵盖：logger 层级、有效级别、三条最佳实践、完整 demo、常见坑与速查。

---

## 目录

1. [核心模型：Logger 层级树](#一核心模型logger-层级树)
2. [有效级别：一条日志"出不出得来"](#二有效级别一条日志出不出得来)
3. [三条最佳实践](#三三条最佳实践)
4. [完整可运行 Demo](#四完整可运行-demo)
5. [常见误区：模块里写 `logging.info`](#五常见误区模块里写-logginginfo)
6. [惰性格式化](#六惰性格式化)
7. [异常记录](#七异常记录)
8. [进阶：dictConfig](#八进阶dictconfig)
9. [速查表](#九速查表)

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

| 写法 | 结果 | 问题 |
|---|---|---|
| `getLogger(__name__)` | `mypkg.db` | ✅ 可分层控制 |
| `getLogger("db")` | `db` | ❌ 与 `mypkg` 无父子关系，无法按包控制 |
| `logging.info(...)` | `root` | ❌ 丢失模块信息，无法分层 |

分层带来的好处——**一行控制整个库**：

```python
logging.getLogger("mypkg").setLevel(logging.WARNING)  # mypkg 下所有子模块 INFO 全部压掉
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

| 事件 | 结论 |
|---|---|
| 调用 `logging.info()` 会改级别吗？ | **不会**。级别只由 `basicConfig` / `setLevel` 决定 |
| 在 `basicConfig(level=DEBUG)` 下 `logging.debug()` 出得来吗？ | **会**，门槛是 DEBUG，所有级别都放行 |
| 根设成 `WARNING` 后 `logging.debug()` 出得来吗？ | **不会**，方法名决定事件级别，门槛拦住就出不来 |

**"调用的方法名"决定事件级别，"配置的 level"决定门槛，二者完全独立。**

---

## 三、三条最佳实践

### ✅ 实践 1：每个模块用 `getLogger(__name__)`

```python
# mypkg/db.py
import logging
logger = logging.getLogger(__name__)   # → "mypkg.db"
```

- 日志里的 `%(name)s` 自动显示模块路径，**一眼定位哪行代码打的**；
- 保留层级关系，可按包/子模块精细调级别、加 handler。

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

`logger.exception(msg)` ≡ `logger.error(msg, exc_info=True)`，级别 ERROR，**自动附带完整 Traceback**。

**为什么必须在 `except` 内？** 它依赖"当前线程正在处理的异常"（`sys.exc_info()`）。出块后异常信息是空的：

```python
try:
    risky()
except Exception:
    pass

logger.exception("这行在外面")   # ❌ 输出: NoneType: None
```

**三种写法对比：**

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

> 无活跃异常但想记录某个异常对象：`logger.error("...", exc_info=exc)`（3.5+）。

---

## 四、完整可运行 Demo

### 项目结构

```
demo/
├── main.py                 # 应用入口：唯一调用 basicConfig 的地方
└── mypkg/                  # 模拟第三方库
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
import sys
from mypkg import service

# ✅ 只有应用配置 logging，且只配一次
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)


def main():
    service.get_users()
    service.dangerous_op()


if __name__ == "__main__":
    main()
```

### 输出

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

**观察点：**
- `%(name)s` 直接显示模块路径，定位清晰；
- `logger.exception` 自动追加 Traceback；
- 库代码零配置，日志仍按应用配置输出（`propagate=True` 冒泡到根）。

---

## 五、常见误区：模块里写 `logging.info`

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

**但它能出来吗？能**——取决于根 level 放不放行，与写法无关。

**验证代码：**

```python
import logging, sys
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    datefmt="%H:%M:%S", stream=sys.stdout)

logger = logging.getLogger("mypkg.db")

print("根 logger 级别:", logging.getLogger().level)   # 10
print("子 logger 级别:", logger.level)               # 0 (NOTSET，靠继承)

logging.debug("根 logger 发 debug")     # ✅ 名字 root
logging.info("根 logger 发 info")       # ✅ 名字 root
logger.debug("模块 logger 发 debug")    # ✅ 名字 mypkg.db
logger.info("模块 logger 发 info")      # ✅ 名字 mypkg.db

logging.getLogger().setLevel(logging.WARNING)   # 现在才真的改级别
logging.info("这句不出了")              # ❌ 被 WARNING 拦住
logger.warning("这句出")                # ✅ 继承 WARNING
```

---

## 六、惰性格式化

**用 `%s` 占位符，别用 f-string：**

```python
logger.debug("SQL: %s", sql)     # ✅ 只有级别放行才拼字符串
logger.debug(f"SQL: {sql}")      # ❌ 即使 DEBUG 关着也会先算 f-string
```

高频率日志 + 昂贵参数时差距明显。logger 内部把 `%` 运算延迟到真正要输出时。

> 例外：`exc_info` 已带异常时，**别把异常再塞进 message**，否则重复。  
> `logger.exception(f"失败: {e}")` → 改为 `logger.exception("查询失败")`。

---

## 七、异常记录

### 核心规则

| 场景 | 写法 |
|---|---|
| `except` 块内记录 | `logger.exception("msg")` |
| 想用非 ERROR 级别 | `logger.xxx("msg", exc_info=True)` |
| 无活跃异常、有异常对象 | `logger.error("msg", exc_info=exc)` |
| 不要这样做 | `logger.error(str(e))`（丢堆栈）、`except` 外调 `exception` |

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

## 八、进阶：dictConfig

`basicConfig` 只能配根 logger。复杂场景（按 logger 分配 handler/级别）用 `dictConfig`：

```python
import logging.config

logging.config.dictConfig({
    "version": 1,
    "formatters": {
        "std": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "std"}
    },
    "loggers": {
        "mypkg":     {"level": "WARNING"},     # 库整体压到 WARNING
        "mypkg.db":  {"level": "DEBUG"},       # db 子模块单独开 DEBUG
    },
    "root": {"level": "INFO", "handlers": ["console"]},
})
```

**这正体现"按 `__name__` 分层"的威力——只有点分名字的 logger 才能精确控制到子模块。**

---

## 九、速查表

| 场景 | 做法 | 反例 |
|---|---|---|
| 拿 logger | `logging.getLogger(__name__)` | `getLogger("db")`（丢层级）/ `logging.info`（走 root） |
| 库模块 | 只调 `logger.xxx()` | `basicConfig` / `addHandler` / `setLevel` |
| 应用入口 | `basicConfig` 或 `dictConfig`，**只配一次** | 每个模块都配一遍 |
| 重复配置根 logger | `basicConfig(..., force=True)` | 直接再调（静默失效） |
| 记录异常 | `logger.exception("msg")`（在 `except` 内） | `logger.error(str(e))` / `except` 外调 `exception` |
| 带参数 | `logger.info("x=%s", x)` | `logger.info(f"x={x}")` |
| 按包控级别 | `getLogger("pkg").setLevel(...)` | 逐个模块设 |
| 输出到文件 | 应用层 handler 配置 | 库自己写文件 |

### 一句话记忆

> **库只"报事"，应用才"决定怎么记"；异常堆栈交给 `logger.exception`，务必写在 `except` 里；级别配置只看 `basicConfig`/`setLevel`，调哪个方法不影响级别。**

---

## 附：日志级别对照

| 级别 | 数值 | 用途 |
|---|---|---|
| `DEBUG` | 10 | 调试细节（SQL、变量） |
| `INFO` | 20 | 正常运行关键节点 |
| `WARNING` | 30 | 异常但可继续（默认根级别） |
| `ERROR` | 40 | 出错，功能受影响 |
| `CRITICAL` | 50 | 严重错误，程序可能退出 |