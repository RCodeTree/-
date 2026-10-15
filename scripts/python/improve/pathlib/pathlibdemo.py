from pathlib import Path

# 面向对象的 pathlib 替代字符串拼路径，用 shutil 完成复制、打包、磁盘巡检。这是采集器/日志清理/备份脚本的底层能力。

# pathlib 模块提供了一个面向对象的路径操作接口

# Path(".")          # 相对
# Path.cwd()         # 当前目录（= os.getcwd()）
# Path.home()        # 家目录
# Path("/var/log")   # 绝对（Windows 会自动适配盘符）
Path(".")
current_dir = Path.cwd() # 获取当前目录路径
home_dir = Path.home() # 获取家目录路径
custom_path = Path("/var/log") # 获取自定义路径

print(f"家目录: {home_dir}")
print(f"当前目录: {current_dir}")
print(f"自定义路径: {custom_path}")


print("\n")


# 路径属性
# p = Path.home() / "logs" / "app.log"
# p.name      # app.log
# p.stem      # app          （去后缀）
# p.suffix    # .log
# p.parent    # ~/logs
# p.parts     # 各层元组
# p.absolute()
# p.resolve() # 绝对路径 + 解析软链接
p = Path.home() / "logs" / "app.log" # 创建路径对象
print(f"路径: {p}")
print(f"路径名称: {p.name}")
print(f"路径后缀: {p.suffix}")
print(f"路径.stem: {p.stem}") # 即去后缀的文件名称
print(f"路径.parent: {p.parent}") # 所属目录
print(f"路径.parts: {p.parts}") # ('C:\\', 'Users', 'rong', 'logs', 'app.log')
print(f"路径.absolute(): {p.absolute()}")
print(f"路径.resolve(): {p.resolve()}")
print(f"路径.exists(): {p.exists()}") # 路径是否存在 返回布尔值
print(f"路径.is_file(): {p.is_file()}") # 是否是文件 返回布尔值
print(f"路径.is_dir(): {p.is_dir()}") # 是否是目录 返回布尔值


print("\n")


# 拼接: / 运算符（最优雅）
# p = Path.home() / "logs" / "app.log"   # 跨平台，自动加分隔符
# p2 = p.with_suffix(".txt")             # 改后缀 → app.txt
p2 = p.with_suffix(".txt") # 改后缀 → app.txt
print(f"路径2: {p2}") # 改后缀 → app.txt
print(f"路径.exists(): {p2.exists()}")


print("\n")


# 判断与遍历
# p.exists() / p.is_file() / p.is_dir()
# Path("logs").iterdir()        # 遍历当前层 获取指定目录（这里是 logs 文件夹）下的直接子项（包含文件和文件夹），不会递归进入子文件夹
# Path(".").glob("*.py")        # 当前层匹配 在当前目录（. 代表当前工作目录）下，匹配符合特定模式的文件/文件夹
# Path(".").rglob("*.log")      # 递归匹配（替代 os.walk 的 80% 场景）
test_dir = Path("..") # 获取上一级目录
for p in test_dir.iterdir():
    print(p)

print("\n")

test_dir = Path(".")
for p in test_dir.glob("*.py"):
    print(p)

print("\n")

test_dir = Path("..")
for p in test_dir.rglob("*.py"):
    print(p)


print("\n")


# 建目录 / 读写文件
# Path("a/b/c").mkdir(parents=True, exist_ok=True)  # 建多层，已存在不报错
# Path("out.txt").write_text("hello", encoding="utf-8")
# print(Path("out.txt").read_text(encoding="utf-8"))
# Path("out.txt").unlink()      # 删除文件




