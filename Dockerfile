FROM python:3.14-slim-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /usr/local/bin/uv

ENV UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --python /usr/local/bin/python3.14


FROM python:3.14-slim-trixie

COPY --from=builder /app/.venv /app/.venv

WORKDIR /app
COPY . .

RUN useradd -r -u 10001 -M watchdog
USER watchdog

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1

CMD ["granian", "--interface", "wsgi", "--host", "127.0.0.1", "--port", "3010", \
     "--workers", "1", "--blocking-threads", "4", "main:app"]
