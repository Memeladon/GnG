.PHONY: build run test clean migrate-up migrate-down help

# Variables
BINARY_NAME=server
BUILD_DIR=build
MIGRATIONS_DIR=migrations

# Database connection string from environment variables
DB_CONNECTION="host=$(DB_HOST) port=$(DB_PORT) user=$(DB_USER) password=$(DB_PASSWORD) dbname=$(DB_NAME) sslmode=$(DB_SSLMODE)"

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
	@echo "  migrate-up    - Run database migrations up (requires DB_* env vars)"
	@echo "  migrate-down  - Run database migrations down (requires DB_* env vars)"
	@echo "  migrate-create - Create new migration"
	@echo "  deps          - Install dependencies"
	@echo "  fmt           - Format code"
	@echo "  lint          - Lint code"
	@echo "  help          - Show this help"
	@echo ""
	@echo "Required environment variables for database operations:"
	@echo "  DB_HOST       - Database host"
	@echo "  DB_PORT       - Database port"
	@echo "  DB_USER       - Database user"
	@echo "  DB_PASSWORD   - Database password"
	@echo "  DB_NAME       - Database name"
	@echo "  DB_SSLMODE    - SSL mode (optional, defaults to 'disable')"
