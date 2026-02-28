# 【核心修复 1】：精确锁定 Debian 12 (bookworm) 稳定版，彻底杜绝测试版 (trixie) 带来的包管理器崩溃
FROM python:3.10-slim-bookworm

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 【核心修复 2】：利用当地极佳的官方 CDN 直连优势，移除容易断流的第三方镜像，并加入容错重试机制
RUN apt-get clean && apt-get update --fix-missing || apt-get update \
    && apt-get install -y \
    wget gnupg libgconf-2-4 libxss1 libnss3 libasound2 fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 恢复 pip 的全球高速默认源
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps chromium

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]