# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

set shell := ["bash", "-uc"]
venv := ".venv"
python := venv + "/bin/python"

default:
    @just --list --unsorted \
        --list-heading $'\033[1mAVIN DEV COMMANDS\033[0m\n\n' \
        --list-prefix '  → '

# ----------------------------------------------------------------------------
# Environment
# ----------------------------------------------------------------------------

# Create python venv if missing (.venv)
[group('Environment')]
venv:
    @if [ ! -d "{{venv}}" ]; then \
        python3 -m venv {{venv}}; \
        {{venv}}/bin/python -m pip install --upgrade pip; \
    fi

# Install AVIN in editable mode
[group('Environment')]
install: venv
    {{python}} -m pip install -e .

# Install AVIN with dev dependencies
[group('Environment')]
install-dev: venv
    {{python}} -m pip install -e ".[dev]"
    just install-tbank

# Install T-Bank SDK from custom registry
[group('Environment')]
install-tbank: venv
    {{python}} -m pip install t-tech-investments --index-url https://opensource.tbank.ru/api/v4/projects/238/packages/pypi/simple

# ----------------------------------------------------------------------------
# Code quality
# ----------------------------------------------------------------------------

# Fix imports
[group('Code quality')]
imports:
    {{python}} -m ruff check --select I --fix avin tests

# Format code
[group('Code quality')]
fmt:
    {{python}} -m ruff format avin tests

# Run ruff linter
[group('Code quality')]
lint:
    {{python}} -m ruff check avin tests

# Run mypy type check
[group('Code quality')]
type:
    {{python}} -m mypy avin --no-namespace-packages

# ----------------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------------

# Run unit tests
[group('Tests')]
test:
    {{python}} -m pytest -m "not (integration or slow)"

# Run unit tests with stdout
[group('Tests')]
test-s:
    {{python}} -m pytest -m "not (integration or slow)" -s

# Run one test file
[group('Tests')]
test-file file:
    {{python}} -m pytest {{file}} -s

# Run integration tests
[group('Tests')]
integration:
    {{python}} -m pytest -m integration

# Run slow tests
[group('Tests')]
slow:
    {{python}} -m pytest -m slow

# Run all tests
[group('Tests')]
all-test:
    just test
    just integration
    just slow

# ----------------------------------------------------------------------------
# Benchmarks
# ----------------------------------------------------------------------------

# Bench build footprint from ticks
[group('Benchmarks')]
bench-footprint:
    {{venv}}/bin/python bench/footprint_builder.py

# ----------------------------------------------------------------------------
# Project
# ----------------------------------------------------------------------------

# Go AVIN development (start venv, setup nvim)
[group('Project')]
go:
    . {{venv}}/bin/activate && nvim -c AvinDevPy

# Fix imports, format, lint, typecheck and test
[group('Project')]
pre-commit:
    just imports
    just fmt
    just lint
    just type
    just test

# Remove caches
[group('Project')]
clean:
    rm -rf .mypy_cache
    rm -rf .pytest_cache
    rm -rf .ruff_cache
    rm -rf htmlcov
    rm -rf .coverage
    rm -rf coverage.xml
    rm -rf avin.zip
    {{python}} -m ruff clean || true

# Remove caches and .venv
[group('Project')]
clean-all:
    just clean
    rm -rf {{venv}}/

# Create avin.zip from HEAD
[group('Project')]
archive:
    git archive --format zip HEAD -o avin.zip
