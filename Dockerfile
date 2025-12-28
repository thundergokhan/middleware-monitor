# Base Image: Python 3.9 Slim (Lightweight, Production Ready)
FROM python:3.9-slim

# Working Directory
WORKDIR /app

# Install System Dependencies (Minimal)
# curl/wget might be needed for healthchecks if we add them later
# RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy Requirements first (Docker Cache Optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
COPY . .

# Expose Web Port
EXPOSE 5000

# Entrypoint: Run in Web Mode by default
CMD ["python", "-m", "src.main", "--web"]
