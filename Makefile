# Define env variables
ENV ?= local
ENVS = local test action prod
IS_ENV_VALID := $(filter $(ENV), $(ENVS))

# Docker
DOCKER_COMPOSE_FILE = containers/docker-compose.$(ENV).yml
DOCKER_COMPOSE = docker compose -f ${DOCKER_COMPOSE_FILE} --env-file=.env
IMAGE_TAG = $(shell git rev-parse --short HEAD)

# define directories
VENV_DIR = .venv
VENV_BIN = $(VENV_DIR)/bin
REQ_DIR = requirements
REQ_IN = $(REQ_DIR)/$(ENV).in
REQ_TXT = $(REQ_DIR)/$(ENV).txt
UV_INSTALL_SCRIPT = https://astral.sh/uv/install.sh

# Detect installed tools
IS_UV_INSTALLED := $(shell command -v uv || echo "")
IS_PIP_COMPILE_INSTALLED := $(shell command -v $(VENV_BIN)/pip-compile || echo "")


# The `ask` macro displays a prompt to the user, processes their input,
# and conditionally executes a command based on the response.
#
# Args:
#   1: The message to display to the user (e.g., a question).
#   2: The command to execute if the user responds with 'y' or 'Y'.
#   3: The message to display and exit if the user responds with 'n' or 'N'.
#
# Example usage:
#   $(call ask, "Installing dependency",echo "Installing dep..." && install,"Installation aborted.")
#
# Example output:
# > Installing dependency, are you sure? (y/n)
# > y
# > Installing dep...
#
# > Installing dependency, are you sure? (y/n)
# > n
# > Installation aborted
define ask
	echo "$(1) Are you sure? (y/n)"; \
	read choice; \
	if [ "$$choice" = "y" ] || [ "$$choice" = "Y" ]; then \
		$(2); \
	else \
		echo "$(3)"; \
		exit 0; \
	fi
endef

# Tasks
.PHONY: list_targets help init install_uv install install_hooks lock configure venv_dir venv check_env install_deps start run stop build dev restart reset tail_logs temp_run test lint rev seed migrate prod clean prune rm_imgs

list_targets: ### Internal command used for getting a list of commands for .PHONY
	@awk '/^[a-zA-Z_\-]+:/ {sub(/:/, ""); printf "%s ", $$1} END {print ""}' $(MAKEFILE_LIST)

help:
	@echo "Usage:\n    make \033[36m<target>\033[0m"
	@awk ' \
	BEGIN { \
		group = ""; \
	} \
	/^[#] Group:/ { \
		group = substr($$0, index($$0,$$3)); \
		print "\n" group " Commands:"; \
	} \
	/^[a-zA-Z_-]+:.*## / && !/###/ { \
		target = $$1; \
		description = substr($$0, index($$0, "##") + 3); \
		gsub(":", "", target); \
		printf "  \033[36m%-15s\033[0m %s\n", target, description \
	} \
	' $(MAKEFILE_LIST)


# Group: Setup
init: install configure run migrate seed ## Initialize the project, dependencies, and start the server

install_uv: ## Install 'uv' if needed (this will install it globally)
	@echo "Installing 'uv'...";
	@curl -LsSf $(UV_INSTALL_SCRIPT) | sh;

install: check_env venv ## Install dependencies from the lockfile for the specified ENV
	@if [ -z $(IS_UV_INSTALLED) ]; then \
		$(call ask,\
			"'uv' is not installed. Proceeding will install to the global system.",\
			$(MAKE) install_deps,\
			"Cannot proceed without 'uv'. Exiting."\
		); \
	else \
		$(MAKE) install_deps; \
	fi;
	@$(MAKE) install_hooks

install_hooks: ## Install 'pre-commit' git hooks, only for local.
	@if [ $(ENV) == local ]; then \
		echo "Installing pre-commit git hooks..."; \
		pre-commit install; \
	else \
		echo "Not a git repository. Skipping pre-commit hooks installation."; \
	fi

lock: check_env venv ## Create or update the lockfile
	@echo "Updating lockfile...";
	@for env in $(ENVS); do \
		in_file=$(REQ_DIR)/$$env.in; \
		out_file=$(REQ_DIR)/$$env.txt; \
		echo "Compiling $$in_file -> $$out_file"; \
		uv pip compile $$in_file -o $$out_file --quiet; \
	done

configure: ## Create a .env file for environment variables
	@echo "Creating .env file..."
	@$(VENV_BIN)/python scripts/create_env_file.py

venv_dir:	### Create the venv dir if it DNE
	@mkdir -p $(VENV_DIR)

