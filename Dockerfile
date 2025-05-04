FROM python:3.12

ENV PYTHONUNBUFFERED=1
WORKDIR /app/

# Способ 1: Установка uv через pip с зеркалом
RUN pip install uv==0.4.15 -i https://pypi.tuna.tsinghua.edu.cn/simple

# Способ 2: Копирование uv из официального образа (если pip не работает)
# COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /usr/local/bin/uv
# RUN chmod +x /usr/local/bin/uv

COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/
COPY ./scripts/ /app/scripts
COPY ./migrations/ /app/migrations
COPY ./app /app/app
ENV UV_HTTP_TIMEOUT=120
RUN uv sync
# RUN pip install --no-cache-dir -r pyproject.toml

CMD ["uv", "run", "app/main.py"]
