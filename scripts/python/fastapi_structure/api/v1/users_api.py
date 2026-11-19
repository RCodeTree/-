"""用户模块路由分层"""
import mimetypes
import os.path
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Form
from fastapi.params import Query, Path
from fastapi.responses import HTMLResponse
from multipart import file_path
from starlette.responses import FileResponse, StreamingResponse, RedirectResponse

from schema.users_schema import User
from schema.Form_schema import FormData

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/{id}")  # 路径参数，获取用户ID
def get_users(id: int = Path(..., description="用户ID", gt=0)):
    return {"users(路径参数)": "This is a user", "id": id}


@router.get("/me")  # 查询参数，获取用户ID
def get_users(id: int = Query(..., description="用户ID", gt=0)):
    return {"users(查询参数)": "This is a user", "id": id}


@router.post("/me", response_model=User)
def get_users(user: User):
    return user  # FastAPI 的特性，自动将请求体中的数据转换为 User 模型，自动转为 JSON


@router.post("/me")  # 表单参数 对应 前端form表单提交
def get_users(form_data: Annotated[FormData, Form()]):
    return form_data


@router.get("/htmltype", response_class=HTMLResponse)  # 返回以 HTML 格式响应(默认响应格式为 JSON)
def get_html():
    return """
    <html>
        <body>
            <form action="/users/html" method="post">
                <input type="text" name="username">
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """


@router.get("/filetype")  # 返回以文件形式响应
def get_file():
    return FileResponse("./demo.png")


@router.get("/stream-file-type")  # 返回以流形式响应
async def get_stream_file():
    file_path = ""  # 流式文件路径(如：视频、音频)
    media_type, _ = mimetypes.guess_type(file_path)  # 获取文件的媒体类型

    def iterfile():
        with open(file_path, "rb") as file_like:
            # 读取文件并逐块读取，每次读取 1MB，然后 yield 出去
            while chunk := file_like.read(1024 * 1024):  # := 是 python 3.8 引入的赋值表达式，用于在表达式中进行赋值，避免了额外的赋值语句
                yield chunk  # yield 是 python 中用来定义生成器的关键字，它可以让函数“暂停”并“记住”当前的执行状态，下次调用时从暂停的地方继续执行

    filename = quote(os.path.basename(file_path))  # 获取文件名并进行 URL 编码
    return StreamingResponse(
        iterfile(),
        media_type=media_type or "application/octet-stream",
        filename=filename
    )

@router.get("/redirecttype") # 重定向响应
def get_redirect():
    return RedirectResponse(url="https://baidu.com")
