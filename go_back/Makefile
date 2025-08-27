.PHONY: build run test clean migrate-up migrate-down help

# Variables
BINARY_NAME=server
BUILD_DIR=build
MIGRATIONS_DIR=migrations

# Database connection string (update as needed)
DB_CONNECTION="host=localhost port=5432 user=postgres password=password dbname=gng_db sslmode=disable"

# Default target
all: build

# Build the application
build:
	@echo "Building application..."
	@mkdir -p $(BUILD_DIR)
	go build -o $(BUILD_DIR)/$(BINARY_NAME) ./cmd/server
	@echo "Build complete: $(BUILD_DIR)/$(BINARY_NAME)"

# Run the application
run:
	@echo "Running application..."
	go run ./cmd/server/main.go

# Run tests
test:
	@echo "Running tests..."
	go test -v ./...

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)
	@go clean

# Run database migrations up
migrate-up:
	@echo "Running database migrations up..."
	goose -dir $(MIGRATIONS_DIR) postgres $(DB_CONNECTION) up

# Run database migrations down
migrate-down:
	@echo "Running database migrations down..."
	goose -dir $(MIGRATIONS_DIR) postgres $(DB_CONNECTION) down

# Create new migration
migrate-create:
	@echo "Creating new migration..."
	@read -p "Enter migration name: " name; \
	goose -dir $(MIGRATIONS_DIR) create $$name sql

# Install dependencies
deps:
	@echo "Installing dependencies..."
	go mod tidy
	go mod download

# Format code
fmt:
	@echo "Formatting code..."
	go fmt ./...

# Lint code
lint:
	@echo "Linting code..."
	golangci-lint run

# Show help
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
