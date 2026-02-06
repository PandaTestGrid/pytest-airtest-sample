# Airtest容器环境Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    android-tools-adb \
    android-tools-fastboot \
    libopencv-dev \
    python3-opencv \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建报告目录
RUN mkdir -p reports/screenshots logs

# 默认命令
CMD ["python", "-m", "pytest", "--help"]