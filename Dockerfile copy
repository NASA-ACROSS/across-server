FROM ghcr.io/prefix-dev/pixi:0.29.0 AS build

ARG APP_ENV=local

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN echo ${APP_ENV}

WORKDIR /app

# Copy only the necessary files for dependency installation first
COPY pyproject.toml ./
COPY pixi.lock ./

# Copy over the file holding the version for hatch build
COPY across_server/__about__.py ./across_server/

RUN pixi install -e ${APP_ENV} --locked

RUN pixi shell-hook -s bash -e ${APP_ENV} > /shell-hook
RUN echo "#!/bin/bash" > /app/entrypoint.sh
RUN cat /shell-hook >> /app/entrypoint.sh
RUN echo 'exec "$@"' >> /app/entrypoint.sh

FROM ubuntu:24.04 AS local
WORKDIR /app

COPY --from=build /app/.pixi/envs/local /app/.pixi/envs/local
COPY --from=build --chmod=0755 /app/entrypoint.sh /app/entrypoint.sh

# No source code is needed to be in the container since it uses the volume for the source code.
# See docker-compose.debug.yml services.app.volumes

EXPOSE 8000

# from pixi shell-hook
ENV PATH=/app/.pixi/envs/local/bin:$PATH
ENV CONDA_PREFIX=/app/.pixi/envs/local

ENTRYPOINT [ "/app/entrypoint.sh" ]

CMD [ "fastapi", "dev", "across_server/main.py", "--host", "0.0.0.0", "--port", "8000"]


FROM debian:bookworm-slim AS test
WORKDIR /app
COPY --from=build /app/.pixi/envs/test /app/.pixi/envs/test

# Copy source code
COPY ./across_server ./across_server

# from pixi shell-hook
ENV PATH=/app/.pixi/envs/test/bin:$PATH
ENV CONDA_PREFIX=/app/.pixi/envs/test

FROM debian:bookworm-slim AS production
WORKDIR /app
COPY --from=build /app/.pixi/envs/production /app/.pixi/envs/production

# Copy source code
COPY ./across_server ./across_server

EXPOSE 8000

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# Create a non-root user with a UID of 5678 and no password, then change ownership of /app
RUN useradd -m -u 5678 appuser && chown -R appuser /app
USER appuser

# from pixi shell-hook
ENV PATH=/app/.pixi/envs/production/bin:$PATH
ENV CONDA_PREFIX=/app/.pixi/envs/production

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]