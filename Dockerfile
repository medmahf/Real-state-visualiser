# ---------- build du front ----------
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---------- runtime backend ----------
FROM python:3.12-slim
WORKDIR /app

RUN useradd --create-home --uid 1000 app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app backend/ ./backend/
COPY --from=frontend --chown=app:app /app/frontend/dist ./backend/app/static

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
