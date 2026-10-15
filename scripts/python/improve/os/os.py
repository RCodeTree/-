import os

# os 模块（操作系统接口）
# 1. 路径与环境
#
# os.getcwd() 当前目录 / os.chdir(path) 切换
# os.environ 环境变量字典 → 用 os.environ.get("KEY", "默认值") 读（键不存在直接 [] 会 KeyError）
# os.getlogin() 登录名（无 tty 时可能报错），更稳的是 import getpass; getpass.getuser()
current_dir = os.getcwd() # 获取当前目录路径
user = os.environ.get("USER") or os.environ.get("USERNAME", "unknown") # 获取用户名 并 设置默认值
home = os.environ.get("HOME")
print(f"当前目录: {current_dir}")
print(f"{user}")



# 2. 路径工具 os.path（重点，高频）
# os.path.join("logs", "app.log")   # 跨平台拼接 → logs/app.log 或 logs\app.log
# os.path.abspath(".")              # 绝对路径
# os.path.exists(p) / isdir / isfile
# os.path.basename("/var/log/x.log")  # x.log
# os.path.dirname("/var/log/x.log")   # /var/log
# os.path.splitext("x.log")           # ('x', '.log')
# os.path.getsize(p)                  # 字节数

# 3. 目录与文件操作
#
# os.listdir(d) 列出目录
# os.walk(d) 递归遍历（返回 (当前目录, 子目录列表, 文件列表)）
# os.makedirs(p, exist_ok=True) 建多层目录（exist_ok=True 避免已存在报错）
# os.remove / os.rename
