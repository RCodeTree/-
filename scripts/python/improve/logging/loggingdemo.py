import logging

# 标准库 logging，学会**级别、格式、输出目标（handler）**三件事，养成生产级日志习惯

# DEBUG(10) < INFO(20) < WARNING(30) < ERROR(40) < CRITICAL(50)

# Logger 最佳实践
# 每个模块用 logger = logging.getLogger(__name__)，按模块名分层；
# 库代码不要调 basicConfig（那是使用者的事），只发日志；
# 记录异常堆栈用 logger.exception(...)（必须在 except 块内）。
# 库代码里没有出现任何 basicConfig / setLevel，但日志照样按应用的配置输出——因为库的 logger 默认 propagate=True，会向上冒泡到根 logger 的 handler。


# 根配置，影响所有 logger
logging.basicConfig(
    level=logging.INFO,  # 级别门槛
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(),  # 控制台
              logging.FileHandler("app.log")],  # 文件
)

# 模块级配置，影响当前模块(假设，如果为模块，必须使用logging.getLogger(__name__)，以便按模块名分层)
logging.info("服务启动")
logging.warning("磁盘使用率 82%")
logging.error("连接数据库失败")
