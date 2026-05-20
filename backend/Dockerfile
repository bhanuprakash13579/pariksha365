FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (curl added for HEALTHCHECK)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Docker-native health check: Railway uses this to know when the container is
# truly ready before routing traffic. --start-period=5s gives uvicorn time to
# bind the port; after that we probe /health every 10s with a 5s timeout.
# Three consecutive failures = unhealthy (container is replaced, not just
# restarted with bad code). Without this, Railway probes immediately after
# container start and can mark the service unhealthy before uvicorn is ready.
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -fs http://localhost:${PORT:-8000}/health || exit 1

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --proxy-headers --forwarded-allow-ips '*'
