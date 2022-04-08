.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: run
run:
	cd ./app && uvicorn main:tutorial_app --reload

.PHONY: black
black:
	black .

.PHONY: lint
lint:
	pylint ./app --rcfile=./.pylintrc

.PHONY: security
security:
	safety check

.PHONY: test
test:
	pytest ./app
