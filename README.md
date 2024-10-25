# ACROSS Server

This is the codebase for the ACROSS Server. It provides access to Science Situational Awareness (SSA) tools and resources.

## Contents

- [Getting Started](#getting-started)
  - [Development](#development)
    - [Database](#database)
  - [Testing Routes Locally](#testing-routes-locally)
  - [Debugging](#debugging)
- [Architecture](#architecture)
  - [API Layer (Router/Controller)](#api-layer-routercontroller)
  - [Authentication and Authorization](#authentication-and-authorization-layer)
  - [Service Layer](#service-layer)
  - [Data Layer](#data-layer)
- [Project Structure](#project-structure)
  - [Routers/Controllers Files](#routerscontrollers-files)
  - [Auth Directory](#auth-directory)
  - [Service Files](#service-files)
  - [Environment Variable Configuration](#environment-variable-configuration)
  - [Database Migrations](#database-migrations)
- [Deployment](#deployment)
  - [Continuous Integration (CI)](#continuous-integration-ci)
  - [[TBD] Continuous Deployment (CD)](#continuous-deployment-cd)
- [Glossary](#glossary)
  - [Tech Stack](#tech-stack)
  - [Environment Variables](#environment-variables)

## Getting Started

It is assumed that the user has completed and installed the following:

- Clone the repository
- [`pixi` Installation](https://pixi.sh/latest/#installation)
- [Docker Desktop Installation](https://docs.docker.com/desktop/)

Then simply run

```zsh
pixi run init
```

That's it! This is a [`pixi task`](https://pixi.sh/latest/features/advanced_tasks/) that
will install dependencies, create a `.env` config file, build the docker containers, run migrations, and run the initial
seed for basic usage with the ACROSS frontend.

**small note:** `pixi` tasks can be run with `pixi r <task>` as well.

If everything completed successfully, you should be able to access the generated OpenAPI
docs locally at

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Development

In order to run the server through the CLI run

```zsh
pixi run dev
```

This will start up the development server in your terminal which will run outside of the docker container.

If you already have the container running, you may need to stop the currently running server to free up the port using

```zsh
pixi run down
```

This will only stop the `app` container which runs the server, _NOT_ the `db` container. This is acceptable since most cases will not need to stop the database itself, however if the container is stopped, fear not, it is volumed and will not clear the existing data.

While it is possible to develop using the server running on the docker container, it may not always
be ideal. Specifically, logs will output to the container itself.

A tail of the logs can be output to your local terminal if you'd like through the following for ease which runs a docker command.

```zsh
pixi run tail_log
```

#### Database

A couple notes on developing against the database:

1. When making changes to the db schema, you will likely want to reset your local db. This is possible through `pixi r reset`.
2. While developing new features or functionality, it is good practice to build out the seed data accordingly to make writing the PR for yourself as the author and testing the PR for others easier. Reducing the amount of required setup for a PR is a huge boon to quality since reviewers will be able to very quickly and easily test acceptance criteria.

### Testing Routes Locally

For the `local` env there is an auth route `/auth/local-token` that will provide a long lived access token for a given user email. This can be used to authorize different users with different scopes easily for testing.

The next section will guide you through running a debug session in vscode.

### Debugging

In the `Run and Debug` sidebar panel in vscode, launch `Uvicorn: Fastapi`. This will start the development server with an attached debugger. More information on debugging in vscode can be found [here](https://code.visualstudio.com/docs/editor/debugging).

## Architecture

The high level architecture of the server is as follows:

1. API Layer (Routers and Controllers)
2. Authentication and Authorization Layer
3. Service Layer
4. Data Layer

### API Layer (Router/Controller)

The API layer or routers/controllers will be responsible for defining the endpoints and documenting it accordingly. The routers can depend on multiple services, but should largely focus on high level logic that requires an interaction between services. Business logic should not be within the controller.

### Authentication and Authorization Layer

The authentication and authorization layer handle the security of the server. Authentication is based on secure tokens which will be verified upon each request. Once they are verified, the scopes of the user making a request will be checked for authorization. These are generally handled through the use of JSON Web Tokens (JWT) and Role-Based Access Control (RBAC) for assigned permissions or scopes.

### Service Layer

Services are ways the application can interact with the system's data and other external systems. They should be responsible for the "business logic" of behavior and functionality. Services should be the only layer to interact directly with the database. Other services can depend on each other for shared functionality.

### Data Layer

The database is separated and defined through sqlalchemy models. Sqlalchemy is also used to interact with the database. This layer also incudes and is responsible for migrations.

## Project Structure

```text
across-server # Your named directory where the repo lives
├── migrations/
├── across_server
│   ├── auth/
│   │   └── tokens/
│   │       ├── base_token.py       # base functionality of JWT tokens
│   │       ├── access_token.py     # strategy to interact with an access token
│   │       ├── magic_token.py      # strategy to interact with the magic link token
│   │       └── refresh_token.py    # strategy to interact with a refresh token
│   │   ├── router.py       # auth endpoints
│   │   ├── schemas.py
│   │   ├── config.py       # auth specific config
│   │   ├── magic_link.py
│   │   ├── schemas.py
│   │   ├── security.py     # method of security (OAuth, HTTPBearer, etc)
│   │   ├── strategies.py   # RBAC strategies
│   │   ├── exceptions.py
│   │   └── service.py
│   ├── routes/
│   │   └── user/
│   │       ├── router.py
│   │       ├── schemas.py
│   │       ├── constants.py
│   │       ├── exceptions.py
│   │       └── service.py
│   ├── <external_service>/
│   │   ├── client.py       # Client model for external service
│   │   ├── schemas.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   └── utils.py
│   ├── core/               # Any shared ACROSS dependencies
│   │   ├── schemas.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   └── exceptions.py
│   ├── db/
│   │   ├── models.py       # The entire DB schema for ACROSS
│   │   ├── config.py       # DB configuration
│   │   └── database.py     # DB connection-related logic and management
│   ├── __about__.py        # Holds the deployed version of the server
│   └── main.py             # Entrypoint to the server
├── tests/
│   ├── auth/
│   ├── routes/
│   │   └── user/
│   ├── <external_service>/
├── templates/
│   └── login-link-email.html
├── .env
├── .gitignore
├── docker-compose.debug.yml
├── docker-compose.yml
├── Dockerfile
├── pixi.lock
├── pyproject.toml
├── README.md
└── ...

```

### Routers/Controllers Files

The files will be named `router.py` within their domain and contain a `fastapi` `APIRouter`.

For example, the `user` domain will have a `user/router.py`.

```py
router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
    },
)
```

### Auth Directory

The auth layer, in theory, can live on it's own, which is the reasoning for separating the `auth` directory to it's own top level module with `across_server`. Within the `auth` submodule there is `auth.strategies` which will provide the route security dependencies. These will range from global scope access to self "user" access. They are flexible and new strategies can be added easily in the future.

### Service Files

The service files will generally be named `service.py` within their domain and the service class will be named `DomainService`.

For example, the `user` domain will have a `user/service.py` and the class within will be `UserService`.

Services will have a dependency to the db through `get_session` from the `db` module.

### Environment Variable Configuration

A "dotenv" (`.env`) file is created in the root of the project if it does not exist when running `pixi run init`. The specific task is `configure` which leads to `scripts/create_env_file.py`. This file holds the default values for local development, and is done this way since the `.env` is `.gitignore`d from the repository.

The actual `.env` file may contain passwords and secrets to external services such as Space Track and those should not be committed. For sensitive values please reach out to an ACROSS admin or developer to obtain those secrets.

#### Changing Environment Variables

You must stop and rebuild the app container for them to take effect.

### Database Migrations

Database migrations are run with alembic. A utility `pixi` task is available:

```bash
pixi run rev "<title>"
```

The title should be relevant to the PR of the ticket, or directly related to the change (e.g. "create new user", "add column favorite_color to user", "add table telescope")

For example:

```bash
pixi run rev "create new user"
```

will automatically create a revision or migration file under `/migrations/versions` and have the format of `YYYY_MM_DD-<rev ID>_create_new_user.py`. More information about alembic configuration can be found in the `alembic.ini` file.

## Deployment

### Continuous Integration (CI)

The CI pipeline runs on any PR against `main`. It is initialized through a GitHub Action within `.github/workflows/ci.yml` which will include running the linters, formatter, building the docker container, and running automated tests. All of the checks must pass in order for a PR to be approved and merged.

### Continuous Deployment (CD)

TBD

### Helpful Docker Commands To Aid in Debugging a Dockerfile

Build a container separately from docker-compose

```zsh
docker build -t <image-name> .
```

optionally add `--target` for whichever stage you want to build.

Open a shell in a particular image by spinning up a temporary container for it

```zsh
docker run --rm -it --entrypoint=/bin/bash <image-name>
```

Note that it is assumed the image has bash installed.

## Glossary

### Tech Stack

- [Python](https://www.python.org/) as the programming language
- [FastAPI](https://fastapi.tiangolo.com/) as the server framework
- [Pydantic](https://docs.pydantic.dev/latest/) for schema validation
- [SqlAlchemy](https://www.sqlalchemy.org/) for the Object-Relation Mapping (ORM)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) for DB migrations
- [PostgreSQL](https://www.postgresql.org/) for the database
- [Docker](https://docs.docker.com/) for containerization and container composition with `docker-compose`
- [Pixi](https://www.pixi.sh/) as the project management tool (dependency management, tasks, etc)
- [pre-commit](https://pre-commit.com) for running linting/styling on the pre-commit git hook

### Environment Variables

ACROSS relies on the following environment variables:

| Variable                | Use                                                                                |
| ----------------------- | ---------------------------------------------------------------------------------- |
| `SPACETRACK_USER`       | Login username for space-track.org.                                                |
| `SPACETRACK_PWD`        | Login password for space-track.org.                                                |
| `ACROSS_DB_HOST`        | Host name of Postgres database                                                     |
| `ACROSS_DB_NAME`        | Name of Postgres database                                                          |
| `ACROSS_DB_USER`        | Username for Postgres database                                                     |
| `ACROSS_DB_IAM_AUTH`    | For AWS instances, do IAM authentication                                           |
| `ACROSS_DB_PWD`         | Password for Postgres database (not need if IAM used)                              |
| `ACROSS_DB_ECHO`        | SqlAlchemy verbose output, will flood output with SQL statements.                  |
| `AWS_REGION`            | AWS region name                                                                    |
| `AWS_PROFILE`           | Name of AWS profile to get credentials                                             |
| `ACROSS_EMAIL_USERNAME` | Email SMTP Username                                                                |
| `ACROSS_EMAIL_PASSWORD` | Email SMTP Password                                                                |
| `ACROSS_EMAIL`          | From address for sent email                                                        |
| `ACROSS_SMTP_HOST`      | Hostname of SMTP server                                                            |
| `ACROSS_SMTP_PORT`      | Port number of SMTP server                                                         |
| `ACROSS_DEBUG`          | Set debug mode, which makes output more verbose                                    |
| `ACROSS_FRONTEND_IP`    | IP address allowed to access private endpoints.                                    |
| `ACROSS_FRONTEND_URL`   | URL of front end website                                                           |
| `ACROSS_ADMIN_TOKEN`    | Requested API token for an admin-level user created when the database is created   |
| `ACROSS_FRONTEND_TOKEN` | Requested API token for a frontend-level user created when the database is created |
| `ACROSS_FRONTEND_EMAIL` | Frontend-level user's email.                                                       |
