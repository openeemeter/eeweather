# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:0.13.0@sha256:cdc6093146eb3ff6a40107b38f008b789e050e77ad87865e381d9917da55a168 AS uv
FROM python:3.14-slim AS app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# uv (fast installer) from the digest-pinned stage above
COPY --from=uv /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# deps layer (cacheable): install the locked dependencies only; the build fails
# if uv.lock is out of date with pyproject.toml
COPY pyproject.toml README.md LICENSE uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv export --locked --no-emit-project --extra dev -o /tmp/requirements.txt && \
    uv pip install --system -r /tmp/requirements.txt

COPY eeweather/ /app/eeweather
RUN uv pip install --system --no-deps -e /app

# Run as an unprivileged user whose UID matches the host user that bind-mounts the
# repository, so files written into the mount stay writable on both sides
ARG UID=1000
RUN useradd --uid ${UID} --create-home --shell /bin/sh app
ENV UV_CACHE_DIR=/home/app/.cache/uv
USER app
