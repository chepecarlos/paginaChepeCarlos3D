FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir \
    "invoke>=2.2.0" \
    "livereload>=2.7.1" \
    "pelican[markdown]>=4.11.0.post0"

COPY . .

ARG SITEURL=
ARG INSTAGRAM_SYNC=0

# Build static output for production. Instagram sync is optional to avoid flaky builds.
RUN set -eux; \
    if [ "$INSTAGRAM_SYNC" = "1" ]; then \
        python scripts/sync_instagram_feed.py; \
    fi; \
    SITEURL="$SITEURL" pelican content -o output -s publishconf.py

FROM nginx:1.27-alpine

COPY --from=builder /app/output /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/index.html >/dev/null || exit 1
