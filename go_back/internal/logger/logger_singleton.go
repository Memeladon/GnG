package logger

import (
	"sync"
)

var (
	// Глобальные экземпляры логгеров для каждого слоя
	handlerLoggerInstance    *Logger
	serviceLoggerInstance    *Logger
	repositoryLoggerInstance *Logger
	middlewareLoggerInstance *Logger
	databaseLoggerInstance   *Logger
	configLoggerInstance     *Logger
	utilsLoggerInstance      *Logger

	// Мьютексы для потокобезопасной инициализации
	handlerLoggerOnce    sync.Once
	serviceLoggerOnce    sync.Once
	repositoryLoggerOnce sync.Once
	middlewareLoggerOnce sync.Once
	databaseLoggerOnce   sync.Once
	configLoggerOnce     sync.Once
	utilsLoggerOnce      sync.Once

	// Глобальная конфигурация
	globalConfig *LoggerConfig
	configOnce   sync.Once
)

// GetHandlerLogger возвращает синглтон логгера для handler слоя
func GetHandlerLogger() *Logger {
	handlerLoggerOnce.Do(func() {
		handlerLoggerInstance = NewLogger(HandlerLayer)
	})
	return handlerLoggerInstance
}

// GetServiceLogger возвращает синглтон логгера для service слоя
func GetServiceLogger() *Logger {
	serviceLoggerOnce.Do(func() {
		serviceLoggerInstance = NewLogger(ServiceLayer)
	})
	return serviceLoggerInstance
}

// GetRepositoryLogger возвращает синглтон логгера для repository слоя
func GetRepositoryLogger() *Logger {
	repositoryLoggerOnce.Do(func() {
		repositoryLoggerInstance = NewLogger(RepositoryLayer)
	})
	return repositoryLoggerInstance
}

// GetMiddlewareLogger возвращает синглтон логгера для middleware слоя
func GetMiddlewareLogger() *Logger {
	middlewareLoggerOnce.Do(func() {
		middlewareLoggerInstance = NewLogger(MiddlewareLayer)
	})
	return middlewareLoggerInstance
}

// GetDatabaseLogger возвращает синглтон логгера для database слоя
func GetDatabaseLogger() *Logger {
	databaseLoggerOnce.Do(func() {
		databaseLoggerInstance = NewLogger(DatabaseLayer)
	})
	return databaseLoggerInstance
}

// GetConfigLogger возвращает синглтон логгера для config слоя
func GetConfigLogger() *Logger {
	configLoggerOnce.Do(func() {
		configLoggerInstance = NewLogger(ConfigLayer)
	})
	return configLoggerInstance
}

// GetUtilsLogger возвращает синглтон логгера для utils слоя
func GetUtilsLogger() *Logger {
	utilsLoggerOnce.Do(func() {
		utilsLoggerInstance = NewLogger(UtilsLayer)
	})
	return utilsLoggerInstance
}

// GetGlobalConfig возвращает глобальную конфигурацию логгера
func GetGlobalConfig() *LoggerConfig {
	configOnce.Do(func() {
		globalConfig = ConfigFromEnv()
	})
	return globalConfig
}

// InitializeLoggers инициализирует все логгеры с глобальной конфигурацией
func InitializeLoggers() {
	config := GetGlobalConfig()

	// Инициализируем все логгеры с конфигурацией
	handlerLoggerOnce.Do(func() {
		handlerLoggerInstance = NewLoggerWithConfig(HandlerLayer, config)
	})

	serviceLoggerOnce.Do(func() {
		serviceLoggerInstance = NewLoggerWithConfig(ServiceLayer, config)
	})

	repositoryLoggerOnce.Do(func() {
		repositoryLoggerInstance = NewLoggerWithConfig(RepositoryLayer, config)
	})

	middlewareLoggerOnce.Do(func() {
		middlewareLoggerInstance = NewLoggerWithConfig(MiddlewareLayer, config)
	})

	databaseLoggerOnce.Do(func() {
		databaseLoggerInstance = NewLoggerWithConfig(DatabaseLayer, config)
	})

	configLoggerOnce.Do(func() {
		configLoggerInstance = NewLoggerWithConfig(ConfigLayer, config)
	})

	utilsLoggerOnce.Do(func() {
		utilsLoggerInstance = NewLoggerWithConfig(UtilsLayer, config)
	})
}

