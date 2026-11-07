# 拉取基础运行环境
FROM python:3.14-slim

# 设置项目目录
WORKDIR /app

# 复制项目依赖文件
COPY requirements.txt .

# 根据依赖文件安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目源代码
COPY . .

# 设置容器启动固定启动的入口执行
ENTRYPOINT ["python3","main.py"]
