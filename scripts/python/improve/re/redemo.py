# re 正则，从日志里提取结构化字段

import re

# re 核心函数
# re.search(p, s)	找第一个匹配，返回 Match
# re.match(p, s)	只从开头匹配
# re.findall(p, s)	返回全部匹配
# re.sub(p, repl, s)	替换
# re.split(p, s)	按正则切分
# re.compile(p)	预编译，重复使用更快

# 常用元字符
# \d 数字   \w 字母数字下划线   \s 空白   . 任意字符
# * 0+次    + 1+次    ? 0或1次    {n} {m,n} 次数
# [] 字符集  () 分组  ^ 开头  $ 结尾  | 或  \b 词边界

# 分组（本课重点）
# (...) 捕获分组；(?P<名字>...) 命名分组 → m.groupdict() 直接变字典，日志解析最爱
# 贪婪 vs 非贪婪：.* 尽量多吃，.*? 尽量少吃（提取字段时默认用非贪婪，否则会“吃过头”）

# demo
log = '127.0.0.1 - - [18/Oct/2026:10:22:01 +0800] "GET /api/v1 HTTP/1.1" 502 4321 0.031'
pat = (r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s.*?'
       r'"(?P<method>\w+) (?P<path>\S+) .*?"\s(?P<status>\d+)\s(?P<size>\d+)')
m = re.search(pat, log)
print(m.groupdict())  # {'ip':'127.0.0.1','method':'GET','path':'/api/v1','status':'502','size':'4321'}

print("\n")

line = 'password=MyS3cret123'
print(re.sub(r'(password=).*', r'\1***', line))  # password=***

print("\n")

# findall 提取所有 IP 并去重
text = "node1 10.0.0.5 node2 10.0.0.8 node1 10.0.0.5"
ips = sorted(set(re.findall(r'\d+\.\d+\.\d+\.\d+', text)))
print(ips)  # ['10.0.0.5', '10.0.0.8']

print("\n")

# 提取 5xx 错误码
for line in ['GET / 502', 'GET / 200', 'POST /x 504']:
    m = re.search(r'\b(50\d)\b', line) # \b 不匹配字符，它匹配一个位置：这个位置的一边是"单词字符"（\w：字母、数字、下划线），另一边不是单词字符（空格、标点、行首行尾等）
    if m:
        print("5xx 错误:", m.group())