// SetGlobalLogLevel устанавливает уровень логирования для всех логгеров
func SetGlobalLogLevel(level LogLevel) {
	config := GetGlobalConfig()
	config.Level = level

	// Обновляем уровень для всех существующих логгеров
	if handlerLoggerInstance != nil {
		handlerLoggerInstance.SetLevel(level)
	}
	if serviceLoggerInstance != nil {
		serviceLoggerInstance.SetLevel(level)
	}
	if repositoryLoggerInstance != nil {
		repositoryLoggerInstance.SetLevel(level)
	}
	if middlewareLoggerInstance != nil {
		middlewareLoggerInstance.SetLevel(level)
	}
	if databaseLoggerInstance != nil {
		databaseLoggerInstance.SetLevel(level)
	}
	if configLoggerInstance != nil {
		configLoggerInstance.SetLevel(level)
	}
	if utilsLoggerInstance != nil {
		utilsLoggerInstance.SetLevel(level)
	}
}

// ResetLoggers сбрасывает все экземпляры логгеров (полезно для тестирования)
func ResetLoggers() {
	handlerLoggerInstance = nil
	serviceLoggerInstance = nil
	repositoryLoggerInstance = nil
	middlewareLoggerInstance = nil
	databaseLoggerInstance = nil
	configLoggerInstance = nil
	utilsLoggerInstance = nil

	handlerLoggerOnce = sync.Once{}
	serviceLoggerOnce = sync.Once{}
	repositoryLoggerOnce = sync.Once{}
	middlewareLoggerOnce = sync.Once{}
	databaseLoggerOnce = sync.Once{}
	configLoggerOnce = sync.Once{}
	utilsLoggerOnce = sync.Once{}

	globalConfig = nil
	configOnce = sync.Once{}
}

// Convenience functions для быстрого доступа к логгерам

// Debug логирует debug сообщение используя repository логгер
func Debug(msg string, fields ...interface{}) {
	GetRepositoryLogger().Debug(msg, fields...)
}

// Info логирует info сообщение используя repository логгер
func Info(msg string, fields ...interface{}) {
	GetRepositoryLogger().Info(msg, fields...)
}

// Warn логирует warning сообщение используя repository логгер
func Warn(msg string, fields ...interface{}) {
	GetRepositoryLogger().Warn(msg, fields...)
}

// Error логирует error сообщение используя repository логгер
func Error(msg string, fields ...interface{}) {
	GetRepositoryLogger().Error(msg, fields...)
}

// Fatal логирует fatal сообщение используя repository логгер
func Fatal(msg string, fields ...interface{}) {
	GetRepositoryLogger().Fatal(msg, fields...)
}

// Debugf логирует форматированное debug сообщение
func Debugf(format string, args ...interface{}) {
	GetRepositoryLogger().Debugf(format, args...)
}

// Infof логирует форматированное info сообщение
func Infof(format string, args ...interface{}) {
	GetRepositoryLogger().Infof(format, args...)
}

// Warnf логирует форматированное warning сообщение
func Warnf(format string, args ...interface{}) {
	GetRepositoryLogger().Warnf(format, args...)
}

// Errorf логирует форматированное error сообщение
func Errorf(format string, args ...interface{}) {
	GetRepositoryLogger().Errorf(format, args...)
}

// Fatalf логирует форматированное fatal сообщение
func Fatalf(format string, args ...interface{}) {
	GetRepositoryLogger().Fatalf(format, args...)
}
