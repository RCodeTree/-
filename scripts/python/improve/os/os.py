import os

# os 模块（操作系统接口）
# 1. 路径与环境
#
# os.getcwd() 当前目录 / os.chdir(path) 切换
# os.environ 环境变量字典 → 用 os.environ.get("KEY", "默认值") 读（键不存在直接 [] 会 KeyError）
# os.getlogin() 登录名（无 tty 时可能报错），更稳的是 import getpass; getpass.getuser()
current_dir = os.getcwd() # 获取当前目录路径
user = os.environ.get("USER") or os.environ.get("USERNAME", "unknown") # 获取用户名 并 设置默认值
home = os.environ.get("HOMEPATH") # Linux下是 HOME，Windows下是 HOMEPATH
print(f"当前目录: {current_dir}")
print(f"登录用户名: {user}")
print(f"家目录: {home}")


print("\n")


# 2. 路径工具 os.path（重点，高频）
# os.path.join("logs", "app.log")   # 跨平台拼接 → logs/app.log 或 logs\app.log
# os.path.abspath(".")              # 绝对路径 .表示当前目录 ，..表示上一级目录
# os.path.exists(p) / isdir / isfile
# os.path.basename("/var/log/x.log")  # x.log
# os.path.dirname("/var/log/x.log")   # /var/log
# os.path.splitext("x.log")           # ('x', '.log')
# os.path.getsize(p)                  # 字节数
p = os.path.join("logs", "app.log") # 拼接路径
status = os.path.exists(p) # 路径是否存在，返回 True/False

abs_path = os.path.abspath(".") # 获取当前目录的绝对路径
abs_path2 = os.path.abspath("..") # 获取上一级目录的绝对路径

basename = os.path.basename(p) # 获取路径的.basename，即文件名
dirname = os.path.dirname(p) # 获取路径的.dirname，即目录名
ext = os.path.splitext(p) # 获取路径的扩展名

current_file=os.getcwd()
size = os.path.getsize(current_file + "\\os.py") # 获取文件大小，以字节为单位


print(f"拼接后的路径: {p}")
print(f"路径 {p} 存在: {status}")
print(f"当前目录的绝对路径: {abs_path}")
print(f"上一级目录的绝对路径: {abs_path2}")
print(f"路径 {p} 的文件名: {basename}")
print(f"路径 {p} 的目录名: {dirname}")
print(f"路径 {p} 的扩展名: {ext[1]}") # 返回元组 ext[0] -> logs\app，ext[1] -> .log 是扩展名
print(f"路径 {current_file + '\\os.py'} 的大小: {size} 字节") # 获取文件大小，以字节为单位




# 3. 目录与文件操作
#
# os.listdir(d) 列出目录
# os.walk(d) 递归遍历（返回 (当前目录, 子目录列表, 文件列表)）
# os.makedirs(p, exist_ok=True) 建多层目录（exist_ok=True 避免已存在报错）
# os.remove / os.rename

