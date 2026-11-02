# Use Python 3.12 on a lightweight Debian base.
FROM docker.io/library/python:3.12-slim

# Python runtime configuration.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Application working directory.
WORKDIR /app

# Install Python dependencies.
COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

# Create an unprivileged application user.
RUN groupadd --system app \
    && useradd --system --gid app --create-home app

# Copy only the application and database code.
COPY --chown=app:app app/ ./app/
COPY --chown=app:app db/ ./db/

# Run as non-root.
USER app

# Flask application port.
EXPOSE 8000

# Start Flask through Gunicorn.
CMD ["gunicorn", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "2", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "app:create_app()"]