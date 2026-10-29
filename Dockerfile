FROM python:3.14.10-slim-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --python /usr/local/bin/python3.14


FROM python:3.14.10-slim-trixie

COPY --from=builder /app/.venv /app/.venv

WORKDIR /app
COPY *.py ./

USER 10001:10001

ENV PATH="/app/.venv/bin:$PATH"

CMD ["granian", "--interface", "wsgi", "--host", "127.0.0.1", "--port", "3010", \
     "--workers", "1", "--blocking-threads", "4", "main:app"]
