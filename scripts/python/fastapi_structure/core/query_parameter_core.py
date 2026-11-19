"""编写一个通用参数函数，使用 FastApi 的依赖注入"""
def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}
