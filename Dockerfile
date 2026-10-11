FROM python:3.11-slim

WORKDIR /app

# Suppress the root user warning from pip
ENV PIP_ROOT_USER_ACTION=ignore

# Install the uv package manager
RUN pip install --no-cache-dir uv

# Copy repository files
COPY . .

# Install dependencies
RUN uv sync

# Expose Render's standard web port
EXPOSE 10000

# Start Academix in SSE transport mode on port 10000
CMD ["uv", "run", "academix", "--transport", "sse", "--port", "10000"]
