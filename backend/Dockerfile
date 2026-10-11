FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir uvicorn fastapi pydantic pydantic-settings sqlalchemy aiosqlite httpx greenlet structlog pytest pytest-asyncio

# Copy application source
COPY backend/app ./app
COPY backend/tests ./tests

ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite+aiosqlite:///./lenny_growth.db
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
