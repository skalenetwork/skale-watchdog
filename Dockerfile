FROM ubuntu:24.04 AS builder

ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHON_VERSION=3.13.8

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        libpcre2-dev \
    && rm -rf /var/lib/apt/lists/*

ENV UV_PYTHON_INSTALL_DIR=/opt/python \
    UV_PYTHON_PREFERENCE=only-managed

RUN uv python install "${PYTHON_VERSION}"

WORKDIR /app
COPY pyproject.toml ./
RUN uv venv /opt/venv --python "${PYTHON_VERSION}" && \
    uv pip install --python /opt/venv/bin/python --prerelease=allow --no-cache .


FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        libpcre2-8-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/python /opt/python
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONPATH="/app"

WORKDIR /app
COPY . .
RUN mkdir -p /app/healthspool

CMD ["uwsgi", "--ini", "uwsgi.ini"]