venv: venv_dir ### Create venv within specified env
	@if [ ! -d $(VENV_BIN) ]; then \
		echo "Creating virtual environment."; \
		uv venv $(VENV_DIR) --python '>=3.12,<3.13'; \
	fi;

check_env: ### Check if the passed in ENV is valid
	@if [ -z $(IS_ENV_VALID) ]; then \
		echo "Invalid ENV: '$(ENV)'. Allowed values are: $(ENVS)"; \
		exit 1; \
	fi

check_prod: ### Check if the env is prod
	@if [ $(ENV) == prod ]; then \
		echo "This can only be run on non-production environments."; \
		exit 1; \
	fi

install_deps: ### Install dependencies
	@uv pip sync $(REQ_TXT);
	@echo "Installed dependencies";

mfa: ## Auth with AWS through MFA
	@scripts/mfa.sh

# Group: Development
start: check_prod run migrate seed ## Start the application containers (includes migrating and seeding)

dev: check_prod ## Start the server in the terminal
	@$(VENV_BIN)/fastapi dev across_server/main.py

stop: check_prod ## Stop the server container
	@$(DOCKER_COMPOSE) down app

stop_all: check_prod ## Stop all containers
	@$(DOCKER_COMPOSE) down -v

build: check_prod ## Build the containers (does not run them)
	@DOCKER_BUILDKIT=1 $(DOCKER_COMPOSE) build --build-arg APP_ENV=$(ENV)

restart: ## Restarts the app container
	@$(DOCKER_COMPOSE) restart

reset: check_prod ## Resets the db containers and volumes
	@$(call ask,\
		"Proceeding will reset the db and delete any existing data.", \
		$(MAKE) stop_all && $(MAKE) start,\
		"Reset aborted."\
	);

hard_reset: check_prod ## Hard reset and rebuild everything (basically `rm -rf` for the entire stack)
	@$(call ask,\
		"Proceeding will reset everything locally.", \
		$(MAKE) stop_all && $(MAKE) rm_imgs && $(MAKE) start,\
		"Reset aborted."\
	);

tail_logs: ## Output a tail of logs for the server
	@$(DOCKER_COMPOSE) logs -ft app

temp_run: check_prod ## Start a temporary container from an image with a bash shell for debugging
	@docker run --rm -it --entrypoint=/bin/bash across-server-app


# Group: Testing
test: ## Run automated tests
	@$(VENV_BIN)/pytest --cov=across_server tests/**;

lint: ## Run linting
	@$(VENV_BIN)/pre-commit run --all-files;

types: ## Run type checks
	@$(VENV_BIN)/mypy;


# Group: Database
rev: ## Create a new database revision (migration). Usage: `make rev REV_TITLE="Migration title"`
	@if [ -z $(REV_TITLE) ]; then \
		echo "The REV_TITLE is missing for the revision."; \
	else \
		$(VENV_BIN)/alembic revision --autogenerate -m "$(REV_TITLE)"; \
	fi

seed: check_prod ## Seed the database with initial data (only used on local and dev environments)
	@if [ -n "$(filter $(ENV), local dev)" ]; then \
		$(VENV_BIN)/python -m migrations.seed; \
	else \
		echo "Seeding is only allowed in ENVs: local, dev."; \
	fi

migrate: ## Run the migrations for the database
	@$(VENV_BIN)/alembic upgrade head

# Group: Running
run: ## Run the containers
	@$(DOCKER_COMPOSE) up -d --wait --wait-timeout 30

# Group: Production
build_prod: ## Build the containers for production -- does not use docker-compose
	@DOCKER_BUILDKIT=1 docker build \
		-t across-server:$(IMAGE_TAG) \
		--no-cache \
		--platform linux/amd64 \
		--provenance false \
		--ssh default \
		--build-arg APP_ENV=prod \
		-f./containers/Dockerfile .

client: ## Generate client
	@docker run --rm \
		-v ${PWD}:/local \
			openapitools/openapi-generator-cli generate \
		-i /local/openapi.json \
		-g python \
		-o /local/out/python \
		-c /local/openapi-config.json

client_templates:
	docker run --rm \
		-v ${PWD}:/local \
			openapitools/openapi-generator-cli author template \
		-g python \
		-o /local/templates/python

# Group: Cleaning
clean: ## Clean virtual env
	@rm -rf $(VENV_DIR)
	@echo "Cleaned up environment."

prune: ## prune the images and containers
	@docker container prune
	@docker image prune

rm_imgs: ## Delete images associated with the application.
	@$(DOCKER_COMPOSE) down --rmi all
