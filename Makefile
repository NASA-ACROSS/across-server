# Define env variables
ENV ?= local
ENVS = local test lint prod
IS_ENV_VALID := $(filter $(ENV), $(ENVS))

# define directories
VENV_DIR = .venv
VENV_BIN = $(VENV_DIR)/bin
REQ_DIR = requirements
REQ_IN = $(REQ_DIR)/$(ENV).in
REQ_TXT = $(REQ_DIR)/$(ENV).txt
UV_INSTALL_SCRIPT = https://astral.sh/uv/install.sh

# Detect installed tools
IS_UV_INSTALLED := $(shell which uv || echo "")
IS_PIP_COMPILE_INSTALLED := $(shell which $(VENV_BIN)/pip-compile || echo "")

# Tasks
.PHONY:
	check_env install_uv pip_tools venv_dir venv install clean dev help

# @awk -F ':.*## ' '/^[a-zA-Z_-]+:.*## / && !/###/ { printf "    \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
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

check_env: ### Check if the passed in ENV is valid
	@if [ -z $(IS_ENV_VALID) ]; then \
		echo "Invalid ENV: '$(ENV)'. Allowed values are: $(ENVS)"; \
		exit 1; \
	fi

# Group: Setup
install_uv: ## Install 'uv' if needed (this will install it globally)
	@echo "Installing 'uv'...";
	@curl -LsSf $(UV_INSTALL_SCRIPT) | sh;

install: check_env venv ## Install dependencies from the lockfile for the specified ENV
	@if [ -z $(IS_UV_INSTALLED) ]; then \
		echo "'uv' is not installed. Would you like to install it to the global system now? (y/n)"; \
		read choice; \
		if [ "$$choice" = "y" ] || [ "$$choice" = "Y" ]; then \
			$(MAKE) install_uv; \
		else \
			echo "Cannot proceed without 'uv'. Exiting."; \
			exit 1; \
		fi; \
	fi;
	@uv pip sync $(REQ_TXT);
	@echo "Installed dependencies";
	
lock: check_env venv ## Create or update the lockfile.
	@echo "Updating lockfile...";
	@uv pip compile $(REQ_IN) -o $(REQ_TXT) --quiet;

venv_dir:	### Create the venv dir if it DNE
	@mkdir -p $(VENV_DIR)

venv: venv_dir ### Create venv within specified env
	@if [ ! -d $(VENV_BIN) ]; then \
		echo "Creating virtual environment."; \
		uv venv $(VENV_DIR) --python '>=3.12,<3.13'; \
	fi;

# Group: Development
build: ## Build the local docker containers
	@docker compose -f docker-compose.local.yml up --build -d;

dev: ## Start the server in the terminal
	@$(VENV_BIN)/fastapi dev across_server/main.py;

# Group: Testing
test: ## Run automated tests
	@$(VENV_BIN)/pytest --cov=across_server **/*/*.py;

lint: ## Run linting
	@$(VENV_BIN)/pre-commit run;

# Group: Database
rev: ## Create a new database revision (migration). Usage: `make rev REV_TITLE="Migration title"`
	@if [ -z $(REV_TITLE) ]; then \
		echo "The REV_TITLE is missing for the revision.\n"; \
		exit 1; \
	fi
	@$(VENV_BIN)/alembic revision --autogenerate -m "$(REV_TITLE)";

seed: ## Seed the database with initial data (only used on local and dev environments)
	@if [ -n "$(filter $(ENV), local)" ]; then \
		$(VENV_BIN)/python -m migrations.seed; \
	else \
		echo "Seeding is only allowed in ENVs: local, dev."; \
	fi

migrate: ## Run the migrations for the database
	@$(VENV_BIN)/alembic upgrade head

# Group: Production
prod: ## Build the production container
	@docker compose up --build -d;
	
# Group: Cleaning
clean: ## Clean virtual env
	@rm -rf $(VENV_DIR)
	@echo "Cleaned up environment."