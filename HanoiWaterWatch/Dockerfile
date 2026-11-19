FROM node:22-bookworm-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
COPY shared/registry/ /build/shared/registry/
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt && useradd --create-home --uid 10001 hww
COPY backend/ ./backend/
COPY shared/ ./shared/
COPY --from=frontend /build/frontend/dist ./frontend/dist
ENV PYTHONPATH=/app/backend FRONTEND_DIST=/app/frontend/dist
RUN mkdir -p /app/.local && chown -R hww:hww /app
USER hww
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=3)"
CMD ["sh", "-c", "cd /app/backend && alembic upgrade head && python -m app.cli seed && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --workers 1"]

