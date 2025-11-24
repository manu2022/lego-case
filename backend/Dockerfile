FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv && \
    uv pip install -r pyproject.toml

# Copy application code
COPY . .

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Activate venv and run the application
CMD [".venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

