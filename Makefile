.DEFAULT_GOAL:=help
SHELL=bash
VENV=.venv
ACTIVATE_ENV=source ~/avin/.venv/bin/activate

venv:
	python3 -m venv $(VENV)
	$(MAKE) requirements

requirements: .venv
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install --upgrade -r requirements.txt

dev: .venv
	$(ACTIVATE_ENV) && nvim -c AvinDevPy

check:
	ruff check --select I --fix
	mypy avin --no-namespace-packages

fmt:
	ruff format

test:
	pytest tests

pre-commit:
	$(MAKE) check
	$(MAKE) fmt
	$(MAKE) test

clean:
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .venv/
	ruff clean


T1="\033[1m"
T2="\033[0m"
B0="\033[32m"
B1="    \033[32m"
B2="\033[0m"
help:
	@echo -e $(T1)Usage:$(T2) make [$(B0)target$(B2)]
	@echo ""
	@echo -e $(T1)Virtual environment:$(T2)
	@echo -e $(B1)venv$(B2)"           Create python .venv"
	@echo -e $(B1)requirements$(B2)"   Install/Update python requirements"
	@echo -e $(B1)dev$(B2)"            Activate venv & start neovim"
	@echo ""
	@echo -e $(T1)Code quality:$(T2)
	@echo -e $(B1)check$(B2)"          Linting ruff, mypy"
	@echo -e $(B1)fmt$(B2)"            Autoformatting"
	@echo -e $(B1)test$(B2)"           Run pytests"
	@echo -e $(B1)pre-commit$(B2)"     Make all code quality"
	@echo ""
	@echo -e $(T1)Help:$(T2)
	@echo -e $(B1)help$(B2)"           Display this help message"

