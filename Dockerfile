# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the Python backend and serve
FROM python:3.12-slim
WORKDIR /app

# Install uv
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh && \
    apt-get clean

# Copy pyproject.toml and lock file
COPY backend/pyproject.toml backend/uv.lock ./
# Install dependencies using uv
RUN uv sync --frozen --no-dev --no-install-project

# Copy backend source code and tests
COPY backend/app/ ./app/
COPY backend/knowledge/ ./knowledge/
COPY backend/tests/ ./tests/

# Copy built frontend assets to a static folder that FastAPI will serve
COPY --from=frontend-builder /app/frontend/dist ./static

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
