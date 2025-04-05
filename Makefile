# Variables
REPO_NAME ?= zim95
USER_NAME ?= zim95
NAMESPACE ?= browseterm-new
HOST_DIR ?= /Users/namahshrestha/projects/cert-manager


# Development
dev_build:
	./scripts/development/development-build.sh $(USER_NAME) $(REPO_NAME)

dev_setup:
	./scripts/development/development-setup.sh $(NAMESPACE) $(HOST_DIR)

dev_teardown:
	./scripts/development/development-teardown.sh $(NAMESPACE)

# Production
prod_build:
	./scripts/deployment/development-build.sh $(USER_NAME) $(REPO_NAME)

prod_setup:
	./scripts/deployment/development-setup.sh $(NAMESPACE) $(HOST_DIR)

prod_teardown:
	./scripts/deployment/development-teardown.sh $(NAMESPACE)

.PHONY: dev_build dev_setup dev_teardown prod_build prod_setup prod_teardown
