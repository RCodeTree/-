"""用户请求和响应数据模型"""
from pydantic import Field

from pydantic import BaseModel


class User(BaseModel):
    id: int = Field(..., description="用户ID")
    name: str = Field(default=None, max_length=50, description="用户名")
