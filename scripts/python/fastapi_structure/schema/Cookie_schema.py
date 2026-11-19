"""Cookie请求和响应数据模型"""
from pydantic import BaseModel


class cookie(BaseModel):
    model_config = {"extra": "forbid"}  # 禁止额外字段

    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None
