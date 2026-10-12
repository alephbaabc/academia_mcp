FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_ROOT_USER_ACTION=ignore
ENV GIT_PYTHON_REFRESH=quiet

RUN pip install --no-cache-dir uv

COPY . .

RUN uv sync

EXPOSE 10000

# Use native SSE transport which Gemini's web validator expects
CMD ["uv", "run", "python", "-m", "academia_mcp", "--transport", "sse", "--port", "10000"]