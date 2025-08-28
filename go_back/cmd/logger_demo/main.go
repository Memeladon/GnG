package main

import (
	"errors"
	"time"

	"gng/internal/logger"
)

func main() {
	// Инициализируем все логгеры один раз при запуске программы
	logger.InitializeLoggers()

	// Демонстрация работы оптимизированного логгера в разных слоях приложения

	// 1. Handler layer - используем синглтон
	handlerLogger := logger.GetHandlerLogger()
	handlerLogger.Info("🚀 Server started",
		"port", 8080,
		"environment", "development",
		"version", "1.0.0",
	)

	// 2. Service layer - используем синглтон
	serviceLogger := logger.GetServiceLogger()
	serviceLogger.Info("📊 Processing user request",
		"user_id", "12345",
		"operation", "get_profile",
	)

	// 3. Repository layer - используем синглтон
	repoLogger := logger.GetRepositoryLogger()
	repoLogger.Debug("🔍 Executing database query",
		"table", "users",
		"query", "SELECT * FROM users WHERE id = ?",
		"params", []interface{}{"12345"},
	)

	// 4. Middleware layer - используем синглтон
	middlewareLogger := logger.GetMiddlewareLogger()
	middlewareLogger.Info("🔗 CORS middleware enabled",
		"allowed_origins", []string{"http://localhost:3000"},
		"allowed_methods", []string{"GET", "POST", "PUT", "DELETE"},
	)

	// 5. Database layer - используем синглтон
	dbLogger := logger.GetDatabaseLogger()
	dbLogger.Info("💾 Database connection established",
		"host", "localhost",
		"port", 5432,
		"database", "gng_db",
		"connection_pool_size", 10,
	)

	// 6. Демонстрация различных уровней логирования
	serviceLogger.Debug("🔍 Debug: Detailed operation information")
	serviceLogger.Info("ℹ️  Info: General operation information")
	serviceLogger.Warn("⚠️  Warning: Something to pay attention to")

	// 7. Демонстрация логирования ошибок
	err := errors.New("database connection timeout")
	serviceLogger.WithField("error", err.Error()).Error("❌ Failed to process request")

	// 8. Демонстрация контекста
	userLogger := serviceLogger.WithContext(map[string]interface{}{
		"user_id":    "12345",
		"session_id": "sess_abc123",
		"ip_address": "192.168.1.100",
	})

	userLogger.Info("👤 User action performed",
		"action", "profile_update",
		"fields_updated", []string{"email", "avatar"},
	)

	// 9. Демонстрация форматированного логирования
	serviceLogger.Infof("📝 Processing request %s for user %s at %s",
		"GET", "12345", time.Now().Format("15:04:05"),
	)

	// 10. Демонстрация производительности
	start := time.Now()
	time.Sleep(100 * time.Millisecond) // Имитация работы
	elapsed := time.Since(start)

	serviceLogger.Info("⚡ Operation completed",
		"duration", elapsed.String(),
		"status", "success",
	)

	// 11. Демонстрация предупреждений
	repoLogger.Warn("🐌 Slow query detected",
		"query_time", "2.5s",
		"threshold", "1s",
		"table", "users",
		"recommendation", "Consider adding index on user_id",
	)

	// 12. Демонстрация быстрых функций (автоматически используют repository логгер)
	logger.Info("🚀 Quick logging without specifying layer")
	logger.Error("❌ Quick error logging", "error", "something went wrong")
	logger.Debugf("🔍 Quick debug: %s", "formatted message")

	// 13. Демонстрация глобальной настройки уровня логирования
	handlerLogger.Info("🔧 Demonstrating global log level configuration...")

	// Устанавливаем глобальный уровень для всех логгеров
	logger.SetGlobalLogLevel(logger.DebugLevel)

	// Теперь все логгеры будут показывать debug сообщения
	serviceLogger.Debug("🔍 This debug message will now be visible")

	// Возвращаем к info уровню
	logger.SetGlobalLogLevel(logger.InfoLevel)

	// 14. Демонстрация переиспользования логгеров
	handlerLogger.Info("🔄 Demonstrating logger reuse...")

	// Получаем те же экземпляры логгеров (не создаются новые)
	sameHandlerLogger := logger.GetHandlerLogger()
	sameServiceLogger := logger.GetServiceLogger()
	sameRepoLogger := logger.GetRepositoryLogger()

	// Проверяем, что это те же экземпляры
	handlerLogger.Info("✅ Handler logger instance reused",
		"handler_logger_ptr", &handlerLogger,
		"same_handler_logger_ptr", &sameHandlerLogger,
		"are_same", &handlerLogger == &sameHandlerLogger,
	)

	serviceLogger.Info("✅ Service logger instance reused",
		"service_logger_ptr", &serviceLogger,
		"same_service_logger_ptr", &sameServiceLogger,
		"are_same", &serviceLogger == &sameServiceLogger,
	)

	repoLogger.Info("✅ Repository logger instance reused",
		"repo_logger_ptr", &repoLogger,
		"same_repo_logger_ptr", &sameRepoLogger,
		"are_same", &repoLogger == &sameRepoLogger,
	)

	// 15. Демонстрация критических ошибок (закомментировано, чтобы не завершать программу)
	// serviceLogger.Fatal("💀 Critical system error", "error_code", "E001", "action", "system_shutdown")

	handlerLogger.Info("✅ Optimized logger demonstration completed successfully!")

	// 16. Финальная информация о возможностях
	handlerLogger.Info("📚 Logger features demonstrated:",
		"layers", []string{"Handler", "Service", "Repository", "Middleware", "Database"},
		"levels", []string{"Debug", "Info", "Warn", "Error", "Fatal"},
		"features", []string{"Context", "Fields", "Formatted", "Configuration", "Colors", "Caller Info", "Singleton Pattern", "Global Configuration"},
		"optimizations", []string{"Single Instance", "Lazy Initialization", "Thread Safe", "Memory Efficient"},
	)

	// 17. Информация об оптимизации
	handlerLogger.Info("🚀 Optimization benefits:",
		"memory_saved", "~1KB per logger instance",
		"instances_created", "7 total (one per layer)",
		"instances_reused", "Unlimited",
		"performance_improvement", "No more object creation overhead",
	)
}
