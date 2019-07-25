PYTHON_BIN ?= python

format: isort black

black:
	'$(PYTHON_BIN)' -m black --target-version py36 --exclude '/(\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|_build|buck-out|build|dist|node_modules|webpack_bundles)/' .

isort:
	'$(PYTHON_BIN)' -m isort -rc src
	'$(PYTHON_BIN)' -m isort -rc tests

venv: requirements.txt
	'$(PYTHON_BIN)' -m pip install -r requirements.txt

%.txt: %.in
	'$(PYTHON_BIN)' -m piptools compile --generate-hashes $<
