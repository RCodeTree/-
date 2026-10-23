import requests

# 异常类型：requests.Timeout、requests.ConnectionError、requests.HTTPError（raise_for_status 抛出）、基类 requests.RequestException。

# requests 核心三件套
# # GET：params 拼 query
# r = requests.get(url, params={"q": "python"}, timeout=5)
# # POST：json= 自动序列化 + 自动设 Content-Type
# r = requests.post(url, json={"a": 1}, headers={"Authorization": "Bearer x"}, timeout=5)
# # 取结果
# r.status_code          # 200
# r.json()               # 把响应体解析成 dict
# r.text                 # 原始文本
# r.raise_for_status()   # 4xx/5xx 抛 HTTPError，否则静默

# timeout=5                # 连接+读 都 5 秒
# timeout=(3.05, 10)       # (连接超时, 读超时) 分离
# 指数退避：每次等待 backoff * 2**(attempt-1) 秒，避免重试风暴

# GET 实例
# r = requests.get("https://httpbin.org/get", params={"per_page": 1}, timeout=5) # 发送 GET 请求 返回响应对象
# print(r.json())
# print(r.status_code) # 200
# print(r.json()["args"])

# POST 实例
# data = {"hostname": "web-01", "cpu": 42.5}
# try:
#     r = requests.post("https://httpbin.org/post", json=data, timeout=5)
#     r.raise_for_status()  # 不成功就抛异常
#     print(r.json())
#     print("上报成功:", r.json()["json"])  # httpbin 会回显 json
# except requests.HTTPError as e:
#     print("HTTP 错误:", e)
# except requests.Timeout:
#     print("超时")
# except requests.RequestException as e:
#     print("网络错误:", e)
