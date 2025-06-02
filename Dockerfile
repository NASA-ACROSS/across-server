FROM python:3.12-bookworm AS build

# install make
RUN apt-get update && apt-get install -y make

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Configure SSH to use the forwarded agent
RUN echo "Host github.com\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null" >> /etc/ssh/ssh_config

ARG APP_ENV=local

WORKDIR /app

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for container logging
ENV PYTHONUNBUFFERED=1

# Copy only the necessary files for dependency installation first
COPY ./Makefile ./
COPY ./requirements/${APP_ENV}.txt ./requirements/

# Copy over the file holding the version for hatch build
COPY ./across_server/__about__.py ./across_server/

# Install dependencies
RUN --mount=type=ssh make install ENV=${APP_ENV}


FROM python:3.12-slim AS local

WORKDIR /app

COPY --from=build /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

# No source code is needed to be in the container since it uses the volume for the source code.
# See docker-compose.debug.yml services.app.volumes

EXPOSE 8000


FROM python:3.12-slim AS test
WORKDIR /app

COPY --from=build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY ../across_server ./across_server


FROM python:3.12-slim AS prod
WORKDIR /app

COPY --from=build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY ../across_server ./across_server

EXPOSE 8000

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# Create a non-root user with a UID of 5678 and no password, then change ownership of /app
RUN useradd -m -u 5678 appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "across_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
