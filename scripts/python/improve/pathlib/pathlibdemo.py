from pathlib import Path

# 面向对象的 pathlib 替代字符串拼路径，用 shutil 完成复制、打包、磁盘巡检。这是采集器/日志清理/备份脚本的底层能力。

# Path(".")          # 相对
# Path.cwd()         # 当前目录（= os.getcwd()）
# Path.home()        # 家目录
# Path("/var/log")   # 绝对（Windows 会自动适配盘符）

# 路径属性
# p = Path.home() / "logs" / "app.log"
# p.name      # app.log
# p.stem      # app          （去后缀）
# p.suffix    # .log
# p.parent    # ~/logs
# p.parts     # 各层元组
# p.absolute()
# p.resolve() # 绝对路径 + 解析软链接


