init:
    pip install -r requirements.txt

install:
    pip install .

dev:
    pip install . -e

test:
    tox
    
docs:
    cd docs
    pip install -r requirements.txt
    sphinx -b html
    sphinx -b pdf
