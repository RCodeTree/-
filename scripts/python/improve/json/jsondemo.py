import json

# 序列化 = 对象 ↔ 文本
# 序列化（dump）：Python 对象 → 字符串/文件
# 反序列化（load）：字符串/文件 → Python 对象
# 目的：跨进程、跨服务、跨语言交换数据，或把配置落盘。

"""
# 字符串 ↔ 对象
json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)
json.loads(text)

# 文件 ↔ 对象
json.dump(obj, f, ...)   # 写文件
json.load(f)             # 读文件

ensure_ascii=False：中文不转 \\u 编码，可读；
indent=2：缩进美化。
类型映射：dict→object, list→array, str→string, int/float→number, True→true, None→null。
⚠️ 坑：datetime 对象不能直接 dumps，要先 str() 转字符串。
"""