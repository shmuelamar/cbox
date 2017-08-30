SHELL := $(shell which bash)
PROJECT := cbox
ACTIVATE_VENV = source activate ${PROJECT}
CONDA_REQS := "conda-requirements.txt"
TEST_REQS := "test-requirements.txt"

setup-env:
	-conda create -y -n ${PROJECT} ipython
	${ACTIVATE_VENV} && \
	  conda install -y --file ${CONDA_REQS}

test-setup: setup-env
	${ACTIVATE_VENV} && pip install -r ${TEST_REQS}

test: clean validate
	${ACTIVATE_VENV} && \
	export PYTHONPATH=./$(PROJECT):$$PYTHONPATH && \
	py.test --cov $(PROJECT)/ --cov-report=term --cov-report=html --junitxml=nosetests.xml -s -v tests/test_*.py

clean:
	find ./tests/ -name '*.py[co]' -exec rm {} \;
	rm -rf build dist $(PROJECT).egg-info
	rm -f nosetests.xml
	rm -f .coverage
	rm -rf .cache/
	rm -rf htmlcov/

validate:
	${ACTIVATE_VENV} && flake8 setup.py $(PROJECT)/ tests/ examples/

all:
	$(error please pick a target)

.PHONY: clean validate
