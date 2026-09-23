# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1 — builder: install dependencies into an isolated virtualenv.
# Using the slim image keeps the attack surface small; the build tools that
# might be pulled in here never reach the final image.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Create the venv first so it caches independently of the source.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2 — runtime: minimal image, no build tools, runs as a non-root user.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Home points at a writable tmpfs so the image works with a
    # read-only root filesystem (readOnlyRootFilesystem: true).
    HOME=/tmp \
    PATH="/opt/venv/bin:$PATH"

# Drop OS packages we don't need and apply security updates.
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    # Create a dedicated, unprivileged user (uid/gid 10001).
    && groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

# Copy the pre-built virtualenv from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Copy source last (changes most often) and hand ownership to the app user.
COPY --chown=appuser:appuser . .

# Never run as root.
USER appuser

EXPOSE 8000

# Only the API server — database migrations run as a Kubernetes initContainer
# (see production-deployment.yaml), not on every container start.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
