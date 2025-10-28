# Makefile for CPU Simulator Project

# Configuration
IMAGE_NAME = cpu_simulator
FILES_DIR = files
MAIN_SCRIPT = main.py
VENV_DIR = venv
INSTRUCTIONS ?= $(FILES_DIR)/instruction_input.txt
MEMORY ?= $(FILES_DIR)/data_input.txt

.PHONY: help build run run-mounted local-run test clean venv activate local-test

# 🧰 Help
help:
	@echo "Usage:"
	@echo "  make build         Build the Docker image"
	@echo "  make run           Run simulator in Docker with default arguments"
	@echo "  make run-mounted   Run simulator in Docker with mounted input files"
	@echo "  make local-run     Run simulator locally with Python"
	@echo "  make test          Run pytest inside Docker"
	@echo "  make clean         Remove Docker image"
	@echo "  make venv          Create Python virtual environment"
	@echo "  make activate      Show activation instructions"
	@echo "  make local-test    Run pytest in virtual environment"

# 🐳 Docker Commands
build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm $(IMAGE_NAME) --instructions $(INSTRUCTIONS) --memory $(MEMORY)

run-mounted:
	docker run --rm -v ${PWD}/$(FILES_DIR):/cpu_simulator/$(FILES_DIR) $(IMAGE_NAME) --instructions $(INSTRUCTIONS) --memory $(MEMORY)

test:
	docker run --rm $(IMAGE_NAME) pytest

clean:
	docker rmi $(IMAGE_NAME)

# 🐍 Local Python Commands
local-run:
	python $(MAIN_SCRIPT) --instructions $(INSTRUCTIONS) --memory $(MEMORY)

local-test:
	$(VENV_DIR)/Scripts/activate && pytest

# 🧪 Virtual Environment Setup
venv:
	python3.13 -m venv $(VENV_DIR)
	$(VENV_DIR)/Scripts/activate && pip install -r requirements.txt

activate:
	@echo "To activate the virtual environment:"
	@echo "  source $(VENV_DIR)/bin/activate   # On macOS/Linux"
	@echo "  $(VENV_DIR)\\Scripts\\activate     # On Windows"