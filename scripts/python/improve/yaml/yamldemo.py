# yaml 用于人写配置（Docker Compose、K8s 清单、CI 文件，可读性好、支持注释）

import yaml

# yaml.safe_dump(obj, f, allow_unicode=True)
# cfg = yaml.safe_load(text)      # ✅ 只认数据，安全

"""
⚠️ 安全红线：永远 safe_load，禁用 yaml.load()。
旧版 yaml.load 可反序列化成任意 Python 对象，恶意 YAML 能触发任意代码执行（同类问题你在 subprocess 和 pathlib 已接触过，是贯穿全程的主线）。
"""