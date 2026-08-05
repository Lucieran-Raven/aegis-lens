FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy pyproject.toml and source code
COPY pyproject.toml ./
COPY requirements.txt ./
COPY src/ ./src/
COPY app.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Set PYTHONPATH
ENV PYTHONPATH=/app/src

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Expose port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Switch to non-root user
USER appuser

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081"]
