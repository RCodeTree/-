from datetime import datetime, timedelta, date, timezone
import time

# strftime = format（对象→字符串），strptime = parse（字符串→对象）；
# 时间戳互转：time.time() → datetime.fromtimestamp(ts)；datetime.timestamp()；
# ⚠️ 时区：now() 是 naive（无时区）；跨时区/存库要转 aware（zoneinfo 的 ZoneInfo）。

# datetime.now()	取当前时间	无 → datetime
# now.strftime(fmt)	格式化/序列化（时间→文本）	datetime → str
# datetime.strptime(s, fmt)	解析/反序列化（文本→时间）	str → datetime
# now + timedelta(...)	日期运算	datetime → datetime

now = datetime.now()  # 当前时间
print(now)
print(now.strftime("%Y-%m-%d %H:%M:%S"))  # 格式化输出 对象 -> 字符串(序列化)
print(datetime.strptime("2026-10-18", "%Y-%m-%d"))  # 解析字符串 字符串 -> 对象(反序列化)
print(now + timedelta(days=30))  # 日期加减

print("\n")


from datetime import datetime
ts = time.time() # 获取时间戳
print("时间戳转换到当前时间：" + datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"))
print(datetime.now().timestamp())



