FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_FROZEN=1 \
    UV_NO_DEV=1

WORKDIR /app

# Instala dependencias desde el lockfile (capa cacheable, separada del codigo).
# --frozen hace que el build falle si pyproject.toml y uv.lock estan
# desincronizados, en vez de instalar de menos en silencio.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

ARG SITEURL=
ARG INSTAGRAM_SYNC=0

# Build static output for production. Instagram sync is optional to avoid flaky builds.
RUN set -eux; \
    if [ "$INSTAGRAM_SYNC" = "1" ]; then \
        uv run python scripts/sync_instagram_feed.py; \
    fi; \
    SITEURL="$SITEURL" uv run pelican content -o output -s publishconf.py

FROM nginx:1.27-alpine

COPY --from=builder /app/output /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/index.html >/dev/null || exit 1
