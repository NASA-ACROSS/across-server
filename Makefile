# Define variables
ENV ?= local
ENVS = local test types prod
VENV_DIR = .venv/$(ENV)
VENV_BIN = $(VENV_DIR)/bin
# this will only work when running make from the CWD
# https://stackoverflow.com/questions/18136918/how-to-get-current-relative-directory-of-your-makefile
PWD := $(shell pwd;)
IS_PIP_COMPILE_INSTALLED := $(shell which $(VENV_BIN)/pip-compile || echo "")
IS_UV_INSTALLED := $(shell which uv || echo "")

# Tasks
.PHONY:
	uv pip_compile_check venv install clean venv_dir

# create venv dir
venv_dir:
	@if [ ! -d $(VENV_DIR) ]; then \
		mkdir -p $(VENV_DIR); \
	else \
		echo "'$(ENV)' virtual environment directory exists."; \
	fi; \

# install uv if needed
uv:
	@if [ -z $(IS_UV_INSTALLED) ]; then \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=$(VENV_DIR) env INSTALLER_NO_MODIFY_PATH=1 sh \
	else \
		echo "uv is already installed."; \
	fi;

# create venv within specified env
venv: uv
	@if [ ! -d $(VENV_DIR)/bin ]; then \
		echo "Creating '$(ENV)' virtual env..."; \
		uv venv $(VENV_DIR); \
	else \
		echo "'$(ENV)' virtual environment exists."; \
	fi;

pip_compile_check:
	@source $(VENV_DIR)/bin/activate;
	@if [ -z $(IS_PIP_COMPILE_INSTALLED) ]; then \
		echo "pip-tools not found."; \
		pip install pip-tools; \
	fi; \

# Install dependencies for the specified ENV
install: pip_compile_check
	@source $(VENV_DIR)/bin/activate; \
	$(VENV_BIN)/pip-compile requirements/$(ENV).in -o requirements/$(ENV).txt; \
	$(VENV_BIN)/pip-sync requirements/$(ENV).txt; \
	echo "Installed $(ENV) dependencies."; \

# Clean generated lock files
clean:
	rm -rf .env/$(ENV)
	rm -f requirements/*.txt