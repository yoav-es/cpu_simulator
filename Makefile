# Makefile for CPU Simulator Project

# Configuration
IMAGE_NAME = cpu_simulator
FILES_DIR = files
MAIN_SCRIPT = main.py

# Targets
.PHONY: help build run run-mounted local-run test clean

help:
	@echo "Usage:"
	@echo "  make build         Build the Docker image"
	@echo "  make run           Run simulator in Docker with default arguments"
	@echo "  make run-mounted   Run simulator in Docker with mounted input files"
	@echo "  make local-run     Run simulator locally with Python"
	@echo "  make test          Run pytest inside Docker"
	@echo "  make clean         Remove Docker image"

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm $(IMAGE_NAME) --instructions $(FILES_DIR)/instruction_input.txt --memory $(FILES_DIR)/data_input.txt

run-mounted:
	docker run --rm -v ${PWD}/$(FILES_DIR):/cpu_simulator/$(FILES_DIR) $(IMAGE_NAME) --instructions $(FILES_DIR)/instruction_input.txt --memory $(FILES_DIR)/data_input.txt

local-run:
	python $(MAIN_SCRIPT) --instructions $(FILES_DIR)/instruction_input.txt --memory $(FILES_DIR)/data_input.txt

test:
	docker run --rm $(IMAGE_NAME) pytest

clean:
	docker rmi $(IMAGE_NAME)