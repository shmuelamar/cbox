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
	py.test --cov $(PROJECT)/ --cov-report=term --cov-report=html --junitxml=report.xml -s -v tests/test_*.py

clean:
	find ./tests/ -name '*.py[co]' -exec rm {} \;
	rm -rf build dist $(PROJECT).egg-info
	rm -f nosetests.xml
	rm -f .coverage
	rm -rf .cache/
	rm -rf htmlcov/

validate:
	${ACTIVATE_VENV} && flake8 setup.py $(PROJECT)/ tests/ examples/

build-dist: clean
	${ACTIVATE_VENV} && \
	export PYTHONPATH=./$(PROJECT):$$PYTHONPATH && \
	python setup.py sdist bdist_wheel
	gpg --detach-sign -a dist/cbox-*.tar.gz
	gpg --detach-sign -a dist/cbox-*.whl

upload-pypi: clean test build-dist
	twine upload dist/cbox-${CBOX_VERSION}.tar.gz dist/cbox-${CBOX_VERSION}.tar.gz.asc
	twine upload dist/cbox-${CBOX_VERSION}-py3-none-any.whl dist/cbox-${CBOX_VERSION}-py3-none-any.whl.asc

all:
	$(error please pick a target)

.PHONY: clean validate
