init:
	pip install --upgrade -r requirements.txt

install:
	pip install --upgrade -r requirements.txt
	pip install --upgrade .

dev:
	pip install --upgrade -r requirements.txt
	pip install --upgrade -e .

test:
	pip install --upgrade flake8 pytest tox
	flake8 .
	tox

dist:
	pip install --upgrade build twine
	python -m build
	python -m twine -r polygphys dist/*
	
docs:
	pip install --upgrade -r docs/requirements.txt
	python setup.py build_sphinx
