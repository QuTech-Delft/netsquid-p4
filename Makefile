PYTHON       = python3
SOURCEDIR    = netsquid_p4
TESTDIR      = tests
COVREP       = term
MINCOV       = 0
PIP_FLAGS    = --extra-index-url=https://${NETSQUIDPYPI_USER}:${NETSQUIDPYPI_PWD}@pypi.netsquid.org

help:
	@echo "requirements      Install the package requirements."
	@echo "dev-requirements  Install extra requirements for development."
	@echo "examples          Run all the examples."
	@echo "tests             Run the tests."
	@echo "coverage          Print the coverage report."
	@echo "cov-html          Open the coverage report produced using `make tests COVREP=html`."
	@echo "flake8            Run the flake8 linter."
	@echo "pylint            Run the pylint linter."
	@echo "clean             Removes all temporary files (such as .pyc and __pycache__)."
	@echo "verify            Verify the project by running tests and linters."

_check_variables:
ifndef NETSQUIDPYPI_USER
	$(error Set the environment variable NETSQUIDPYPI_USER before uploading)
endif
ifndef NETSQUIDPYPI_PWD
	$(error Set the environment variable NETSQUIDPYPI_PWD before uploading)
endif

requirements: _check_variables
	@$(PYTHON) -m pip install --upgrade -r requirements.txt ${PIP_FLAGS}

dev-requirements: _check_variables
	@$(PYTHON) -m pip install --upgrade -r dev-requirements.txt ${PIP_FLAGS}

examples:
	@$(PYTHON) -m examples.run_examples > /dev/null && echo "Examples OK!" || (echo "Examples failed!" && /bin/false)

tests:
	@$(PYTHON) -m pytest -v --cov=${SOURCEDIR} --cov-report=${COVREP} ${TESTDIR}

coverage:
	@$(PYTHON) -m coverage report --fail-under=${MINCOV}

cov-html:
	@xdg-open htmlcov/index.html

flake8:
	@$(PYTHON) -m flake8 ${SOURCEDIR} ${TESTDIR}

pylint:
	@$(PYTHON) -m pylint ${SOURCEDIR}

clean:
	@/usr/bin/find . -name '*.pyc' -delete
	@/usr/bin/find . -name __pycache__ -prune -exec rm -rf "{}" \;
	@/usr/bin/rm -rf .pytest_cache
	@/usr/bin/rm -f .coverage
	@/usr/bin/rm -rf htmlcov

_verified:
	@echo "The package has been successfully verified"

verify: clean requirements dev-requirements tests coverage flake8 pylint _verified

.PHONY: _check_variables requirements dev-requirements examples tests coverage cov-html flake8 pylint clean verify _verified
