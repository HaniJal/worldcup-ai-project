FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

# Install to system Python - not affected by volume mounts
RUN uv pip install --system -r pyproject.toml 2>/dev/null || \
    uv sync --frozen --no-cache --system

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]