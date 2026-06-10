FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY services/web-app/requirements.txt ./requirements.txt

RUN pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    LOG_LEVEL=INFO

WORKDIR /app

RUN useradd --create-home appuser

COPY services/web-app/requirements.txt ./requirements.txt
COPY --from=builder /wheels /wheels

RUN pip install --root-user-action=ignore --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY services/web-app/app.py ./app.py
COPY services/web-app/templates ./templates
COPY services/web-app/static ./static

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('WEB_APP_PORT', '5000') + '/health', timeout=3).read()"

CMD ["python", "app.py"]
