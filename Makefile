# Define variables
ENV ?= local
ENVS = local test types prod
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
	install_uv pip_tools venv_dir venv install clean dev

# Create directories
venv_dir:
	@mkdir -p $(VENV_DIR)

# install uv if needed
install_uv:
	@if [ -z $(IS_UV_INSTALLED) ]; then \
		echo "Installing uv..."; \
		curl -LsSf $(UV_INSTALL_SCRIPT) | sh; \
	fi;

# create venv within specified env
venv: venv_dir
	@if [ ! -d $(VENV_DIR)/bin ]; then \
		echo "Creating virtual environment."; \
		uv venv $(VENV_DIR); \
	fi;

# Install dependencies for the specified ENV
lock: venv
	@echo "Updating lockfile...";
	@uv pip compile $(REQ_IN) -o $(REQ_TXT) --quiet;

install: venv
	@uv pip sync $(REQ_TXT);
	@echo "Installed dependencies";

build:
	@docker compose -f docker-compose.local.yml up --build -d;

dev:
	@source .venv/bin/activate
	@fastapi dev src/across_api/main.py

prod:
	@docker compose up --build -d;
	
# Clean generated lock files
clean:
	@rm -rf $(VENV_DIR)
	@rm -f $(REQ_DIR)/*.txt
	@echo "Cleaned up environment and lock files."