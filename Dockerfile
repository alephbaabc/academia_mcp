FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including git and graphics libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_ROOT_USER_ACTION=ignore
ENV GIT_PYTHON_REFRESH=quiet

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy repository files
COPY . .

# Install dependencies
RUN uv sync

EXPOSE 10000

# Directly launch academia_mcp on Render's required port using streamable-http
CMD ["uv", "run", "python", "-m", "academia_mcp", "--transport", "streamable-http", "--port", "10000"]
