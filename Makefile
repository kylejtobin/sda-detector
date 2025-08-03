.PHONY: help setup check test clean install-uv run self-analyze legacy-run legacy-self-analyze

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install-uv: ## Install uv package manager
	@if command -v uv >/dev/null 2>&1; then \
		echo "✅ uv already installed"; \
	else \
		echo "📦 Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✅ uv installed - restart shell or run: source ~/.bashrc"; \
	fi

setup: install-uv ## Setup SDA detector dependencies
	@echo "📦 Installing dependencies..."
	@uv sync
	@echo "✅ SDA detector setup complete"

dev: ## Install dev dependencies
	uv add --dev "pytest>=8.0.0" "mypy>=1.13.0" "ruff>=0.8.0"

check: ## Quick check
	uv run ruff check . && uv run mypy src/

test: ## Run tests
	uv run pytest

run: ## Run SDA detector on a file (usage: make run FILE=path/to/file.py)
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Please specify a file: make run FILE=path/to/file.py"; \
	else \
		PYTHONPATH=src uv run python -m sda_detector "$(FILE)"; \
	fi

self-analyze: ## Run SDA detector on itself (dogfooding)
	PYTHONPATH=src uv run python -m sda_detector src/sda_detector "SDA Detector Self-Analysis"

legacy-run: ## Run original single-file detector: make legacy-run FILE=path/to/file.py
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Please specify a file: make legacy-run FILE=path/to/file.py"; \
	else \
		uv run python src/sda_detector.py "$(FILE)"; \
	fi

legacy-self-analyze: ## Run original detector on itself
	uv run python src/sda_detector.py src/sda_detector.py "SDA Detector Self-Analysis"

clean: ## Clean up caches
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ __pycache__/
