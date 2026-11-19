"""Cookie和Header模块路由分层"""
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi import Cookie, Header
from fastapi.params import Path

from schema.Cookie_schema import cookie
from schema.Header_schema import header

router = APIRouter(prefix="/verify", tags=["verify"])


@router.get("/mycookie")  # 获取Cookie
def get_cookie(mycookie: Annotated[cookie, Cookie()] = None):
    return {
        "cookie": f"{mycookie.session_id}",
        "fatebook_tracker": f"{mycookie.fatebook_tracker}",
        "googall_tracker": f"{mycookie.googall_tracker}"
    }


@router.get("/myheader")  # 获取Header
def get_header(myheader: Annotated[header, Header(convert_underscores=False)] = None):
    return {
        "header": f"{myheader.host}",
        "save_data": f"{myheader.save_data}",
        "if_modified_since": f"{myheader.if_modified_since}",
        "traceparent": f"{myheader.traceparent}",
        "x_tag": f"{myheader.x_tag}"
    }


@router.get("/except/{id}") # HTTPException 异常处理和响应设置
def get_except(id: int):
    if id <= 0:
        raise HTTPException(status_code=400, detail="id 必须大于0")
    return {"id": id}
