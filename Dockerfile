FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY . .

RUN uv sync --frozen --no-dev

CMD ["uv", "run", "python", "-m", "nerdearla_mcp.server"]