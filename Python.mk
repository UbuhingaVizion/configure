PACKAGE_COVERAGE=$(PACKAGE_DIR)

PYPI_REPO?=
PYPI_REPO_USERNAME?=
PYPI_REPO_PASSWORD?=

ifneq "${PYPI_REPO_USERNAME}" ""
    TWINE_OPS+= --username "$(PYPI_REPO_USERNAME)" --password "$(PYPI_REPO_PASSWORD)"
else
	TWINE_OPS?=
endif

ifneq "${PYPI_REPO}" ""
    TWINE_OPS+= --repository-url "${PYPI_REPO}"
endif


# Minimum coverage
COVER_MIN_PERCENTAGE=70

# Recipes ************************************************************************************
.PHONY: run-tests build clean beautify publish requirements all-requirements \
	flake autopep sort-imports relative-imports python-help prepush pull-request

python-help:
	@echo "Python options"
	@echo "-----------------------------------------------------------------------"
	@echo "python-help:             	This help"
	@echo "run-tests:               	Run tests with coverage"
	@echo "clean:                   	Clean compiled files"
	@echo "flake:                   	Run Flake8"
	@echo "prepush:                 	Helper to run before to push to repo"
	@echo "autopep:                 	Reformat code using PEP8"
	@echo "sort-imports:            	Sort imports"
	@echo "beautify:                	Reformat code (autopep + sort-imports)"
	@echo "build:                   	Build python package"
	@echo "publish:                 	Publish new version in repository"
	@echo "requirements:            	Install package base requirements"
	@echo "requirements-dev:        	Install development package requirements"
	@echo "requirements-lint:       	Install lint requirements"
	@echo "requirements-package:    	Install requirements in order to build and publish package"
	@echo "requirements-docs:       	Install documentation requirements"
	@echo "all-requirements:	    	Install all requirements"
	@echo "get-version:			    	Prints current version"
	@echo "increase-version.{level}:	Increase version using level which can be 'bugfix', 'minor' or 'major'"


# Code recipes
requirements:
	@echo "Installing base requirements..."
	python3 -m pip install -r requirements.txt

requirements-%: requirements
	@echo "Installing requirements ${*}..."
	python3 -m pip install -r requirements-${*}.txt

all-requirements: requirements requirements-lint requirements-package \
				  requirements-dev
	@echo "All requirements installed"


build:
	python3 setup.py bdist_wheel

publish: build
	@echo "Publishing new ${PACKAGE_NAME} version on PyPi..."
	@echo ${TWINE_OPS}
	twine upload $(TWINE_OPS) dist/*.whl

autopep:
	autopep8 --max-line-length 120 -a -r -j 8 -i .

flake:
	@echo "Running flake8 tests..."
	flake8 ${PACKAGE_COVERAGE}.py
	flake8 tests.py
	# flake8 docs/source
	isort -c ${ISORT_PARAMS} ${PACKAGE_COVERAGE}.py
	isort -c ${ISORT_PARAMS} tests.py
	isort -c ${ISORT_PARAMS} setup.py


run-tests:
	@echo "Running unit tests..."
	pytest -v --cov-report term-missing --cov-fail-under=${COVER_MIN_PERCENTAGE} --cov=${PACKAGE_COVERAGE} --exitfirst tests.py

prepush: flake run-tests

pull-request: flake run-tests

sort-imports:
	isort ${ISORT_PARAMS} ${PACKAGE_COVERAGE}.py
	isort ${ISORT_PARAMS} tests.py
	isort ${ISORT_PARAMS} setup.py setup_utils.py
	# isort ${ISORT_PARAMS} docs/source

relative-imports:
	absolufy-imports --never $(shell find . -name "*.py" -not -path "./.build/*")

beautify: autopep relative-imports sort-imports

# Clean files and directories created when testing or running pyspark
clean:
	@echo "Cleaning compiled files..."
	find . | grep -E "(__pycache__|\.pyc|\.pyo|pytest_cache)$ " | xargs rm -rf
	@echo "Cleaning distribution files..."
	rm -rf dist
	@echo "Cleaning build files..."
	rm -rf build
	@echo "Cleaning egg info files..."
	rm -rf ${PACKAGE_NAME}.egg-info
	@echo "Cleaning coverage files..."
	rm -f .coverage


increase-version.%:
	python3 setup_utils.py increase-version --level ${*}

get-version:
	@python3 setup_utils.py get-version

check-setup:
	@python3 setup.py check -r -s -m
