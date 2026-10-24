# Python 实战笔记：argparse · 字符串处理 · asyncio 探活 · 类型注解

> 整理自一次"多主机批量 TCP 探活"脚本开发过程中的问题。
> 主线：`argparse 参数解析` → `字符串切分清洗` → `asyncio 并发探活` → `类型注解`。

---

## 目录

1. [argparse：传入分隔符参数](#1-argparse传入分隔符参数)
2. [argparse：传入多个 host 的几种写法](#2-argparse传入多个-host-的几种写法)
3. [踩坑复盘：`--seq` 为什么没生效](#3-踩坑复盘seq-为什么没生效)
4. [字符串 `strip()` 的用法](#4-字符串-strip-的用法)
5. [`async def prob_tcp(host: str, port: int) -> dict` 签名解析](#5-async-def-prob_tcphost-str-port-int---dict-签名解析)
6. [asyncio 探活核心：`open_connection` + `wait_for` + 关闭](#6-asyncio-探活核心open_connection--wait_for--关闭)
7. [`dict[Any, Any]` 到底是什么](#7-dictany-any-到底是什么)
8. [附：完整可用探活脚本骨架](#8-附完整可用探活脚本骨架)

---

## 1. argparse：传入分隔符参数

### 核心结论
`p.add_argument()` 的 `type` **默认就是 `str`**，逗号、竖线、冒号等普通字符直接就能接收。关键在**命令行怎么传**和**是否要解转义**。

### 基础用法

```python
import argparse

p = argparse.ArgumentParser()
p.add_argument('--sep', default=',', help='分隔符')
args = p.parse_args()
print(repr(args.sep))
```

```bash
python demo.py --sep ,        # 逗号，shell 一般不需引号
python demo.py --sep '|'      # 竖线必须加引号，否则当管道
python demo.py --sep ' '      # 空格必须加引号
python demo.py --sep '::'     # 多字符也行
```

> ⚠️ 字符在 shell 里有特殊含义（`| * > & ; 空格 $` 等）时**必须加引号**，否则程序收不到。

### 想传 `\t`、`\n` 这类控制字符

命令行写 `--sep '\t'`，Python 收到的是**两个字符**（反斜杠 + t），不是 Tab。要自定义 `type` 解码：

```python
def escape_decode(s: str) -> str:
    """把 '\t' 这类转义序列转成真实字符"""
    return s.encode('utf-8').decode('unicode_escape')

p.add_argument('--sep', type=escape_decode, default=',')
```

```bash
python demo.py --sep '\t'   # 输出真正的 Tab
python demo.py --sep '\n'   # 换行
```

> 含中文分隔符时 `unicode_escape` 有坑，可用 `codecs.decode(s, 'unicode_escape')` 或只做有限映射。

### 限制单字符

```python
def one_char(s: str) -> str:
    if len(s) != 1:
        raise argparse.ArgumentTypeError(f'必须是单个字符，收到 {s!r}')
    return s

p.add_argument('--sep', type=one_char, default=',')
```

### 小结

| 需求 | 做法 |
|---|---|
| 普通字符 | `type=str`（默认），shell 特殊字符加引号 |
| `\t \n` 转义 | 自定义 `type` 走 `unicode_escape` |
| 只允许单字符 | 自定义 `type` 校验 `len==1` |
| 限定候选 | `choices=[...]`（别和转义解码混用） |

---

## 2. argparse：传入多个 host 的几种写法

### 方案对比

| 写法 | 命令行形式 | 适合场景 |
|---|---|---|
| `--hosts "a,b,c"` + `--sep` | 一个字符串 | 批量粘贴、host 多、分隔符可变 |
| `nargs='+'` | `--hosts a b c` | **最常用**，简单直接 |
| `action='append'` | `-H a -H b -H c` | 语义上"逐个添加" |
| `type` 里 split | `--hosts a,b,c d` | 灵活，但拿不到 `--sep` |
| `FileType` / 文件读取 | 从文件读 | host 超多、要注释 |

### 最常用：`nargs='+'`

```python
p.add_argument('--hosts', nargs='+', default=['localhost'])
```

```bash
python demo.py --hosts 192.168.1.1 192.168.1.2 web01
```

> ⚠️ `nargs='+'` 会一直吃到下一个选项，位置参数顺序要注意，建议把它放最后。

### 可重复添加：`action='append'`

```python
p.add_argument('-H', '--host', action='append', default=None)
# 使用时：hosts = args.host or []   （避免可变默认值陷阱）
```

```bash
python demo.py -H 192.168.1.1 -H 192.168.1.2
```

### 从文件读

```python
p.add_argument('--hosts-file', type=str, default=None)

if args.hosts_file:
    with open(args.hosts_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                hosts.append(line)
```

> 建议用 `type=str` 而非 `argparse.FileType('r')`：后者在解析阶段立刻开文件，不够灵活。

---

## 3. 踩坑复盘：`--seq` 为什么没生效

### 现象

```python
p.add_argument("--seq", default=",")
p.add_argument("--hosts", help="多个主机IP")
```

```bash
python main.py --seq , --hosts 127.0.0.1,192.168.142.130,10.255.255.1
# 输出：127.0.0.1,192.168.142.130,10.255.255.1   ← 没切分！
```

### 原因

**argparse 不会自动用 `--seq` 去切 `--hosts`**。它们是两个独立参数，argparse 把 `--hosts` 原样收成一个字符串。

也**不能在 `type=` 里切**，因为 `type` 执行时 `args.seq` 还没解析出来。

### 正确做法：`parse_args()` 之后手动 split

```python
args = p.parse_args()

hosts = []
if args.hosts:
    hosts = [h.strip() for h in args.hosts.split(args.seq) if h.strip()]
```

> 一句话：`--seq` 只是普通字符串参数，切分必须自己写 `args.hosts.split(args.seq)`。

---

## 4. 字符串 `strip()` 的用法

### 作用
去掉字符串**首尾**的指定字符（默认是空白字符），返回**新字符串**，中间内容不动。

```python
"  hello world  \n".strip()     # 'hello world'
"hello world".strip()           # 'hello world'（中间空格保留）
```

### 默认去掉的空白字符
空格 `' '`、制表符 `'\t'`、换行 `'\n'`、回车 `'\r'`、换页 `'\f'`、垂直制表 `'\v'`。

### 带参数：字符集合（不是子串！）

```python
"***hello***".strip("*")     # 'hello'
"--=hello=--".strip("-=")    # 'hello'
"abcba".strip("ab")          # 'c'   ← 两端所有 a、b 都被削掉
```

> ⚠️ 大坑：`strip("ab")` 去掉的是首尾**所有** `a` 和 `b`，不是去掉子串 `"ab"`。

### 变体

| 方法 | 处理方向 |
|---|---|
| `strip()` | 首 + 尾 |
| `lstrip()` | 只左 |
| `rstrip()` | 只右 |

### 典型用途：清理分割结果

```python
hosts = [h.strip() for h in args.hosts.split(args.seq) if h.strip()]
```

- `h.strip()`：去掉 `" 192.168.1.1 "` 两边的空格（否则 socket 连接失败）
- `if h.strip()`：过滤空串和纯空格串
- 读文件时 `line.strip()` 去掉行末 `\n`，`if line` 过滤空行

> 补充：`"a,,b".split(",")` → `['a', '', 'b']`，空串不会自动消失，所以需要 `if h.strip()` 过滤。

---

## 5. `async def prob_tcp(host: str, port: int) -> dict` 签名解析

```python
async  def  prob_tcp  (host: str, port: int)  ->  dict
 ①     ②     ③          ④                      ⑤
```

| 编号 | 部分 | 含义 |
|---|---|---|
| ① | `async` | **协程函数**：调用不执行，返回 coroutine 对象，须 `await` |
| ② | `def` | 函数定义关键字 |
| ③ | `prob_tcp` | 函数名（应为 `probe_tcp`，拼写瑕疵不影响运行） |
| ④ | `(host: str, port: int)` | 参数 + **类型注解**（运行时**不校验**，仅供 IDE / 静态检查） |
| ⑤ | `-> dict` | **返回值类型注解**（同样不强制） |

### `async` 的关键行为

```python
result = prob_tcp("127.0.0.1", 22)        # ❌ 只得到 coroutine，不执行
result = await prob_tcp("127.0.0.1", 22)  # ✅ 真正执行
```

并发探活的本质：

```python
tasks = [prob_tcp(h, args.port) for h in hosts]
results = await asyncio.gather(*tasks)    # 全部并发
```

### 为什么用 `async` 而不是线程
探活是 **I/O 密集型**：协程靠事件循环调度，成千上万个也扛得住；线程方案 N 个 host 要 N 个线程，开销大。

### 并发限流（对应 `--concurrency`）

```python
sem = asyncio.Semaphore(args.concurrency)

async def guarded(host):
    async with sem:
        return await prob_tcp(host, args.port)

results = await asyncio.gather(*(guarded(h) for h in hosts))
```

---

## 6. asyncio 探活核心：`open_connection` + `wait_for` + 关闭

```python
reader, writer = await asyncio.wait_for(
    asyncio.open_connection(host, port), timeout=timeout)
writer.close()
await writer.wait_closed()
```

### 第 1~2 行：发起连接 + 超时保护

- `asyncio.open_connection(host, port)` 返回 **coroutine**，`await` 后真正握手，成功返回 `(reader, writer)`：
  - `reader`：`StreamReader`，读数据
  - `writer`：`StreamWriter`，写数据 / 关闭
- `asyncio.wait_for(coro, timeout)`：超时未完成则**取消协程并抛 `asyncio.TimeoutError`**

**为什么必须加超时？** `open_connection` 默认无超时。若目标被防火墙 DROP / 主机宕机，会一直挂到系统 TCP 超时（几十秒到几分钟）。

```python
# 等价写法（Python 3.11+，更干净）
reader, writer = await asyncio.open_connection(host, port, timeout=timeout)
```

### 探活异常对照表

| 情况 | 异常 | 返回速度 |
|---|---|---|
| 端口没开 / 有 RST | `ConnectionRefusedError`（`OSError` 子类） | 秒回 |
| 包被丢 / 主机下线 | `asyncio.TimeoutError` | 等满 timeout |
| 域名解析失败 | `socket.gaierror`（`OSError` 子类） | 秒回 |

> 这两个异常都要 catch，否则一个 host 挂掉会让整个 `gather` 抛异常。

### 第 3 行：`writer.close()`
- **同步**方法，不需要 await
- 请求关闭、开始四次挥手，但**返回时连接未真正关闭完**
- 不 close 会导致 fd 泄漏 → `Too many open files`

### 第 4 行：`await writer.wait_closed()`
- **异步**方法，挂起直到连接彻底关闭、fd 释放（Python 3.7+）

```python
# ❌ 只 close
writer.close()

# ✅ 优雅关闭
writer.close()
await writer.wait_closed()
```

### 两个易踩的坑

**坑 1：超时后 `writer` 未定义**

```python
# ❌ 错：超时路径下 writer 未定义，UnboundLocalError
try:
    reader, writer = await asyncio.wait_for(...)
except asyncio.TimeoutError:
    pass
writer.close()

# ✅ 对：只在成功分支关闭
writer = None
try:
    reader, writer = await asyncio.wait_for(...)
except (asyncio.TimeoutError, OSError) as e:
    result["error"] = type(e).__name__
finally:
    if writer is not None:
        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionResetError, OSError):
            pass
```

**坑 2：`wait_closed()` 本身可能抛异常**，需 `try/except` 兜底。

### 探活的本质
**能成功建立 TCP 连接 = 端口开放**。连上后不读不写立刻关闭，这是端口扫描 / 探活的标准做法。

---

## 7. `dict[Any, Any]` 到底是什么

### 结论：**一个字典**，不是字典数组

```python
dict[K, V]   # 泛型注解：K = 键类型，V = 值类型（不是数组维度！）
dict[Any, Any]   # 一个 dict，键值类型任意
```

### "字典数组"应该这样写

```python
list[dict[Any, Any]]        # 列表，每元素是 dict
list[dict[str, Any]]        # 更推荐：键固定为 str
```

| 注解 | 含义 |
|---|---|
| `dict[Any, Any]` | 一个字典 |
| `list[dict[Any, Any]]` | 字典的列表（"字典数组"） |
| `tuple[dict, dict]` | 恰好两个字典的元组 |
| `dict[str, dict]` | 嵌套字典，不是数组 |

### 关于 `Any`
- 来自 `typing`，**必须** `from typing import Any`
- 意为"任意类型，检查器别管我"——等于**放弃类型检查**
- `-> dict` 和 `-> dict[Any, Any]` 基本等价，后者更显式
- `dict[...]` 内置泛型需 **Python 3.9+**（3.8 及以下用 `typing.Dict`）

### 回到探活场景的两层类型

```python
# prob_tcp 返回单个字典
async def probe_tcp(host: str, port: int) -> dict[str, Any]: ...

# gather 收集后是列表
results: list[dict[str, Any]] = await asyncio.gather(
    *(probe_tcp(h, args.port) for h in hosts)
)
```

### 更推荐：`TypedDict` 精确描述字段

```python
from typing import TypedDict, Optional

class ProbeResult(TypedDict):
    host: str
    port: int
    alive: bool
    latency_ms: Optional[float]
    error: Optional[str]

async def probe_tcp(host: str, port: int) -> ProbeResult: ...
async def probe_all(hosts: list[str], port: int) -> list[ProbeResult]: ...
```

字段固定时用 `TypedDict`，IDE 补全和 mypy 都能真正生效。

---

## 8. 附：完整可用探活脚本骨架

```python
import argparse
import asyncio
import time
from typing import Optional, TypedDict


class ProbeResult(TypedDict):
    host: str
    port: int
    alive: bool
    latency_ms: Optional[float]
    error: Optional[str]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="多主机批量探活 + 并发上报")
    p.add_argument("--seq", default=",", help="分隔符")
    p.add_argument("--hosts", help="多个主机IP(直接传入，用 --seq 分隔)")
    p.add_argument("--hosts-file", type=str, help="多个主机IP(文件形式，每行一个)")
    p.add_argument("--port", type=int, default=22, help="主机端口")
    p.add_argument("--concurrency", type=int, default=3, help="并发数量")
    p.add_argument("--timeout", type=float, default=2.0, help="单机超时(秒)")
    p.add_argument("--out-dir", default="./", help="探活数据落盘目录")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def parse_hosts(args) -> list[str]:
    hosts: list[str] = []
    if args.hosts:
        hosts.extend(h.strip() for h in args.hosts.split(args.seq) if h.strip())
    if args.hosts_file:
        with open(args.hosts_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    hosts.append(line)
    # 去重保序
    seen, result = set(), []
    for h in hosts:
        if h not in seen:
            seen.add(h)
            result.append(h)
    return result


async def probe_tcp(host: str, port: int, timeout: float = 2.0) -> ProbeResult:
    result: ProbeResult = {
        "host": host, "port": port,
        "alive": False, "latency_ms": None, "error": None,
    }
    start = time.perf_counter()
    writer = None
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        result["alive"] = True
        result["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
    except asyncio.TimeoutError:
        result["error"] = "timeout"
    except OSError as e:
        result["error"] = type(e).__name__
    finally:
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except (ConnectionResetError, OSError):
                pass
    return result


async def main() -> None:
    args = build_parser().parse_args()
    hosts = parse_hosts(args)
    sem = asyncio.Semaphore(args.concurrency)

    async def guarded(h: str) -> ProbeResult:
        async with sem:
            return await probe_tcp(h, args.port, args.timeout)

    results = await asyncio.gather(*(guarded(h) for h in hosts))
    for r in results:
        print(r)


if __name__ == "__main__":
    asyncio.run(main())
```

```bash
# 示例
python main.py --seq , \
  --hosts 127.0.0.1,192.168.142.130,10.255.255.1 \
  --port 22 --concurrency 3
```

---

## 速查表（Cheatsheet）

| 主题 | 关键点 |
|---|---|
| `--sep` + `--hosts` | argparse **不会自动 split**，parse 后手动 `.split(args.seq)` |
| 多 host | 首选 `nargs='+'`；可重复添加用 `action='append'` |
| `strip()` | 去首尾空白；`strip("ab")` 是字符集合不是子串；`if h.strip()` 顺带过滤空串 |
| `async def` | 调用返回 coroutine，必须 `await` / `gather` 才执行 |
| 探活超时 | 必须 `wait_for(open_connection(...), timeout=...)`，否则 DROP 场景挂死 |
| 关闭连接 | `writer.close()` + `await writer.wait_closed()`，注意超时时 writer 未定义 |
| 探活原理 | 能建立 TCP 连接即端口开放，连上即关，不传数据 |
| `dict[Any, Any]` | 一个字典，不是数组；数组用 `list[dict[...]]`；字段固定用 `TypedDict` |