package logger

import (
	"errors"
	"time"
)

// ExampleUsage демонстрирует, как использовать логгер в разных слоях приложения
func ExampleUsage() {
	handlerLogger := NewHandlerLogger()
	handlerLogger.Info("User request received", "user_id", "12345", "endpoint", "/api/users")

	serviceLogger := NewServiceLogger()
	serviceLogger.WithField("operation", "user_creation").Info("Creating new user")

	repoLogger := NewRepositoryLogger()
	repoLogger.WithContext(map[string]interface{}{
		"table":  "users",
		"query":  "SELECT * FROM users WHERE id = ?",
		"params": []interface{}{12345},
	}).Debug("Executing database query")

	err := errors.New("database connection failed")
	serviceLogger.WithField("error", err.Error()).Error("Failed to process user request")

	repoLogger.Warn("Slow query detected",
		"query_time", "2.5s",
		"threshold", "1s",
		"table", "users",
	)

	handlerLogger.Debug("Request headers", "headers", map[string]string{
		"User-Agent": "Mozilla/5.0",
		"Accept":     "application/json",
	})

	start := time.Now()
	elapsed := time.Since(start)
	serviceLogger.Info("Operation completed", "duration", elapsed.String())
}

// ExampleMiddlewareLogger показывает, как использовать логгер в промежуточном ПО
func ExampleMiddlewareLogger() {
	middlewareLogger := NewMiddlewareLogger()

	middlewareLogger.Info("Middleware initialized",
		"middleware", "cors",
		"enabled", true,
	)

	middlewareLogger.Debug("Processing request",
		"method", "GET",
		"path", "/api/users",
		"ip", "192.168.1.1",
	)
}

// ExampleDatabaseLogger показывает, как использовать логгер в операциях с базой данных
func ExampleDatabaseLogger() {
	dbLogger := NewDatabaseLogger()

	dbLogger.Info("Database connection established",
		"host", "localhost",
		"port", 5432,
		"database", "gng_db",
	)

	dbLogger.Debug("Executing transaction",
		"transaction_id", "tx_123",
		"operations", 3,
	)

	dbLogger.Warn("Connection pool reaching limit",
		"current_connections", 45,
		"max_connections", 50,
	)
}
