# Makefile for Test Label Image Generation (UV-based)

# Directories
CONFIG_DIR := config
TEMPLATE_DIR := templates
OUTPUT_DIR := output
SCRIPT_DIR := scripts

# Files
CONFIG_FILE := $(CONFIG_DIR)/test_cases.yaml
TEMPLATE_FILES := $(wildcard $(TEMPLATE_DIR)/*)
SCRIPT_FILE := $(SCRIPT_DIR)/generate_labels.py

# UV commands
UV := uv
PYTHON := uv run python
UV_SYNC := uv sync

# Default target
.PHONY: all
all:
	@echo "Generating test labels..."
	$(PYTHON) $(SCRIPT_FILE) \
		--config $(CONFIG_FILE) \
		--templates $(TEMPLATE_DIR) \
		--output $(OUTPUT_DIR)

# Install dependencies with UV
.PHONY: install
install:
	@echo "Installing dependencies with UV..."
	$(UV_SYNC)
	@echo "Installing Playwright browsers..."
	$(UV) run playwright install chromium
	$(UV) run playwright install-deps
	Dependencies installed

# Sync dependencies (update lockfile)
.PHONY: sync
sync:
	@echo "Syncing dependencies..."
	$(UV_SYNC)

# Update dependencies
.PHONY: update
update:
	@echo "Updating dependencies..."
	$(UV) lock --upgrade

# Export requirements.txt (for compatibility)
.PHONY: export-requirements
export-requirements:
	@echo "Exporting requirements.txt..."
	$(UV) pip compile pyproject.toml -o requirements.txt

# Clean generated files
.PHONY: clean
clean:
	@echo "Cleaning generated images..."
	rm -f $(OUTPUT_DIR)/*.png $(OUTPUT_DIR)/*.json

# Clean everything including venv
.PHONY: distclean
distclean: clean
	@echo "Removing virtual environment..."
	rm -rf .venv
	rm -f uv.lock

# Help
.PHONY: help
help:
	@echo "Test Label Generator - Makefile targets (UV-based):"
	@echo ""
	@echo "  make install          Install dependencies with UV"
	@echo "  make all              Generate all test label images"
	@echo "  make sync             Sync dependencies"
	@echo "  make update           Update all dependencies"
	@echo "  make export-requirements  Export requirements.txt"
	@echo "  make clean            Remove generated images"
	@echo "  make distclean        Remove images and venv"
	@echo ""
	@echo "Examples:"
	@echo "  make                  # Generate all images"
	@echo ""