from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# 自定义中间件定义 --- 继承 BaseHTTPMiddleware 类并实现 dispatch 方法
class MiddlewareCore(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        print("中间件2执行前")
        response = await call_next(request)
        print("中间件2执行后")
        return response
