# 用 argparse 打造规范的 CLI 工具

> 从"能跑"到"规范"：参数类型、action、子命令、互斥、帮助信息、日志联动、退出码、完整 demo、常见坑。argparse 属于**应用层**（入口脚本），所以它在这里配置 logging 完全符合前文的"库只报事、应用管输出"原则。

---

## 目录

1. [为什么用 argparse](#一为什么用-argparse)
2. [最小骨架](#二最小骨架)
3. [位置参数 vs 可选参数](#三位置参数-vs-可选参数)
4. [参数类型与校验：type / choices / nargs / default](#四参数类型与校验type--choices--nargs--default)
5. [action：一个参数能干什么](#五action一个参数能干什么)
6. [短选项、dest、metavar、help](#六短选项destmetavarhelp)
7. [子命令 subparsers](#七子命令-subparsers)
8. [互斥组与参数组](#八互斥组与参数组)
9. [帮助信息美化：formatter_class](#九帮助信息美化formatter_class)
10. [自定义 type 与自定义 Action](#十自定义-type-与自定义-action)
11. [退出码与错误处理](#十一退出码与错误处理)
12. [与 logging 联动：-v / -q](#十二与-logging-联动-v--q)
13. [规范 CLI 的要素清单](#十三规范-cli-的要素清单)
14. [完整可运行 Demo：logtool](#十四完整可运行-demologtool)
15. [常见坑](#十五常见坑)
16. [速查表](#十六速查表)

---

## 一、为什么用 argparse

| 方式 | 问题 |
|---|---|
| `sys.argv` 手工解析 | 位置、`--opt`、`-o`、默认值、`--help` 全要自己写 |
| `getopt` | 只解析，不生成 help、不校验类型、不给你命名空间 |
| **`argparse`** | 标准库、自动 `--help`/`--version`、类型校验、子命令、互斥、错误退出码一条龙 |

`argparse` 帮你做四件事：**解析、校验、生成帮助、错误时以非 0 退出码退出**。你只需要声明"我要哪些参数"。

---

## 二、最小骨架

```python
import argparse

def main():
    parser = argparse.ArgumentParser(
        prog="mytool",                      # 程序名，默认取 sys.argv[0] 的 basename
        description="一句话说明这个工具干什么",   # 显示在 --help 顶部
        epilog="更多用法见 https://example.com", # 显示在 --help 底部
    )
    parser.add_argument("name", help="要问候的人")
    parser.add_argument("--times", type=int, default=1, help="重复次数（默认 1）")
    args = parser.parse_args()              # 从 sys.argv[1:] 解析

    for _ in range(args.times):
        print(f"Hello, {args.name}!")

if __name__ == "__main__":
    main()
```

```bash
$ python mytool.py Alice --times 2
Hello, Alice!
Hello, Alice!

$ python mytool.py            # 缺位置参数 → 自动报错 + 退出码 2
usage: mytool [-h] [--times TIMES] name
mytool: error: the following arguments are required: name

$ python mytool.py --help     # 自动生成，不用自己写
usage: mytool [-h] [--times TIMES] name
...
```

**`parse_args()` 返回一个 `Namespace`**，参数按 `dest` 名字变成属性：`args.name`、`args.times`。

> `parse_known_args()` 返回 `(namespace, 未识别的剩余列表)`，用于"把其余参数透传给子进程"的场景（如 `mygit ... -- git ...`）。

---

## 三、位置参数 vs 可选参数

```python
parser.add_argument("input")              # 位置参数：必须给，按顺序
parser.add_argument("-o", "--output")     # 可选参数：可省略，-o / --output 等价
```

| | 位置参数 | 可选参数 |
|---|---|---|
| 是否必填 | **默认必填**（`nargs='?'` 可改为可选） | 默认可选（`required=True` 可强制） |
| 书写 | 按位置顺序 | `-o val` / `--output val` / `--output=val` |
| `dest` | 取名字本身 | 取长选项名（`--foo-bar` → `foo_bar`），或显式 `dest=` |

**短选项和长选项绑在同一个 `add_argument` 里，是同一个参数的两个名字**，不是两个参数：

```python
parser.add_argument("-o", "--output", dest="output_file")
# 结果只有 args.output_file 一个属性
```

---

## 四、参数类型与校验：type / choices / nargs / default

### `type`：把字符串转成目标类型

```python
parser.add_argument("--port", type=int, default=8000)     # 自动 int()，失败报错
parser.add_argument("--ratio", type=float, default=0.5)
parser.add_argument("--path", type=Path)                  # 可以是任意 callable
```

`type` 是**任意可调用对象**，返回值放进 namespace。转换失败时 argparse 自动生成错误并退出码 2，**不用你写 try/except**。

### `choices`：限定取值

```python
parser.add_argument("--format", choices=["json", "text", "csv"], default="text")
# 传 --format xml → error: argument --format: invalid choice: 'xml' (choose from 'json', 'text', 'csv')
```

`choices` 在 `type` 转换**之后**校验。所以 `type=int, choices=[1,2,3]` 是合法的。

### `nargs`：接收几个值

| 写法 | 含义 | 结果 |
|---|---|---|
| 不写 | 1 个值 | 值本身 |
| `nargs=3` | 恰好 3 个 | **list** |
| `nargs='?'` | 0 或 1 个 | 值或 `default`/`const` |
| `nargs='*'` | 0 个或多个 | **list**（可为 `[]`） |
| `nargs='+'` | 1 个或多个 | **list**（至少 1 个，否则报错） |
| `nargs=argparse.REMAINDER` | 剩余全部 | **list** |

> ⚠️ **只要写了 `nargs`（包括 `nargs=1`），结果就是 list**。`nargs=1` 得到 `["x"]` 而不是 `"x"`——这是最常见的坑之一。

```python
parser.add_argument("files", nargs="+", help="至少一个文件")
parser.add_argument("--tags", nargs="*", default=[], help="可选标签")
```

### `default`

```python
parser.add_argument("--level", default="INFO")
parser.add_argument("--verbose", action="store_true")   # 布尔 flag，默认 False
```

`default=argparse.SUPPRESS` 可以**让该属性不出现在 namespace 里**（用 `getattr(args, "x", None)` 时很有用）。

> ⚠️ **可变默认值的坑**：`default=[]` 在多处共享同一个 list。argparse 在 `append` 场景其实会先 copy，但自己写自定义逻辑时留意别原地修改。

### `required`：强制可选参数必填

```python
parser.add_argument("--token", required=True)   # 写成可选但必须给
```

用这个**要克制**：可选参数加 `required=True` 会让人困惑（`--token` 明明是 `--` 却必填）。如果确实必填，通常不如写成位置参数。常见例外是"必须显式传的配置项"（如 `--env prod`）。

---

## 五、action：一个参数能干什么

`action` 决定"解析到该参数时对 namespace 做什么"。常用值：

| `action` | 效果 | 典型用法 |
|---|---|---|
| `store`（默认） | 存值 | `--name foo` → `args.name = "foo"` |
| `store_true` | 出现即 `True`，默认 `False` | `--debug` |
| `store_false` | 出现即 `False`，默认 `True` | `--no-color` |
| `store_const` | 出现即设为 `const` 值 | `--fast` → `level="fast"` |
| `append` | 每次出现往 list 追加 | `-I a -I b` → `["a","b"]` |
| `count` | 出现次数累加 | `-vvv` → `3` |
| `version` | 打印版本后退出 | `--version` |
| `help` | 打印帮助后退出（`-h` 默认） | `-h` |

### 布尔开关

```python
parser.add_argument("--debug", action="store_true", help="开启调试")
parser.add_argument("--no-color", action="store_false", dest="color", help="关闭彩色输出")
parser.set_defaults(color=True)   # store_false 需要把默认值设回 True
```

> Python 3.9+ 有 `argparse.BooleanOptionalAction`，一个参数同时提供正反两个开关：
> ```python
> parser.add_argument("--color", action=argparse.BooleanOptionalAction, default=True)
> # 用户可写 --color 或 --no-color，help 里自动显示 "--color, --no-color"
> ```

### 累加与计数

```python
parser.add_argument("-I", "--include", action="append", default=[], metavar="DIR")
parser.add_argument("-v", "--verbose", action="count", default=0)
```

```bash
$ mytool -I src -I tests -vvv
# args.include == ["src", "tests"], args.verbose == 3
```

`count` 是"`-v` 越多越详细"的标准做法，后面[第十二节](#十二与-logging-联动-v--q)用它映射 logging 级别。

### `store_const`：开关映射到固定值

```python
parser.add_argument("--fast", dest="mode", action="store_const", const="fast")
parser.add_argument("--safe", dest="mode", action="store_const", const="safe")
parser.set_defaults(mode="safe")
```

---

## 六、短选项、dest、metavar、help

```python
parser.add_argument(
    "-n", "--num",          # 短/长选项
    dest="count",           # namespace 里的属性名（不写则取长选项名）
    type=int,
    default=10,
    metavar="N",            # help 里占位符显示成 -n N 而不是 -n COUNT
    help="输出条数（默认 10）",
)
```

- **`dest`**：决定 `args.xxx` 的名字。长选项 `--foo-bar` 默认转成 `foo_bar`。
- **`metavar`**：只影响 `--help` 里占位符的显示，不影响取值。
- **`help`**：出现在 `--help` 里。可以写 `%(default)s`、`%(prog)s` 等占位符，配合 `ArgumentDefaultsHelpFormatter` 自动填值。

**`-h` 是保留的**，`add_argument` 用 `-h` 会报冲突。要禁用帮助：`ArgumentParser(add_help=False)`。

---

## 七、子命令 subparsers

复杂工具（git、pip、docker）都用子命令：`mytool parse ...`、`mytool stats ...`。

```python
parser = argparse.ArgumentParser(prog="logtool")
sub = parser.add_subparsers(dest="command", required=True)   # required 3.7+

# 子命令 1
p_parse = sub.add_parser("parse", help="解析日志并输出")
p_parse.add_argument("file")
p_parse.add_argument("--format", choices=["json", "text"], default="text")

# 子命令 2
p_stats = sub.add_parser("stats", help="统计状态码分布")
p_stats.add_argument("file")
p_stats.add_argument("--top", type=int, default=10)

args = parser.parse_args()
print(args.command)   # "parse" 或 "stats"
```

要点：

1. **`dest="command"`** 才能知道用户选了哪个子命令；`required=True`（3.7+）保证必须给，否则不会报错而是 `None`。
2. 每个子命令是**独立的 `ArgumentParser`**，参数互不影响。
3. 全局参数要加在**主 parser** 上，且必须放在子命令**之前**：`logtool -v parse x.log` ✅，`logtool parse -v x.log` ❌（`-v` 会被当成子命令 parse 的参数，除非 parse 里也定义）。

### 用 `set_defaults` 做命令分派（推荐模式）

```python
def cmd_parse(args): ...
def cmd_stats(args): ...

p_parse.set_defaults(func=cmd_parse)
p_stats.set_defaults(func=cmd_stats)
parser.set_defaults(func=lambda a: parser.print_help())   # 兜底

args = parser.parse_args()
args.func(args)     # 一行分派，不用 if/elif 链
```

**好处**：新增子命令只加 `set_defaults(func=...)`，分派逻辑零改动。

---

## 八、互斥组与参数组

### 互斥组 `add_mutually_exclusive_group`

同一组里**最多出现一个**，否则报错：

```python
g = parser.add_mutually_exclusive_group()
g.add_argument("--json", action="store_true", help="JSON 输出")
g.add_argument("--csv",  action="store_true", help="CSV 输出")

# $ mytool --json --csv  → error: argument --csv: not allowed with argument --json
```

也可以让其中一个 `required=True`，表示"这组里必须选一个"：

```python
g = parser.add_mutually_exclusive_group(required=True)
g.add_argument("--file", help="从文件读")
g.add_argument("--stdin", action="store_true", help="从标准输入读")
```

### 参数组 `add_argument_group`

**只影响 help 的排版分组，不做互斥**——用来把参数归类，让 `--help` 更易读：

```python
io_group = parser.add_argument_group("输入输出")
io_group.add_argument("input")
io_group.add_argument("-o", "--output")

log_group = parser.add_argument_group("日志选项")
log_group.add_argument("-v", "--verbose", action="count", default=0)
log_group.add_argument("-q", "--quiet", action="store_true")
```

`--help` 里会分节展示：`输入输出:`、`日志选项:`。

---

## 九、帮助信息美化：formatter_class

默认 formatter 会**把多行 help 折成一行**，破坏你精心写的示例排版。常用四种：

| formatter_class | 作用 |
|---|---|
| `ArgumentDefaultsHelpFormatter` | 自动在 help 末尾追加 `(default: xxx)` |
| `RawDescriptionHelpFormatter` | **保留 description/epilog 的原始换行** |
| `RawTextHelpFormatter` | 保留**所有** help 文本换行（包括参数 help） |
| `MetavarTypeHelpFormatter` | 用 `type` 的名字作 metavar（`int` 显示成 `INT`） |

最常用的组合是**自定义一个"带默认值 + 保原文换行"的类**：

```python
class RichFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    pass

parser = argparse.ArgumentParser(
    description="""日志分析工具。

示例:
  logtool parse access.log --format json
  logtool stats access.log --top 5
""",
    formatter_class=RichFormatter,
)
```

---

## 十、自定义 type 与自定义 Action

### 自定义 `type`：把校验逻辑写成一个函数

```python
def positive_int(s):
    v = int(s)              # 先转换，失败会被 argparse 捕获
    if v <= 0:
        raise argparse.ArgumentTypeError(f"必须是正整数，收到 {v}")
    return v

parser.add_argument("--workers", type=positive_int, default=4)
```

规则：**转换失败或校验失败，抛 `ArgumentTypeError`**（或 `ValueError`/`TypeError`），argparse 会把它变成漂亮的错误消息 + 退出码 2。

### 自定义 `Action`：解析时执行副作用

```python
class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        d = dict(getattr(namespace, self.dest, None) or {})
        k, _, v = values.partition("=")
        if not _:
            raise argparse.ArgumentError(self, f"需要 K=V 格式，收到 {values!r}")
        d[k] = v
        setattr(namespace, self.dest, d)

parser.add_argument("-D", "--define", action=KeyValueAction, default={},
                    metavar="K=V", help="定义变量，可重复")
```

```bash
$ mytool -D a=1 -D b=2
# args.define == {"a": "1", "b": "2"}
```

### 关于 `argparse.FileType`

```python
parser.add_argument("input", type=argparse.FileType("r", encoding="utf-8"))
```

它会**在解析时就把文件打开**，`args.input` 是文件对象。便利但缺点明显：

- 参数错了才走到这里也会**先打开文件**，资源管理混乱；
- 无法优雅处理 `-`（标准输入，需要自己写）；
- 出错信息不够可控。

**推荐做法：`type=Path`，在 `main()` 里自己打开**，这样错误处理、`-` 支持、上下文管理都清晰：

```python
from pathlib import Path
parser.add_argument("input", type=Path)
...
if str(args.input) == "-":
    f = sys.stdin
else:
    f = args.input.open("r", encoding="utf-8")
```

---

## 十一、退出码与错误处理

argparse 的退出码约定：

| 情况 | 退出码 | 触发 |
|---|---|---|
| 正常解析 | 0 | 你 `return`/`sys.exit(0)` |
| 参数错误 | **2** | 缺必填、类型错、choices 不匹配、互斥冲突 |
| `-h` / `--help` | 0 | 打印帮助 |
| `--version` | 0 | 打印版本 |

**主动报错退出**：

```python
parser.error("文件不存在: x.log")   # 打印 usage + 错误消息，退出码 2
parser.exit(1, "致命错误\n")        # 自定义退出码和消息
```

**捕获错误而不退出**（Python 3.9+）：

```python
parser = argparse.ArgumentParser(exit_on_error=False)
try:
    args = parser.parse_args(["--port", "abc"])
except argparse.ArgumentError as e:
    print("参数错:", e)
```

> 默认 `exit_on_error=True`，即参数错直接 `SystemExit(2)`。只有想**在测试或嵌进别的程序**时才关掉。

**`--version` 标准写法**：

```python
parser.add_argument("--version", action="version", version="%(prog)s 1.2.3")
```

`%(prog)s` 会被替换成程序名。版本号最好来自包元数据（`importlib.metadata.version("mypkg")`），避免两处维护。

**`main()` 返回退出码的规范结构**：

```python
def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)     # argv=None 时用 sys.argv[1:]
    try:
        return args.func(args) or 0    # 子命令返回 int 或 None
    except MyAppError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**传 `argv=None` 给 `parse_args`** 让函数可测试：测试里 `main(["--format", "json", "x.log"])` 即可，不用 mock `sys.argv`。

---

## 十二、与 logging 联动：-v / -q

这是"规范 CLI"最能体现专业度的一处。`-v` 计数 → 提高日志级别，`-q` → 压低：

```python
import logging

LOG_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]   # -v 0/1/2

parser.add_argument("-v", "--verbose", action="count", default=0,
                    help="增加输出详细度，可重复 -vv")
parser.add_argument("-q", "--quiet", action="store_true",
                    help="只输出错误")

args = parser.parse_args()

if args.quiet:
    level = logging.ERROR
else:
    level = LOG_LEVELS[min(args.verbose, len(LOG_LEVELS) - 1)]

logging.basicConfig(level=level,
                    format="%(levelname)s %(name)s: %(message)s")
```

**注意**：

- `-v` 和 `-q` 语义相反，用**互斥组**更规范（见[第八节](#八互斥组与参数组)）。
- CLI 里配置 logging 是**完全正确的**——CLI 属于应用层，正是[前文笔记]( # )所说"应用负责 basicConfig"的地方。库代码（`core.py`）依旧只 `getLogger(__name__)`。
- 若同时支持 `--log-file`，就按前文方案 A 再 `addHandler`。

---

## 十三、规范 CLI 的要素清单

一个"规范"的 CLI 工具通常具备：

| 要素 | 做法 |
|---|---|
| **自动帮助** | 每个参数都写 `help=`，`description` 说明用途 |
| **版本** | `--version`，版本号来自包元数据 |
| **详细的日志控制** | `-v` 计数 / `-q` 静默，映射到 logging |
| **默认值可读** | `ArgumentDefaultsHelpFormatter` 或 `help` 里写清默认 |
| **限定取值** | 枚举用 `choices=`，数字用 `type=` + 自定义校验 |
| **有意义的名字** | 长选项 `--foo-bar`，短选项只留最常用的 |
| **子命令组织** | 功能多时用 `subparsers`，配合 `set_defaults(func=...)` |
| **stdin/stdout 友好** | `-` 表示标准输入/输出，方便管道 |
| **有意义的退出码** | 0 成功、1 运行时错误、2 参数错误（argparse 已给） |
| **可测试** | `main(argv=None)`，参数解析与业务逻辑分离 |
| **错误走 stderr** | 报错用 `parser.error` 或 `print(..., file=sys.stderr)` |
| **不滥用 required** | 可选参数尽量真可选 |

---

## 十四、完整可运行 Demo：logtool

一个日志分析 CLI，串起上面所有特性。案例沿用前面的 Nginx 日志。

### 项目结构

```
logtool/
├── pyproject.toml
└── logtool/
    ├── __init__.py          # __version__
    ├── cli.py               # 入口：build_parser + main
    └── core.py              # 纯业务，零 argparse，只发日志
```

### `logtool/core.py` —— 业务层（库风格，只发日志）

```python
import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)

LOG_RE = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s.*?"(?P<method>\w+) (?P<path>\S+) .*?"\s'
    r'(?P<status>\d+)\s(?P<size>\d+)'
)


def parse_lines(lines):
    """逐行解析，返回命中记录列表。"""
    rows = []
    for lineno, line in enumerate(lines, 1):
        line = line.rstrip("\n")
        if not line:
            continue
        m = LOG_RE.search(line)
        if not m:
            logger.warning("第 %d 行无法解析，已跳过", lineno)
            continue
        rows.append(m.groupdict())
    logger.info("共解析 %d 行，命中 %d 条", lineno, len(rows))
    return rows


def status_distribution(rows):
    return Counter(r["status"] for r in rows)
```

**注意**：`core.py` 里**没有 argparse、没有 basicConfig**——它不知道自己是命令行还是被 import，符合"库只报事"。

### `logtool/cli.py` —— 入口（应用层，负责 argparse + logging）

```python
import argparse
import json
import logging
import sys
from pathlib import Path

from .core import parse_lines, status_distribution
from . import __version__


class RichFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    pass


def positive_int(s):
    v = int(s)
    if v <= 0:
        raise argparse.ArgumentTypeError(f"必须是正整数，收到 {v}")
    return v


def open_input(path: Path):
    """支持 - 表示 stdin。"""
    if str(path) == "-":
        return sys.stdin
    return path.open("r", encoding="utf-8")


# ---------- 子命令实现：返回退出码 ----------

def cmd_parse(args):
    with open_input(args.input) as f:
        rows = parse_lines(f)

    if args.format == "json":
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        for r in rows:
            print(f'{r["ip"]:<15} {r["method"]:<6} {r["status"]} {r["path"]}')
    return 0


def cmd_stats(args):
    with open_input(args.input) as f:
        rows = parse_lines(f)

    dist = status_distribution(rows)
    for status, n in dist.most_common(args.top):
        print(f"{status}: {n}")
    return 0


# ---------- 构建解析器 ----------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="logtool",
        description="""Nginx 访问日志分析工具。

示例:
  logtool parse access.log
  logtool parse - --format json | jq .
  logtool stats access.log --top 5
""",
        epilog="完整文档见 https://example.com/logtool",
        formatter_class=RichFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # 全局日志选项（必须写在子命令之前）
    log_group = parser.add_argument_group("日志选项")
    mx = log_group.add_mutually_exclusive_group()
    mx.add_argument("-v", "--verbose", action="count", default=0,
                    help="提高输出详细度，可重复")
    mx.add_argument("-q", "--quiet", action="store_true", help="只输出错误")

    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    # parse
    p = sub.add_parser("parse", help="解析并输出记录", formatter_class=RichFormatter)
    p.add_argument("input", type=Path, help="日志文件，- 表示标准输入")
    p.add_argument("--format", choices=["text", "json"], default="text",
                   help="输出格式")
    p.set_defaults(func=cmd_parse)

    # stats
    s = sub.add_parser("stats", help="统计状态码分布", formatter_class=RichFormatter)
    s.add_argument("input", type=Path, help="日志文件，- 表示标准输入")
    s.add_argument("--top", type=positive_int, default=10, metavar="N",
                   help="只显示前 N 个状态码")
    s.set_defaults(func=cmd_stats)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # ✅ 应用层配置 logging（CLI 正是"应用"）
    if args.quiet:
        level = logging.ERROR
    else:
        level = [logging.WARNING, logging.INFO, logging.DEBUG][min(args.verbose, 2)]
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,          # 日志走 stderr，stdout 留给数据
    )

    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(f"logtool: 文件不存在: {e.filename}", file=sys.stderr)
        return 1
    except BrokenPipeError:         # 管道被 head 关掉，安静退出
        return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `logtool/__init__.py`

```python
__version__ = "1.0.0"
```

### `pyproject.toml`（注册命令 `logtool`）

```toml
[project]
name = "logtool"
version = "1.0.0"
requires-python = ">=3.9"

[project.scripts]
logtool = "logtool.cli:main"
```

### 运行效果

```bash
$ logtool --help
usage: logtool [-h] [--version] [-v | -q] COMMAND ...

Nginx 访问日志分析工具。

示例:
  logtool parse access.log
  logtool parse - --format json | jq .
  logtool stats access.log --top 5

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

日志选项:
  -v, --verbose         提高输出详细度，可重复 (default: 0)
  -q, --quiet           只输出错误

COMMAND:
  parse                解析并输出记录
  stats                统计状态码分布

$ logtool parse access.log
127.0.0.1       GET    502 /api/v1

$ logtool parse - --format json < access.log
[{"ip": "127.0.0.1", "method": "GET", "path": "/api/v1", "status": "502", "size": "4321"}]

$ logtool stats access.log --top 5 -v
INFO logtool.core: 共解析 1 行，命中 1 条
502: 1

$ logtool stats x.log --top 0
logtool: error: argument --top: 必须是正整数，收到 0

$ cat access.log | logtool stats - --top 3
```

**这个 demo 体现的规范点**：

- 应用层（cli.py）负责 argparse 与 logging，业务层（core.py）零配置；
- 子命令 + `set_defaults(func=...)` 分派；
- `-v`/`-q` 互斥，`action="count"` 映射日志级别；
- 自定义 `positive_int` 校验；
- `--format` 用 `choices` 限定；
- `-` 支持 stdin，方便管道；
- 日志走 stderr，**stdout 留给数据**（管道友好）；
- 退出码：0 成功、1 文件不存在、2 参数错（argparse 自动）；
- `main(argv=None)` 可测试；
- 帮助信息排版友好（自定义 formatter）。

---

## 十五、常见坑

### 坑 1：`nargs=1` 得到的是 list

```python
parser.add_argument("--x", nargs=1)
# args.x == ["v"]，不是 "v"
```
除非你真要 list，否则别写 `nargs=1`，直接不写 nargs。

### 坑 2：全局参数放错位置

```bash
$ logtool parse -v access.log     # ❌ -v 是主 parser 的，子命令不认识
logtool: error: unrecognized arguments: -v
$ logtool -v parse access.log     # ✅ 全局参数在子命令前
```
解决办法：要么放前面，要么在每个子命令里也 `add_argument`。

### 坑 3：`allow_abbrev` 导致前缀歧义

默认 `allow_abbrev=True`，`--ver` 会尝试匹配 `--verbose`/`--version`，歧义就报错，不歧义就"帮你猜"。**生产工具建议关掉**，避免"猜错参数"的隐性问题：

```python
parser = argparse.ArgumentParser(allow_abbrev=False)
```

### 坑 4：`store_false` 忘记设默认值

```python
parser.add_argument("--no-color", action="store_false", dest="color")
# 不写 set_defaults，args.color 默认是 False —— 和直觉相反！
parser.set_defaults(color=True)   # ✅ 必须补上
```

### 坑 5：可变默认值

```python
parser.add_argument("--tags", nargs="*", default=[])   # 一般安全（argparse 会处理），
# 但自定义 Action 里原地修改 default 对象会污染多次调用
```
自定义 Action 里对 list/dict 操作前先 copy。

### 坑 6：`type=argparse.FileType` 提前打开文件

参数错、别的参数还没校验完，文件已经被打开。**用 `type=Path` 延迟打开**，自己控制错误和 `-`。

### 坑 7：把日志打到 stdout

`logging.basicConfig()` 默认输出到 **stderr**（对），但如果你改成 `stream=sys.stdout`，数据输出和日志混在一起，管道 `| jq` 就炸了。**数据走 stdout，日志走 stderr**。

### 坑 8：`--version` 的两处维护

```python
parser.add_argument("--version", action="version", version="1.0.0")  # ❌ 硬编码
```
用包元数据：
```python
from importlib.metadata import version
parser.add_argument("--version", action="version",
                    version=f"%(prog)s {version('logtool')}")
```

### 坑 9：`dest` 拼错，运行时才 `AttributeError`

`args.foo_bar` 写错成 `args.foobar`，argparse 不报错，直到用到才炸。**用 IDE 补全或尽快加测试**。也可以在 `main` 开头断言关键属性存在。

---

## 十六、速查表

### 参数声明

| 目的 | 写法 |
|---|---|
| 位置参数 | `add_argument("path")` |
| 可选参数 | `add_argument("-o", "--output")` |
| 必填的可选参数 | `add_argument("--token", required=True)`（慎用） |
| 布尔开关 | `action="store_true"` / `"store_false"`（后者配 `set_defaults`） |
| 正反开关（3.9+） | `action=argparse.BooleanOptionalAction` |
| 枚举 | `choices=["json","text"]` |
| 类型转换 | `type=int` / `type=Path` / 自定义函数 |
| 多个值 | `nargs="+"` / `"*"` / `"?"` / `N` |
| 累加 | `action="append"` |
| 计数 | `action="count"` |
| 版本 | `action="version"` |
| 固定值 | `action="store_const", const=...` |
| 自定义副作用 | 继承 `argparse.Action` |

### 结构

| 需求 | 做法 |
|---|---|
| 子命令 | `subparsers = parser.add_subparsers(dest="cmd", required=True)` |
| 命令分派 | 每个子命令 `set_defaults(func=handler)`，`args.func(args)` |
| 互斥 | `add_mutually_exclusive_group(required=...)` |
| 帮助分组 | `add_argument_group("标题")` |
| 保留多行 description | `RawDescriptionHelpFormatter` |
| 显示默认值 | `ArgumentDefaultsHelpFormatter` |
| 可测试 | `main(argv=None)`，`parse_args(argv)` |

### 退出码

| 情况 | 码 |
|---|---|
| 成功 | 0 |
| 参数错误（argparse 自动） | 2 |
| 运行时错误（自己 `return 1`） | 1 |
| `--help` / `--version` | 0 |

### 与 logging 联动

| CLI 选项 | logging |
|---|---|
| `-v` `action="count"` | `[WARNING, INFO, DEBUG][min(v, 2)]` |
| `-q` `store_true` | `logging.ERROR` |
| `-v` 与 `-q` | 互斥组 |
| 日志流 | **stderr**（stdout 留给数据） |
| 配置位置 | CLI 入口 `basicConfig`；业务模块只 `getLogger(__name__)` |

---

## 一句话记忆

> **argparse = 声明式参数定义 + 自动帮助/校验/退出码**；位置参数默认必填、`nargs` 一律返回 list、`store_false` 记得补 `set_defaults`；功能多就用子命令 + `set_defaults(func=...)` 分派；`-v`/`-q` 用互斥组映射 logging 级别，**数据走 stdout、日志走 stderr**；CLI 是应用层，配置 logging 正是它的职责，业务模块保持"只发日志"的库风格。