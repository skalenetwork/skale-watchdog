FROM python:3.13.8-slim-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpcre2-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir app
WORKDIR /app

COPY pyproject.toml ./
RUN uv pip install --prerelease=allow --system --no-cache .


FROM python:3.13.8-slim-trixie

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY . .

RUN mkdir -p /app/healthspool

ENV PYTHONPATH="/app"
CMD ["uwsgi", "--ini", "uwsgi.ini"]
