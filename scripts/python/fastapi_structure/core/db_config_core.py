"""MySQL 数据库连接与 Session 配置"""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# 数据库连接信息（请按本地 MySQL 实际情况修改）
MYSQL_USER = "root"
MYSQL_PASSWORD = "你的密码"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DB = "fastapi_demo"  # 与 data.sql 中的库名保持一致

# 使用 pymysql 作为驱动，charset 指定为 utf8mb4
DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
)

# 数据库引擎：负责维护连接池，并把 SQL 真正发到 MySQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 每次取连接前先 ping，避免拿到已失效的连接
    pool_recycle=3600,   # 连接空闲超过 1 小时后回收，避免 MySQL 端主动断开
    echo=False,          # 置为 True 可在控制台打印实际执行的 SQL，方便调试
)

# 会话工厂：每个请求从这里新建一个独立 Session
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Iterator[Session]:
    """FastAPI 依赖：为每个请求创建独立 Session，请求结束后自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
