# ACROSS Server

This is the codebase for the NASA ACROSS Server. It provides access to Science Situational Awareness (SSA) tools and resources.

## Contents

- [Getting Started](#getting-started)
  - [Development](#development)
    - [Database](#database)
  - [Testing Routes Locally](#testing-routes-locally)
  - [Debugging](#debugging)
  - [VS Code Setup](#vs-code-setup)
- [Architecture](#architecture)
  - [API Layer (Router/Controller)](#api-layer-routercontroller)
  - [Authentication and Authorization](#authentication-and-authorization-layer)
  - [Service Layer](#service-layer)
  - [Data Layer](#data-layer)
- [Project Structure](#project-structure)
  - [Routers/Controllers Files](#routerscontrollers-files)
  - [Auth Directory](#auth-directory)
  - [Service Files](#service-files)
  - [Exception Handling](#exception-handling)
  - [Environment Variable Configuration](#environment-variable-configuration)
  - [Database Design](#database-design)
- [Project Dependencies](#project-dependencies)
- [Deployment](#deployment)
  - [Continuous Integration (CI)](#continuous-integration-ci)
  - [[TBD] Continuous Deployment (CD)](#continuous-deployment-cd)
- [Index](#index)
  - [Environment Variables](#environment-variables)
  - [RESTful APIs](#restful-apis)
  - [Tech Stack](#tech-stack)

## Getting Started

It is assumed that the user has completed and installed the following:

- Clone the repository
- [Docker Desktop Installation](https://docs.docker.com/desktop/)

Then simply run

```zsh
make init
```

That's it! This is a [`Makefile target`](https://makefiletutorial.com/#targets) command that will:

- Ask to install [`uv`](https://docs.astral.sh/uv/getting-started/installation/) if it's not installed. (This is a required step.)
- Install dependencies
- Install [`pre-commit`](https://pre-commit.com/) git hooks.
- Create a `.env` config file
- Build the containers
- Run migrations
- Run the initial seed for basic usage with the ACROSS frontend.

If everything completed successfully, you should be able to access the generated OpenAPI docs locally at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

General documentation for other project commands can be found with `make help`.

### Development

In order to run the server through the CLI run

```zsh
make dev
```

This will start up the development server in your terminal which will run outside of the container.

If you already have the container running, you may need to stop the currently running server to free up the port using

```zsh
make stop
```

This will only stop the `app` container which runs the server, _NOT_ the `db` container. This is acceptable since most cases will not need to stop the database itself, however if the `db` container is stopped at any point, fear not, it is volumed and will not clear the existing data.

While it is possible to develop using the server running on the docker container, it may not always be ideal. Specifically, logs will output to the container itself. A tail of the logs can be output to your local terminal through the following command for ease. Under the hood it runs a docker command.

```zsh
make tail_log
```

#### Database

A couple notes on developing against the database:

1. When making changes to the db schema, you will likely want to reset your local db. This is possible through `make reset`. **This is destructive and will delete all the local data.**
2. While developing new features or functionality, it is good practice to build out the seed data accordingly to make writing the PR for yourself as the author and testing the PR for others easier. Reducing the amount of required setup for a PR is a huge boon to quality since reviewers will be able to very quickly and easily test acceptance criteria.

### Testing Routes Locally

For the `local` env there is an auth route `/auth/local-token` that will provide a long lived access token for a given user email. This can be used to easily authorize users with different scopes for testing purposes.

The next section will guide you through running a debug session in vscode.

### Debugging

In the `Run and Debug` sidebar panel in vscode, launch `Uvicorn: Fastapi`. This will start the development server with an attached debugger. More information on debugging in vscode can be found in [here](https://code.visualstudio.com/docs/editor/debugging).

### VS Code Setup

#### Python Interpreter

When working on a python project is that VS Code will need to be told where the interpreter lives. The interpreter will be in the root of this project under `.venv/bin/python`.

This should be automatically set when the extensions load due to the workspace setting `python.defaultInterpreterPath`. However, it can be set manually with the following steps:

1. `CMD + SHIFT + P` to open the command palette
2. Search for `Python: Select Interpreter`
3. Click on `Python 3.12.4 ('.venv')`

#### Workspace

This should handle any project specific configuration that is needed along with any required extension recommendations, spelling, launch, tasks, etc.

## Architecture

The high level architecture of the server is as follows:

1. API Layer (Routers and Controllers)
2. Authentication and Authorization Layer
3. Service Layer
4. Data Layer

### API Layer (Router/Controller)

The API layer or routers/controllers will be responsible for defining the endpoints and documenting it accordingly. The endpoints follow [REST naming conventions](#restful-apis). The routers can depend on multiple services, but should largely focus on high level logic that requires an interaction between services. Business logic should not be handled within the controller.

### Authentication and Authorization Layer

The authentication and authorization layer handle the security of the server. Authentication is based on secure tokens which will be verified upon each request. Once they are verified, the scopes of the user making a request will be checked for authorization. These are generally handled through the use of JSON Web Tokens (JWT) and Role-Based Access Control (RBAC) for assigned permissions or scopes.

### Service Layer

Services are ways the application can interact with the system's data and other external systems. They should be responsible for the "business logic" of behavior and functionality. Services should be the only layer to interact directly with the database. Other services can depend on each other for shared functionality.

### Data Layer

The database is separated and defined through `sqlalchemy` models. `sqlalchemy` is also used to interact with the database. This layer also includes and is responsible for migrations.

## Project Structure

```text
across-server # Your named directory where the repo lives
├── containers/
│   ├── docker-compose.local.yml
│   ├── docker-compose.prod.yml
│   ├── Dockerfile
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
├── pyproject.toml
├── Makefile
├── README.md
└── ...

```

### Routers/Controllers Files

The files will be named `router.py` within their domain and contain a [`fastapi` `APIRouter`](https://fastapi.tiangolo.com/tutorial/bigger-applications/#an-example-file-structure).

For example, the `user` domain will have a `user/router.py` which will have a defined `router`.

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

A route endpoint to get a user will be described as the following:

```py
@router.get(
    "/{user_id}",
    summary="Read a user",
    description="Read a user by a user ID.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.User,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.User,
            "description": "Return a user",
        },
    },
    dependencies=[Depends(auth.strategies.self_access)],
)
async def get(
    service: Annotated[UserService, Depends(UserService)], user_id: uuid.UUID
):
    return await service.get(user_id)
```

The large majority of the route will only be used to document the endpoint with OpenAPI. Auth will be handled by the `auth.strategies`. The functionality will be dependent on the services that are injected using FastApi's `Depends` for dependency injection.

### `auth` Directory

The `auth` layer, in theory, can live on it's own, which is the reasoning for separating the `auth` directory to it's own top level module with `across_server`. Within the `auth` submodule there is `auth.strategies` which will provide the route security dependencies. These will range from global scope access to self "user" access. They are flexible, and new strategies can be added easily in the future.

The `auth` layer defines its own `AuthUser` schema which is separated from a standard `User` schema. This is a purposeful distinction since these are two different use cases of the `User` data model.

### Service Files

The service files will generally be named `service.py` within their domain and the service class will be named `DomainService`.

For example, the `user` domain will have a `user/service.py` and the class within will be `UserService`.

Services that need to access the database will have a dependency to the db through `get_session` from the `db` module.

Services can handle throwing HTTP exceptions that will bubble up to the router level and finally be displayed to the user. More detail can be found in the [Exception Handling](#exception-handling) section.

### Exception Handling

Exception or error handling is an important part of any well developed software system. Exceptions will generally bubble up as an `HTTPException` taken from `fastapi`.

There are core exceptions that build upon the `HTTPException` to standardize and make errors of the same class (not a literal class, but the category of errors) consistent in logging and format.

A good approach to HTTP exceptions is to separate internal error messages and logs from errors seen by the client. In most cases, there will be more detail in the logged error than the client needs to know about. It is also important to limit the amount of information sent to the client that may help bad actors perform attacks.

A common exception that can be found in `core.exceptions` is the `NotFoundException`. This particular exception will only require an `entity_name` and `entity_id`. The `AcrossHTTPException` parent class will handle logging the error and return the message and status code to the client in a consistent way.

Since most routes will have a common entity being accessed, each route can have an `exceptions.py` associated with the directory to promote reusability.

Continuing with the `user` example:

```py
class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: uuid.UUID):
        super().__init__(entity_name="User", entity_id=user_id)
```

This makes it easy to handle the error anytime a user is not found. The only thing the developer needs to know is to pass in a `user_id`. They don't need to worry about how that will bubble up or what the exact status code is since it is defined somewhere else, but it is easily found if needed.

```py
try:
  # dummy "get user" function
  return get_user(user_id)
except:
  raise UserNotFoundException(user_id)
```

In most of the usages of exception handling, routers themselves do not concern themselves with catching errors. In general, dependencies or services can throw their own `AcrossHTTPException` which is an `HTTPException` (e.g. `NotFoundException`). This reduces the need to handle exceptions in a repetitive manner for common exception cases.

### Environment Variable Configuration

A "dotenv" (`.env`) file is created in the root of the project if it does not exist when running `make init`. The specific task is `configure` which leads to `scripts/create_env_file.py`. This file holds the default values for local development, and is done this way since the `.env` is `.gitignore`d from the repository.

The actual `.env` file may contain passwords and secrets to external services such as Space Track and those should not be committed. For sensitive values please reach out to an ACROSS admin or developer to obtain those secrets.

#### Changing Environment Variables

You must stop and rebuild the app container for them to take effect.

### Database Design

#### Identifiers

Entities will use `UUID`s for identifiers by default using the `Base` mixin that all models should inherit from. In certain cases, a sequential ID may be required, and those should be defined as their own field alongside the default `id` column.

The usage of `UUID`s is helpful to simplify database seeding and any batch processing. The IDs can be generated before any operation to the database to define related entities.

#### Migrations

Database migrations are run with `alembic`. A utility command is available:

```bash
make rev REV_TITLE={title}
```

The title should be relevant to the PR of the ticket, or directly related to the change (e.g. "create new user", "add column favorite_color to user", "add table telescope")

For example:

```bash
make rev REV_TITLE="create new user"
```

will automatically create a revision or migration file under `/migrations/versions` and have the format of `YYYY_MM_DD-<rev ID>_create_new_user.py`. More information about alembic configuration can be found in the `alembic.ini` file.

## Project Dependencies

### Installing New Dependencies

Currently, the simplest way to install new dependencies is to add the dependency to the respective `.in` file within the `requirements/` directory and then run `make lock ENV=<env>` to update the lockfile and `make install ENV=<env>`.

## Deployment

### Continuous Integration (CI)

The CI pipeline runs on any PR against `main`. It is initialized through a GitHub Action within `.github/workflows/ci.yml` which will include running the following jobs: `lint`, `format`, `build` (the docker container), and `test`. All of the checks must pass in order for a PR to be approved and merged.

### Continuous Deployment (CD)

TBD

### Manually pushing an ECR image to the ECR repository

This should generally only be used for testing purposes or emergencies where manual intervention is needed due to issues with the Github Actions deployment pipeline.

The make command for all of these steps is below, but the documentation is included here for reference.

```shell
make push TAG=<replace-with-image-tag>
```

**Note:** This is ACROSS's custom docker build command for deployable containers, the `IMAGE_TAG` is optional here and can be whatever your want, but it is commonly a commit sha (e.g. `sha-1234567` or the long format `sha-1234567890abcdefghijklmnopqrstuvwxyz1234`) or a version (e.g. `v1.2.3` or for pre-release `v1.2.3.beta.1`)

Use the following steps to authenticate and push an image to your repository. For additional registry authentication methods, including the Amazon ECR credential helper, see [Registry Authentication](https://docs.aws.amazon.com/AmazonECR/latest/userguide/Registries.html#registry_auth) .

- Retrieve an authentication token and authenticate your Docker client to your registry. Use the AWS CLI:

    ```shell
    aws ecr get-login-password \
      --region us-east-2 | \
    docker login \
      --username AWS \
      --password-stdin 905418122838.dkr.ecr.us-east-2.amazonaws.com
    ```

    **Note:** If you receive an error using the AWS CLI, make sure that you have the latest version of the AWS CLI and Docker installed.

- Build your Docker image using the following command. For information on building a Docker file from scratch see the [instructions here](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html). You can skip this step if your image is already built:

    ```shell
    make build_deploy IMAGE_TAG=latest
    ```

    **Note:** This is ACROSS's custom docker build command for deployable containers

- After the build completes, tag your ECR image so you can push the image to this repository:

    ```shell
    docker tag \
    core-server:latest \
    905418122838.dkr.ecr.us-east-2.amazonaws.com/core-server:latest
    ```

    **Note:** Replace the ECR image tag with whatever tag is being used.

- Run the following command to push this image to your newly created AWS repository:

    ```shell
    docker push 905418122838.dkr.ecr.us-east-2.amazonaws.com/core-server:latest
    ```

    **Note:** ensure that the tags are the same. To see a list of tagged images run

    ```shell
    docker image list
    ```

    this will output a table similar to the following:

    ```shell
    REPOSITORY                                                 TAG       IMAGE ID       CREATED         SIZE
    core-server                                                latest   57a9918e1dfc   40 seconds ago   209MB
    905418122838.dkr.ecr.us-east-2.amazonaws.com/core-server   latest   cd4c0a5c2b35   20 seconds ago   209MB
    ```

### Helpful Docker Commands To Aid in Debugging a Dockerfile

- Build a container separately from docker-compose

  ```zsh
  docker build -t <image-name> .
  ```

  optionally add `--target` for whichever stage you want to build.

- Open a shell in a particular image by spinning up a temporary container for it

  ```zsh
  make temp_run
  ```

  or

  ```zsh
  docker run --rm -it --entrypoint=/bin/bash <image-name>
  ```

  Note that it is assumed the image has bash installed.

## Index

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
| `ACROSS_FRONTEND_TOKEN` | Requested API token for a frontend-level user created when the database is created |

### RESTful APIs

Helpful resources on REST APIs.

- [RESTful API](https://restfulapi.net/)
- [fastapi-best-practices (REST section)](https://github.com/zhanymkanov/fastapi-best-practices?tab=readme-ov-file#follow-the-rest)

### Tech Stack

- [Python](https://www.python.org/) as the programming language
- [FastAPI](https://fastapi.tiangolo.com/) as the server framework
- [Pydantic](https://docs.pydantic.dev/latest/) for schema validation
- [SqlAlchemy](https://www.sqlalchemy.org/) for the Object-Relation Mapping (ORM)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) for DB migrations
- [PostgreSQL](https://www.postgresql.org/) for the database
- [Docker](https://docs.docker.com/) for containerization and container composition with `docker-compose`
- [uv](https://docs.astral.sh/uv/) as the dependency management tool (dependency management)
- [Makefile](https://www.gnu.org/software/make/manual/make.html) - project management tool for helpful commands.
- [pre-commit](https://pre-commit.com) for running linting/styling on the pre-commit git hook
