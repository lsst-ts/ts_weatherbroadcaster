.PHONY: help
help:
	@echo "Make targets for weatherbroadcaster"
	@echo "make init - Set up dev environment"
	@echo "make docs - Build documentation"
	@echo "make run - Start a local development instance"
	@echo "make update - Update pinned dependencies and run make init"
	@echo "make update-deps - Update pinned dependencies"

.PHONY: init
init:
	uv sync --frozen --all-groups
	uv run pre-commit install

.PHONY: run
run:
	tox run -e run

.PHONY: docs
docs:
	tox run -e docs

.PHONY: update
update: update-deps init

.PHONY: update-deps
update-deps:
	uv lock --upgrade
	uv run --only-group=lint pre-commit autoupdate
	./scripts/update-uv-version.sh
