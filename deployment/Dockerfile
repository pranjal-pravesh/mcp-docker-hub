# Dockerfile for MCP Hub Server
FROM python:3.11-slim

# Install system dependencies including Docker
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    docker.io \
    docker-compose \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create logs directory
RUN mkdir -p logs

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Add appuser to docker group and set proper permissions
RUN usermod -aG docker appuser && \
    chown -R appuser:appuser /app && \
    chmod 666 /var/run/docker.sock || true

# Switch to appuser
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start the application
CMD ["./start.sh"] 