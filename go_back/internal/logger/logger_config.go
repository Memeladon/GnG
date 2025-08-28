package logger

import (
	"os"
	"strings"

	"github.com/charmbracelet/log"
)

// LoggerConfig содержит конфигурацию для логгера
type LoggerConfig struct {
	Level      LogLevel
	Output     string // "stdout", "stderr", "file"
	Filepath   string
	ShowCaller bool
	ShowTime   bool
	Prefix     string
	Colors     bool
}

// DefaultConfig возвращает конфигурацию логгера по умолчанию
func DefaultConfig() *LoggerConfig {
	return &LoggerConfig{
		Level:      InfoLevel,
		Output:     "stderr",
		ShowCaller: true,
		ShowTime:   true,
		Prefix:     "🎯",
		Colors:     true,
	}
}

// ConfigFromEnv создает конфигурацию из переменных окружения
func ConfigFromEnv() *LoggerConfig {
	config := DefaultConfig()

	if level := os.Getenv("LOG_LEVEL"); level != "" {
		switch strings.ToUpper(level) {
		case "DEBUG":
			config.Level = DebugLevel
		case "INFO":
			config.Level = InfoLevel
		case "WARN":
			config.Level = WarnLevel
		case "ERROR":
			config.Level = ErrorLevel
		case "FATAL":
			config.Level = FatalLevel
		}
	}

	if output := os.Getenv("LOG_OUTPUT"); output != "" {
		config.Output = output
	}

	if filepath := os.Getenv("LOG_FILE"); filepath != "" {
		config.Filepath = filepath
		config.Output = "file"
	}

	if prefix := os.Getenv("LOG_PREFIX"); prefix != "" {
		config.Prefix = prefix
	}

	if colors := os.Getenv("LOG_COLORS"); colors != "" {
		config.Colors = strings.ToLower(colors) == "true"
	}

	return config
}

// NewLoggerWithConfig создает новый логгер с пользовательской конфигурацией
func NewLoggerWithConfig(layer AppLayer, config *LoggerConfig) *Logger {
	var output *os.File

	switch config.Output {
	case "stdout":
		output = os.Stdout
	case "file":
		if config.Filepath != "" {
			var err error
			output, err = os.OpenFile(config.Filepath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
			if err != nil {
				output = os.Stderr
			}
		} else {
			output = os.Stderr
		}
	default:
		output = os.Stderr
	}

	options := log.Options{
		ReportCaller:    config.ShowCaller,
		ReportTimestamp: config.ShowTime,
		Level:           convertLogLevel(config.Level),
		Prefix:          config.Prefix,
	}

	l := log.NewWithOptions(output, options)

	if !config.Colors {
		l.SetStyles(log.DefaultStyles())
	}

	return &Logger{
		logger:  l,
		layer:   layer,
		context: make(map[string]interface{}),
	}
}

// convertLogLevel конвертирует наш LogLevel в charmbracelet/log.Level
func convertLogLevel(level LogLevel) log.Level {
	switch level {
	case DebugLevel:
		return log.DebugLevel
	case InfoLevel:
		return log.InfoLevel
	case WarnLevel:
		return log.WarnLevel
	case ErrorLevel:
		return log.ErrorLevel
	case FatalLevel:
		return log.FatalLevel
	default:
		return log.InfoLevel
	}
}

// Удобные функции для создания настроенных логгеров

// NewHandlerLoggerWithConfig создает логгер обработчика с пользовательской конфигурацией
func NewHandlerLoggerWithConfig(config *LoggerConfig) *Logger {
	return NewLoggerWithConfig(HandlerLayer, config)
}

// NewServiceLoggerWithConfig создает логгер сервиса с пользовательской конфигурацией
func NewServiceLoggerWithConfig(config *LoggerConfig) *Logger {
	return NewLoggerWithConfig(ServiceLayer, config)
}

// NewRepositoryLoggerWithConfig создает логгер репозитория с пользовательской конфигурацией
func NewRepositoryLoggerWithConfig(config *LoggerConfig) *Logger {
	return NewLoggerWithConfig(RepositoryLayer, config)
}

// NewMiddlewareLoggerWithConfig создает логгер промежуточного ПО с пользовательской конфигурацией
func NewMiddlewareLoggerWithConfig(config *LoggerConfig) *Logger {
	return NewLoggerWithConfig(MiddlewareLayer, config)
}

// NewDatabaseLoggerWithConfig создает логгер базы данных с пользовательской конфигурацией
func NewDatabaseLoggerWithConfig(config *LoggerConfig) *Logger {
	return NewLoggerWithConfig(DatabaseLayer, config)
}

// NewConfigLoggerWithConfig создает логгер конфигурации с пользовательской конфигурацией
func NewConfigLoggerWithConfig(config *LoggerConfig) *Logger {
	return NewLoggerWithConfig(ConfigLayer, config)
}

// NewUtilsLoggerWithConfig создает логгер утилит с пользовательской конфигурацией
func NewUtilsLoggerWithConfig(config *LoggerConfig) *Logger {
	return NewLoggerWithConfig(UtilsLayer, config)
}
