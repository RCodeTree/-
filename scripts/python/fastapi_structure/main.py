from fastapi import FastAPI

from api import router
from core.middleware_core import MiddlewareCore

app = FastAPI()


# 应用路由
@app.get("/")
async def read_root():
    return {"Hello": "World"}


app.include_router(router.api_router)

# 应用中间件
"""
中间件定义和设置
多个中间件的执行顺序：
当你使用 @app.middleware() 装饰器或 app.add_middleware() 方法添加多个中间件时，每个新中间件都会包裹应用，形成一个栈。最后添加的中间件是“最外层”的，最先添加的是“最内层”的。
在请求路径上，最外层的中间件先运行。
在响应路径上，它最后运行。

中间件函数会接收：

1. request。
2. 一个函数 call_next，它会把 request 作为参数接收。
    这个函数会把 request 传递给相应的路径操作。
    然后它返回由相应路径操作生成的 response。
"""


@app.middleware("http")
async def add_process_time_header(request, call_next):
    print("中间件1执行前")
    response = await call_next(request)
    print("中间件1执行后")
    return response


app.add_middleware(MiddlewareCore)
