.PHONY: build run test clean migrate-up migrate-down help

# Loading .env vars
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

BINARY_NAME=server
BUILD_DIR=build
MIGRATIONS_DIR=migrations

DB_CONNECTION="host=localhost port=5432 user=postgres password=password dbname=gng_db sslmode=disable"

all: build

build:
	@echo "Building application..."
	@mkdir -p $(BUILD_DIR)
	go build -o $(BUILD_DIR)/$(BINARY_NAME) ./cmd/server
	@echo "Build complete: $(BUILD_DIR)/$(BINARY_NAME)"

run:
	@echo "Running application..."
	go run ./cmd/server/main.go

test:
	@echo "Running tests..."
	go test -v ./...

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)
	@go clean

migrate-up:
	@echo "Running database migrations up..."
	goose -dir $(MIGRATIONS_DIR) postgres $(DB_CONNECTION) up

migrate-down:
	@echo "Running database migrations down..."
	goose -dir $(MIGRATIONS_DIR) postgres $(DB_CONNECTION) down

migrate-create:
	@echo "Creating new migration..."
	@read -p "Enter migration name: " name; \
	goose -dir $(MIGRATIONS_DIR) create $$name sql

deps:
	@echo "Installing dependencies..."
	go mod tidy
	go mod download

fmt:
	@echo "Formatting code..."
	go fmt ./...

lint:
	@echo "Linting code..."
	golangci-lint run

help:
	@echo "Available targets:"
	@echo "  build         - Build the application"
	@echo "  run           - Run the application"
	@echo "  test          - Run tests"
	@echo "  clean         - Clean build artifacts"
	@echo "  migrate-up    - Run database migrations up"
	@echo "  migrate-down  - Run database migrations down"
	@echo "  migrate-create - Create new migration"
	@echo "  deps          - Install dependencies"
	@echo "  fmt           - Format code"
	@echo "  lint          - Lint code"
	@echo "  help          - Show this help"
