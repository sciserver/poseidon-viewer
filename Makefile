PROJECT := viewer
CONDA := conda
CONDAFLAGS :=
COV_REPORT := html

default: qa unit-tests

qa:
	pre-commit run --all-files

unit-tests:
	python -m pytest -vv --cov=precalc --cov-report=$(COV_REPORT) -W ignore::RuntimeWarning

conda-env-update:
	$(CONDA) env update $(CONDAFLAGS) -f environment.yml

docs-build:
	jupyter-book build docs/
