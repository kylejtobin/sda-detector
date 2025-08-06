.PHONY: help setup check test clean install-uv run self-analyze analyze-tests compliance-report legacy-run legacy-self-analyze

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
	@uv sync --dev
	@uv pip install -e .
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
		uv run python -m sda_detector "$(FILE)"; \
	fi

self-analyze: ## Run SDA detector on itself (dogfooding)
	uv run python -m sda_detector src/sda_detector "SDA Detector Self-Analysis"

analyze-tests: ## Run SDA detector on test suite (excluding fixtures)
	@echo "📊 Analyzing test suite for SDA compliance..."
	@echo "Domain tests:"
	@uv run python -m sda_detector tests/domain
	@echo "\nIntegration tests:"
	@uv run python -m sda_detector tests/integration

compliance-report: ## Generate full SDA compliance report
	@echo "🏛️ SDA COMPLIANCE REPORT"
	@echo "========================"
	@echo "\n📁 Source Code (src/sda_detector):"
	@uv run python -m sda_detector src/sda_detector | tail -4
	@echo "\n📁 Domain Tests:"
	@uv run python -m sda_detector tests/domain | tail -4
	@echo "\n📁 Integration Tests:"
	@uv run python -m sda_detector tests/integration | tail -4

legacy-run: ## DEPRECATED - Use 'make run' instead
	@echo "❌ legacy-run is deprecated. Use 'make run' instead."

legacy-self-analyze: ## Run original detector on itself (DEPRECATED - file no longer exists)
	@echo "❌ Original sda_detector.py has been removed. Use 'make self-analyze' instead."

clean: ## Clean up caches
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ __pycache__/
