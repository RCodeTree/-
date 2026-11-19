"""Form请求和响应数据模型"""

from pydantic import BaseModel


class FormData(BaseModel):
    username: str
    password: str
