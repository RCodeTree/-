import argparse

# 骨架
p = argparse.ArgumentParser(description="说明文字")
p.add_argument("path", help="位置参数：必填")          # 位置参数
p.add_argument("--host", default="127.0.0.1")          # 可选参数 + 默认值
p.add_argument("--port", type=int, default=8080)       # 类型转换
p.add_argument("-v", "--verbose", action="store_true") # 布尔开关（不带值）
args = p.parse_args()





