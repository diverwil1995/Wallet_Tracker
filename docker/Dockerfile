# 使用 Python 3.9 基礎鏡像
FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 設置環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.4.2

# 安裝系統依賴
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# 複製 Poetry 配置文件
COPY pyproject.toml poetry.lock ./

# 安裝依賴
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# 複製應用程序代碼
COPY . .

# 暴露端口
EXPOSE 8000

# 啟動應用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]