FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including git and graphics libraries for OpenCV/OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Suppress warnings and configure git-python behavior
ENV PIP_ROOT_USER_ACTION=ignore
ENV GIT_PYTHON_REFRESH=quiet

# Install the uv package manager
RUN pip install --no-cache-dir uv

# Copy repository files including app.py wrapper
COPY . .

# Install dependencies
RUN uv sync

# Expose Render's standard web port
EXPOSE 10000

# Start the proxy wrapper script
CMD ["uv", "run", "python", "app.py"]