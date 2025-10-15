FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for LLM providers
# These should be provided at runtime via docker-compose or environment
# ENV OPENAI_API_KEY=""
# ENV ANTHROPIC_API_KEY=""

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/

# Create necessary directories
RUN mkdir -p logs reports

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV FUSEKI_ENDPOINT=http://fuseki:3030/ds

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "src/gateway/main.py"]
