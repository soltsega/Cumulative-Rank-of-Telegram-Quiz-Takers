# Dockerfile for Arat Kilo Gibi Gubae Quiz System
FROM python:3.11-slim

LABEL maintainer="Solomon Tsega <tsegasolomon538@gmail.com>"
LABEL description="Arat Kilo Gibi Gubae Quiz Mastery System"
LABEL version="1.2.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p data docs logs \
    && chmod 755 data docs logs

# Create non-root user for security
RUN groupadd -r quizuser && useradd -r -g quizuser quizuser \
    && chown -R quizuser:quizuser /app

# Switch to non-root user
USER quizuser

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["python", "scripts/main.py"]
