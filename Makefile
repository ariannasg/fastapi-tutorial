.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: run
run:
	uvicorn main:app --reload

.PHONY: black
black:
	black .

.PHONY: lint
lint:
	pylint ./

.PHONY: security
security:
	safety check
