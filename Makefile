.PHONY: run clean

VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip3

run: $(VENV)/bin/activate
	$(PYTHON) main.py

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

lint:
	echo "Linting..."
	$(PYTHON) -m pylint module1/ module2/ module3/ -r n && \
    $(PYTHON) -m pycodestyle module1/ module2/ module3/ --max-line-length=120

test:
	echo "Tests not implemented"
	# TODO

clean:
	rm -rf __pycache__
	rm -rf $(VENV)