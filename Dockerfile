FROM python:3.12-bookworm AS build

# install make
RUN apt-get update && apt-get install -y make

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG BUILD_ENV=local

WORKDIR /app

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for container logging
ENV PYTHONUNBUFFERED=1

# Copy only the necessary files for dependency installation first
COPY ./Makefile ./
COPY ./requirements/${BUILD_ENV}.txt ./requirements/

# Install dependencies
RUN make install ENV=${BUILD_ENV}


FROM python:3.12-slim AS local

WORKDIR /app

COPY --from=build /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

# No source code is needed to be in the container since it uses the volume for the source code.
# See docker-compose.debug.yml services.app.volumes

EXPOSE 8000

# For GHA like test, lint, types
FROM python:3.12-slim AS action
WORKDIR /app

COPY --from=build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY ./across_server ./across_server
COPY ./Makefile ./


FROM python:3.12-slim AS deploy
WORKDIR /app

COPY --from=build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY ./across_server ./across_server

# Copy files needed for migrations
COPY ./alembic.ini ./
COPY ./migrations/ ./migrations/

EXPOSE 8000

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# Create a non-root user with a UID of 5678 and no password, then change ownership of /app
RUN useradd -m -u 5678 appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "across_server.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "54.146.107.154"]
