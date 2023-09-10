VIRTUAL_ENV ?= venv
PIP=$(VIRTUAL_ENV)/bin/pip
PYTHON=$(VIRTUAL_ENV)/bin/python
ISORT=$(VIRTUAL_ENV)/bin/isort
FLAKE8=$(VIRTUAL_ENV)/bin/flake8
BLACK=$(VIRTUAL_ENV)/bin/black
PYTEST=$(VIRTUAL_ENV)/bin/pytest
TOX=$(VIRTUAL_ENV)/bin/tox
PYTHON_MAJOR_VERSION=3
PYTHON_MINOR_VERSION=10
PYTHON_VERSION=$(PYTHON_MAJOR_VERSION).$(PYTHON_MINOR_VERSION)
PYTHON_MAJOR_MINOR=$(PYTHON_MAJOR_VERSION)$(PYTHON_MINOR_VERSION)
PYTHON_WITH_VERSION=python$(PYTHON_VERSION)
SOURCES=laboralkutxa/ tests/


$(VIRTUAL_ENV):
	$(PYTHON_WITH_VERSION) -m venv $(VIRTUAL_ENV)
	$(PIP) install -e ".[dev]"

virtualenv: $(VIRTUAL_ENV)

test: $(VIRTUAL_ENV)
	$(TOX)

pytest: $(VIRTUAL_ENV)
	$(PYTEST) --cov laboralkutxa/ --cov-report term --cov-report html tests/

lint/isort: $(VIRTUAL_ENV)
	$(ISORT) --check-only --diff $(SOURCES)

lint/flake8: $(VIRTUAL_ENV)
	$(FLAKE8) $(SOURCES)

lint/black: $(VIRTUAL_ENV)
	$(BLACK) --check $(SOURCES)

format/isort: $(VIRTUAL_ENV)
	$(ISORT) $(SOURCES)

format/black: $(VIRTUAL_ENV)
	$(BLACK) --verbose $(SOURCES)

lint: lint/isort lint/flake8 lint/black

format: format/isort format/black

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +

clean/all: clean
	rm -rf $(VIRTUAL_ENV)

release/version/check:
ifndef VERSION
	$(error VERSION is not set)
endif

release/version/update: release/version/check
	sed --regexp-extended 's/version = "(.+)"/version = "$(VERSION)"/' --in-place pyproject.toml

release/commit_and_tag: release/version/check
	git commit -a -m ":bookmark: $(VERSION)"
	git tag -a $(VERSION) -m ":bookmark: $(VERSION)"

release/push:
	git push
	git push --tags

release: release/version/update release/commit_and_tag release/push
