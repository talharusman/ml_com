# Docker image for sandboxed submission execution
FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    pandas==2.1.3 \
    numpy==1.26.2 \
    scikit-learn==1.3.2

# Create submission directory
RUN mkdir -p /submissions

# Set working directory
WORKDIR /submissions

# Default command
CMD ["python3"]
