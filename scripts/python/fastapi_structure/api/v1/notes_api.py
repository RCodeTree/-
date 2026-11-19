"""笔记模块路由分层"""
from typing import Annotated

from fastapi import APIRouter
from fastapi import File
from fastapi import UploadFile
from fastapi.params import Form, Depends
from core.query_parameter_core import common_parameters

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/data")  # 依赖注入
def get_notes_data(query: Annotated[dict, Depends(common_parameters)]):
    return query  # 通过依赖注入，可以校验参数的同时，实现代码和参数的复用，直接返回参数数据，这里的query就是依赖注入的返回参数数据


@router.post("/data")  # 表单与文件请求
def create_notes(
        small_note: Annotated[bytes, File()],  # 整个文件一次性直接读进内存，适用于小文件
        large_note: Annotated[UploadFile, File()],  # 上传文件，适用于大文件，当文件较大时，超过内存限制时，会自动写入磁盘
        token: Annotated[str, Form()]
):
    return {
        "small_note": small_note,
        "large_note": large_note.filename,
        "token": token
    }
