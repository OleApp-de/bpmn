# Build stage for better caching and smaller final image
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.9-slim

WORKDIR /app

# Install dumb-init for proper signal handling, curl for health checks, and graphviz for visualization
RUN apt-get update && apt-get install -y \
    dumb-init \
    curl \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application files
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Create Streamlit config directory and copy config
RUN mkdir -p /root/.streamlit
COPY .streamlit/config.toml /root/.streamlit/config.toml

# Keep as root user for simplicity in container environment
# (Docker containers are isolated anyway)

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start the Streamlit server
CMD ["streamlit", "run", "app.py"]