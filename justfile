# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

set shell := ["bash", "-uc"]
venv := ".venv"

default:
    @just --list --unsorted \
        --list-heading $'\033[1mAVIN DEV COMMANDS\033[0m\n\n' \
        --list-prefix '  → '

# ----------------------------------------------------------------------------
# Environment
# ----------------------------------------------------------------------------

# Create local cache dir
[group('Environment')]
cache:
    mkdir -p .cache

# Create python venv if missing (.venv)
[group('Environment')]
venv:
    uv venv

# Install AVIN in editable mode
[group('Environment')]
install: venv cache
    uv pip install -e .

# Install AVIN with dev dependencies
[group('Environment')]
install-dev: venv cache
    uv pip install -e ".[dev]"
    just install-tbank


# Install T-Bank SDK from custom registry
[group('Environment')]
install-tbank: venv
    uv pip install t-tech-investments --extra-index-url \
        https://opensource.tbank.ru/api/v4/projects/238/packages/pypi/simple

# ----------------------------------------------------------------------------
# Code quality
# ----------------------------------------------------------------------------

# Fix imports
[group('Code quality')]
imports:
    uv run ruff check --select I --fix avin tests

# Format code
[group('Code quality')]
fmt:
    uv run ruff format avin tests

# Run ruff linter
[group('Code quality')]
lint:
    uv run ruff check avin tests

# Run mypy type check
[group('Code quality')]
type:
    uv run mypy avin

# ----------------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------------

# Run unit tests
[group('Tests')]
test:
    uv run pytest -m "not integration and not slow"

# Run unit tests with stdout
[group('Tests')]
test-s:
    uv run pytest -m "not integration and not slow" -s

# Run integration tests
[group('Tests')]
integration:
    uv run pytest -m integration

# Run slow tests
[group('Tests')]
slow:
    uv run pytest -m slow

# Run smoke tests
[group('Tests')]
smoke:
    uv run pytest -m smoke -q

# Run all tests
[group('Tests')]
all:
    uv run pytest tests

# Run test coverage
[group('Tests')]
cov:
    pytest --cov=avin --cov-report=term-missing

# ----------------------------------------------------------------------------
# Benchmarks
# ----------------------------------------------------------------------------

# Bench build footprint from ticks
[group('Benchmarks')]
bench-footprint:
    uv run python bench/footprint_builder.py

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

# Commit all changes
[group('Project')]
commit-all message:
    git add .
    git commit -m "{{message}}"

# Remove caches
[group('Project')]
clean:
    rm -rf *.egg-info
    rm -rf .cache
    rm -rf .coverage
    rm -rf .mypy_cache
    rm -rf .pytest_cache
    rm -rf .ruff_cache
    rm -rf avin.zip
    rm -rf coverage.xml
    rm -rf htmlcov
    rm -rf build
    rm -rf dist
    uv run ruff clean || true

# Remove caches and .venv
[group('Project')]
clean-all:
    just clean
    rm -rf {{venv}}/

# Create avin.zip from HEAD
[group('Project')]
archive:
    git archive --format zip HEAD -o avin.zip

# Checkhealth for tools?
[group('Project')]
doctor:
    python3 scripts/doctor.py


# ----------------------------------------------------------------------------
# Launchers
# ----------------------------------------------------------------------------

# Start avin-gui
[group('Launchers')]
gui:
    uv run avin-gui
