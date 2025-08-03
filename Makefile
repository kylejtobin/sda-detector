.PHONY: help setup check test clean install-uv

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
	@uv init --no-readme
	@uv add "pydantic[experimental]>=2.10.0" "pydantic-settings>=2.6.0"
	@echo "✅ SDA detector setup complete"

dev: ## Install dev dependencies
	uv add --dev "pytest>=8.0.0" "mypy>=1.13.0" "ruff>=0.8.0"

check: ## Quick check
	uv run ruff check . && uv run mypy src/

test: ## Run tests
	uv run pytest

clean: ## Clean up caches
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ __pycache__/
