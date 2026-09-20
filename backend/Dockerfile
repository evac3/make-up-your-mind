# Shared base image for both backend services.
# Both the DB service and the AI Gateway use the same dependencies,
# so a single Dockerfile handles both — the CMD is overridden per service
# in docker-compose.yml.
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (cached layer unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full backend source
COPY . .

# Default: run the DB / analytics microservice on port 8001
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
