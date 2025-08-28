# Pocketknife CLI - Simple Makefile for macOS and Linux

.PHONY: help install clean

# Default target
help:
	@echo "Pocketknife CLI - Available Commands:"
	@echo ""
	@echo "  make install    Install/update pocketknife globally"
	@echo "  make clean      Clean build artifacts"
	@echo ""

# Install/update globally using pipx (recommended) or pip as fallback
install:
	@echo "Installing/updating pocketknife..."
	@git pull || true
	@if command -v pipx >/dev/null 2>&1; then \
		pipx install . --force; \
		echo "✅ Pocketknife installed/updated via pipx"; \
	else \
		pip3 install . --user --break-system-packages --force-reinstall; \
		echo "✅ Pocketknife installed/updated via pip"; \
		echo "💡 Consider installing pipx: brew install pipx"; \
	fi
	@echo "Run 'pocketknife --help' to get started"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf __pycache__/
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned"