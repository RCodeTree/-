"""Header请求和响应数据模型"""
from pydantic import BaseModel, Field


class header(BaseModel):
    host: str = Field(default=None, alias="Host")
    save_data: bool = Field(default=None, alias="Save-Data")
    if_modified_since: str | None = Field(default=None, alias="If-Modified-Since")
    traceparent: str | None = Field(default=None, alias="Traceparent")
    x_tag: list[str] = Field(alias="X-Tag")
