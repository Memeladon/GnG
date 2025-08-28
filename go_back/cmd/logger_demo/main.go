package main

import (
	"errors"
	"time"

	logger "gng/internal/utils"
)

func main() {
	// Создаем один логгер для всего приложения
	log := logger.NewLogger()

	// Демонстрация работы упрощенного логгера

	// 1. Базовое логирование
	log.Info("🚀 Server started",
		"port", 8080,
		"environment", "development",
		"version", "1.0.0",
	)

	// 2. Логирование с контекстом
	userLogger := log.WithField("user_id", "12345")
	userLogger.Info("📊 Processing user request",
		"operation", "get_profile",
	)

	// 3. Различные уровни логирования
	log.Debug("🔍 Debug: Detailed operation information")
	log.Info("ℹ️  Info: General operation information")
	log.Warn("⚠️  Warning: Something to pay attention to")

	// 4. Логирование ошибок
	err := errors.New("database connection timeout")
	log.WithField("error", err.Error()).Error("❌ Failed to process request")

	// 5. Логирование с несколькими полями
	log.WithFields(map[string]interface{}{
		"user_id":    "12345",
		"session_id": "sess_abc123",
		"ip_address": "192.168.1.100",
	}).Info("👤 User action performed",
		"action", "profile_update",
		"fields_updated", []string{"email", "avatar"},
	)

	// 6. Форматированное логирование
	log.Infof("📝 Processing request %s for user %s at %s",
		"GET", "12345", time.Now().Format("15:04:05"),
	)

	// 7. Демонстрация производительности
	start := time.Now()
	time.Sleep(100 * time.Millisecond) // Имитация работы
	elapsed := time.Since(start)

	log.Info("⚡ Operation completed",
		"duration", elapsed.String(),
		"status", "success",
	)

	// 8. Демонстрация предупреждений
	log.Warn("🐌 Slow query detected",
		"query_time", "2.5s",
		"threshold", "1s",
		"table", "users",
		"recommendation", "Consider adding index on user_id",
	)

	// 9. Демонстрация базы данных
	log.Info("💾 Database connection established",
		"host", "localhost",
		"port", 5432,
		"database", "gng_db",
		"connection_pool_size", 10,
	)

	// 10. Демонстрация middleware
	log.Info("🔗 CORS middleware enabled",
		"allowed_origins", []string{"http://localhost:3000"},
		"allowed_methods", []string{"GET", "POST", "PUT", "DELETE"},
	)

	// 11. Демонстрация repository
	log.Debug("🔍 Executing database query",
		"table", "users",
		"query", "SELECT * FROM users WHERE id = ?",
		"params", []interface{}{"12345"},
	)

	// 12. Демонстрация завершения
	log.Info("✅ Logger demo completed successfully")
}
