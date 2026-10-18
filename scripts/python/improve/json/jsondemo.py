import json

# json 用于程序/API 之间交换数据（结构化、严格、无注释）
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
#  json 落盘与读回 把 {"app": "collector", "interval": 30, "enable": True} 写入 config.json（ensure_ascii=False, indent=2），再读回打印 interval。

def main():
    Dict = {"app": "collector", "interval": 30, "enable": True}
    with open("../../practice/test.json", "w", encoding="utf-8") as f:
        json.dump(Dict, f, ensure_ascii=False, indent=2) # 序列化到文件中(写到文件中) 字典对象 --> 文件
    with open("../../practice/test.json", "r", encoding="utf-8") as f:
        result = json.load(f) # 反序列化到对象(读取到程序中) 文件 ---> 字典对象
        print(result["interval"])
    pass


if __name__ == "__main__":
    main()
