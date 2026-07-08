# Start from an official, minimal image that already has Python 3.12 installed
FROM python:3.12-slim

# Create (and move into) a folder called /app inside the container —
# everything below this happens relative to /app
WORKDIR /app

# Copy the uv tool itself from its official image into this container's /bin folder,
# so we can use the "uv" command below
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy only the dependency files first (not the rest of the code yet) —
# this lets Docker reuse this step later if only your code changes, not your dependencies
COPY pyproject.toml uv.lock ./

# Install the exact dependency versions locked in uv.lock
# --frozen = don't recalculate versions, use exactly what's locked
# --no-cache = don't keep temporary download files, keeps the image smaller
RUN uv sync --frozen --no-cache

# Now copy the rest of your project files (main.py, etc.) into the container
COPY . .

# Document that this container listens on port 8000 (informational)
EXPOSE 8000

# The command that runs when the container starts:
# launches the FastAPI app with uvicorn, accepting connections from outside the container
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]