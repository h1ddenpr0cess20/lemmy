FROM python:3.11-slim

# Avoid interactive prompts and keep image lean
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /lemmy

# System deps for SSL and timezones (for tools making HTTPS calls)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata first for better caching
COPY pyproject.toml README.md LICENSE /lemmy/
COPY lemmy /lemmy/lemmy
COPY lemmy.py /lemmy/lemmy.py
COPY config.json /lemmy/config.json
COPY help.txt /lemmy/help.txt

# Install the package
RUN pip install --no-cache-dir .

# Use a non-root user for safety
RUN useradd -m -u 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Default to working with LM Studio at localhost:1234
# You can override with: docker run -it <img> --api-base http://host.docker.internal:11434

ENTRYPOINT ["lemmy"]
CMD []
