# subprocess 执行系统命令

# r = subprocess.run(
#     ["命令", "参数1", "参数2"],   # 列表！不要 shell 字符串
#     capture_output=True,          # 捕获 stdout + stderr
#     text=True,                    # 输出为 str（否则是 bytes）
#     check=True,                   # 非 0 退出码 → 抛异常
#     timeout=10,                   # 超时秒数 → 抛异常
# )                                 # shell 默认 False，保持 False！

# shell=True + 字符串拼接 = 命令注入漏洞
