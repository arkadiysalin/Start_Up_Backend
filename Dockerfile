FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Установка uv через pip (альтернатива копированию бинарника)
RUN pip install uv==0.4.15

# Добавляем uv в PATH (если нужно)
ENV PATH="/root/.local/bin:$PATH"

# Копируем зависимости
COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/
COPY ./scripts/ /app/scripts
COPY ./migrations/ /app/migrations
COPY ./app /app/app

# Синхронизируем зависимости через uv
RUN uv pip install -r pyproject.toml  # Или используйте `uv sync`, если у вас есть uv.lock

CMD ["uv", "run", "app/main.py"]
