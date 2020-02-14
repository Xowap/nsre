PYTHON_BIN ?= poetry run python
ENV ?= pypitest

install:
	poetry install

format: isort black

black: install
	$(PYTHON_BIN) -m black --target-version py36 --exclude '/(\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|node_modules|webpack_bundles)/' .

isort: install
	$(PYTHON_BIN) -m isort -rc src
	$(PYTHON_BIN) -m isort -rc tests

test: export PYTHONPATH=$(realpath src)

test: install
	$(PYTHON_BIN) -m pytest
