FROM python:3.11.9-slim-bookworm as python-base

# Python configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    # Poetry configuration
    POETRY_VERSION=2.0.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VENV="/opt/poetry-venv" \
    POETRY_CACHE_DIR="/opt/.cache" \
    # Runtime configuration
    VENV_PATH="/opt/venv" \
    APP_PATH="/app"

# Prepend poetry and venv to path
ENV PATH="$POETRY_VENV/bin:$VENV_PATH/bin:$PATH"

################################
# BUILDER BASE
################################
FROM python-base as builder-base
RUN apt-get update && \
    apt-get install -y \
    curl \
    build-essential

# Install poetry
RUN python -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION} poetry-plugin-export

# Create a virtual environment
RUN python -m venv $VENV_PATH

# Set working directory
WORKDIR $APP_PATH

# Copy project dependency files
COPY pyproject.toml poetry.lock ./

# Install runtime dependencies
RUN poetry export --without-hashes --without dev -f requirements.txt | $VENV_PATH/bin/pip install -r /dev/stdin

################################
# Development
################################
FROM builder-base as dev

# Install dev dependencies
RUN poetry install --no-root

# Copy application code
COPY . .

# Set entrypoint
CMD ["poetry", "run", "python", "-m", "src.main"]

################################
# Production
################################
FROM python-base as prod

# Copy virtual environment from builder
COPY --from=builder-base $VENV_PATH $VENV_PATH

# Make sure we use the virtualenv
ENV PATH="$VENV_PATH/bin:$PATH"

# Copy application code
WORKDIR $APP_PATH
COPY . .

# Create and switch to non-root user
RUN useradd --create-home appuser && \
    chown -R appuser:appuser $APP_PATH
USER appuser

# Set entrypoint
#CMD ["python", "-m", "src.main"]
CMD ["sh", "-c", "uvicorn src.main:app --host $HOST --port $PORT --workers $WORKER_COUNT"]