# subprocess 执行系统命令

# r = subprocess.run(
#     ["命令", "参数1", "参数2"],   # 列表！不要 shell 字符串
#     capture_output=True,          # 捕获 stdout + stderr
#     text=True,                    # 输出为 str（否则是 bytes）
#     check=True,                   # 非 0 退出码 → 抛异常
#     timeout=10,                   # 超时秒数 → 抛异常
# )                                 # shell 默认 False，保持 False！

# shell=True + 字符串拼接 = 命令注入漏洞


"""
subprocess.run(..., env=env) 的 env 参数有个坑：
    一旦传入 env，子进程就「完全」使用你给的这份环境，不会自动和父进程合并
    子进程里就没有 PATH、HOME、SYSTEMROOT 等一堆变量了，结果可能是：
        Linux/macOS：找不到命令、动态库加载失败；
        Windows：subprocess 直接报 [WinError 87] 参数错误 或者程序起不来（因为丢了 SYSTEMROOT 等）。
    所以正确的写法就是先 {**os.environ, ...} 打底，再覆盖自己需要的变量 —— 这正是你这段代码在做的。

-c 是 Python 解释器的命令行选项
    意思是 command：让 Python 把后面那串字符串当成一段脚本源码直接执行，而不是从文件里读。

import subprocess, os
env = {**os.environ, "MY_APP_ENV": "staging"}   # 基于现有环境增量添加    ** 是解包操作符
r = subprocess.run([sys.executable, "-c", "import os; print(os.environ['MY_APP_ENV'])"],
                   capture_output=True, text=True, env=env)
print(r.stdout)
"""