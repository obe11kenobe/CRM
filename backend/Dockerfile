FROM python:3.12-slim

WORKDIR /app/backend

RUN pip install uv

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

COPY backend/ .
COPY frontend/ /app/frontend/

CMD ["sh", "-c", "uv run python manage.py migrate --noinput && uv run python manage.py collectstatic --noinput && uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
