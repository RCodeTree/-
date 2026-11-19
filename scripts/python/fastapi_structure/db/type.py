"""MySQL 专用列类型：无符号 BIGINT（与库表主键/外键一致）。"""
from sqlalchemy.dialects.mysql import BIGINT

UnsignedBigInt = BIGINT(unsigned=True)
