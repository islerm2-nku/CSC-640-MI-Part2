# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH (installer places binary in ~/.local/bin)
ENV PATH="/root/.local/bin:/root/.cargo/bin:$PATH"

# quick check to make failures visible during build
RUN uv --version
# Copy application code FIRST (needed for editable install)
COPY ./app /app
# Install all dependencies using uv
RUN uv pip install --system \
    fastapi>=0.104.1 \
    "uvicorn[standard]>=0.24.0" \
    python-multipart>=0.0.6 \
    mysql-connector-python>=8.2.0 \
    pymysql>=1.1.0 \
    sqlalchemy>=2.0.23 \
    "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.4" \
    python-dotenv>=1.0.0 \
    authlib>=1.3.0 \
    itsdangerous>=2.1.2 \
    httpx>=0.25.2 \
    requests>=2.31.0 \ 
    pydantic>=2.5.2 \
    pydantic-settings>=2.1.0 \
    email-validator>=2.1.0 \
    pytest>=7.4.3 \
    pytest-asyncio>=0.21.1 \
    pytest-cov>=4.1.0 \
    debugpy>=1.8.0 \
    pyirsdk>=1.3.5

# Copy application code
COPY ./app /app

# Create necessary directories
RUN mkdir -p /var/log/app && \
    chmod -R 755 /var/log

# Expose ports
EXPOSE 80
EXPOSE 5678

# Start uvicorn with debugpy for remote debugging
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
