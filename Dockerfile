# ═══════════════════════════════════
# FILE: Dockerfile
# PURPOSE: Multi-stage Docker image with Python 3.11, Node 20, and FFmpeg
# ═══════════════════════════════════

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies: Node.js 20, FFmpeg, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    ffmpeg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify installations
RUN python --version && node --version && npm --version && ffmpeg -version | head -1

WORKDIR /app

# ── Python dependencies ──────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Remotion (Node.js) dependencies ──────
COPY remotion/package.json remotion/package-lock.json* remotion/
RUN cd remotion && npm install --production

# ── Copy application code ────────────────
COPY . .

# ── Create data directories ──────────────
RUN mkdir -p data/scraped_ads data/analysis data/scripts data/videos/audio \
    company_data logs

EXPOSE 8000

# Default: run the FastAPI server
CMD ["python", "main.py", "--mode", "api", "--host", "0.0.0.0", "--port", "8000"]
