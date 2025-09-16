.DEFAULT_GOAL:=help
SHELL=bash
VENV=.venv
APP=~/.local/bin/avin-data

.venv: ## Create python virtual environment & install requirements
	python3 -m venv $(VENV)
	$(MAKE) requirements

requirements: .venv ## Install/Update Python project requirements
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install --upgrade -r requirements.txt

dev: .venv  ## Activate venv & start neovim for this project
	source .venv/bin/activate && nvim -c AvinDevPy

check: ## Run ruff, mypy clippy
	ruff check avin/** --select I --fix
	mypy avin

fmt: ## Run ruff format
	ruff format

test: ## Run pytests
	python3 -m venv $(VENV) && pytest tests

pre-commit: ## Make check, fmt, test
	$(MAKE) check
	$(MAKE) fmt
	$(MAKE) test

build: .venv ## Build the project
	source .venv/bin/activate && flit build --no-use-vcs
	source .venv/bin/activate && pyinstaller avin/bin/avin_data_cli.py \
		--onefile \
		--specpath build \
		--name avin-data

publish: ## Publish pypi.org
	echo "todo!"

install: build ## Install the project
	rm -rf $(APP)
	install -Dm755 dist/avin-data $(APP)
	install -Dm644 res/config.toml ~/.config/avin/config.toml

clean: ## Clean up caches, build artifacts, and the venv
	ruff clean
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .venv/
	rm -rf build
	rm -rf dist

T1="\033[1m"
T2="\033[0m"
B0="\033[32m"
B1="    \033[32m"
B2="\033[0m"
help:
	@echo -e $(T1)Usage:$(T2) make [$(B0)target$(B2)]
	@echo ""
	@echo -e $(T1)Virtual environment:$(T2)
	@echo -e $(B1).venv$(B2)"          Create python .venv"
	@echo -e $(B1)requirements$(B2)"   Install/Update python requirements"
	@echo -e $(B1)dev$(B2)"            Activate venv & start neovim"
	@echo ""
	@echo -e $(T1)Code quality:$(T2)
	@echo -e $(B1)check$(B2)"          Linting ruff, mypy"
	@echo -e $(B1)fmt$(B2)"            Autoformatting"
	@echo -e $(B1)test$(B2)"           Run pytests"
	@echo -e $(B1)pre-commit$(B2)"     Make all code quality"
	@echo ""
	@echo -e $(T1)Build project:$(T2)
	@echo -e $(B1)build$(B2)"          Build python and rust sources"
	@echo -e $(B1)publish$(B2)"        Publish package pypi.org"
	@echo -e $(B1)install$(B2)"        Install the project"
	@echo -e $(B1)clean$(B2)"          Clean the project"
	@echo ""
	@echo -e $(B1)help$(B2)"           Display this help message"
