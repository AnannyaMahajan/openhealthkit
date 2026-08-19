FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject & packages
COPY pyproject.toml .
COPY packages/openhealthkit packages/openhealthkit

# Install dependencies and package
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -e ./packages/openhealthkit[postgres]

# Copy configuration and scripts
COPY .env.example .env

EXPOSE 8000

CMD ["uvicorn", "openhealthkit.main:app", "--host", "0.0.0.0", "--port", "8000"]
