FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv && \
    uv pip install -r pyproject.toml

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Activate venv and run the application
CMD [".venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

