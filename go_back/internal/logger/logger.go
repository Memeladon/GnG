package logger

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"

	"github.com/charmbracelet/log"
)

// LogLevel представляет уровень логирования
type LogLevel string

const (
	DebugLevel LogLevel = "DEBUG"
	InfoLevel  LogLevel = "INFO"
	WarnLevel  LogLevel = "WARN"
	ErrorLevel LogLevel = "ERROR"
	FatalLevel LogLevel = "FATAL"
)

// AppLayer представляет слой приложения, где генерируется лог
type AppLayer string

const (
	HandlerLayer    AppLayer = "🚀 HANDLER"
	ServiceLayer    AppLayer = "⚙️  SERVICE"
	RepositoryLayer AppLayer = "💾 REPOSITORY"
	MiddlewareLayer AppLayer = "🔗 MIDDLEWARE"
	DatabaseLayer   AppLayer = "🗄️  DATABASE"
	ConfigLayer     AppLayer = "⚙️  CONFIG"
	UtilsLayer      AppLayer = "🛠️  UTILS"
)

// Logger - структурированный логгер, показывающий слой приложения и обеспечивающий красивый вывод в консоль
type Logger struct {
	logger  *log.Logger
	layer   AppLayer
	context map[string]interface{}
}

// NewLogger создает новый экземпляр логгера для определенного слоя приложения
func NewLogger(layer AppLayer) *Logger {
	l := log.NewWithOptions(os.Stderr, log.Options{
		ReportCaller:    true,
		ReportTimestamp: true,
		Level:           log.DebugLevel,
		Prefix:          "🎯",
	})

	l.SetStyles(log.DefaultStyles())

	return &Logger{
		logger:  l,
		layer:   layer,
		context: make(map[string]interface{}),
	}
}

// WithContext добавляет поля контекста к логгеру
func (l *Logger) WithContext(ctx map[string]interface{}) *Logger {
	newLogger := &Logger{
		logger:  l.logger,
		layer:   l.layer,
		context: make(map[string]interface{}),
	}

	for k, v := range l.context {
		newLogger.context[k] = v
	}

	for k, v := range ctx {
		newLogger.context[k] = v
	}

	return newLogger
}

// WithField добавляет одно поле к контексту логгера
func (l *Logger) WithField(key string, value interface{}) *Logger {
	return l.WithContext(map[string]interface{}{key: value})
}

// getCallerInfo возвращает информацию о вызывающей функции
func (l *Logger) getCallerInfo() map[string]interface{} {
	pc, file, line, ok := runtime.Caller(2)
	if !ok {
		return map[string]interface{}{}
	}

	funcName := runtime.FuncForPC(pc).Name()
	parts := strings.Split(funcName, ".")
	shortFuncName := parts[len(parts)-1]

	return map[string]interface{}{
		"file":     filepath.Base(file),
		"line":     line,
		"function": shortFuncName,
	}
}

// logWithLayer логирует сообщение с указанием слоя приложения и информацией о вызывающем
func (l *Logger) logWithLayer(level log.Level, msg string, fields ...interface{}) {
	callerInfo := l.getCallerInfo()

	allFields := []interface{}{
		"layer", l.layer,
		"file", callerInfo["file"],
		"line", callerInfo["line"],
		"function", callerInfo["function"],
	}

	for k, v := range l.context {
		allFields = append(allFields, k, v)
	}

	allFields = append(allFields, fields...)

	l.logger.With(allFields...).Log(level, msg)
}

// Debug логирует отладочное сообщение
func (l *Logger) Debug(msg string, fields ...interface{}) {
	l.logWithLayer(log.DebugLevel, msg, fields...)
}

// Info логирует информационное сообщение
func (l *Logger) Info(msg string, fields ...interface{}) {
	l.logWithLayer(log.InfoLevel, msg, fields...)
}

// Warn логирует предупреждающее сообщение
func (l *Logger) Warn(msg string, fields ...interface{}) {
	l.logWithLayer(log.WarnLevel, msg, fields...)
}

// Error логирует сообщение об ошибке
func (l *Logger) Error(msg string, fields ...interface{}) {
	l.logWithLayer(log.ErrorLevel, msg, fields...)
}

// Fatal логирует критическое сообщение и завершает программу
func (l *Logger) Fatal(msg string, fields ...interface{}) {
	l.logWithLayer(log.FatalLevel, msg, fields...)
	os.Exit(1)
}

// Debugf логирует форматированное отладочное сообщение
func (l *Logger) Debugf(format string, args ...interface{}) {
	l.Debug(fmt.Sprintf(format, args...))
}

// Infof логирует форматированное информационное сообщение
func (l *Logger) Infof(format string, args ...interface{}) {
	l.Info(fmt.Sprintf(format, args...))
}

// Warnf логирует форматированное предупреждающее сообщение
func (l *Logger) Warnf(format string, args ...interface{}) {
	l.Warn(fmt.Sprintf(format, args...))
}

// Errorf логирует форматированное сообщение об ошибке
func (l *Logger) Errorf(format string, args ...interface{}) {
	l.Error(fmt.Sprintf(format, args...))
}

// Fatalf логирует форматированное критическое сообщение и завершает программу
func (l *Logger) Fatalf(format string, args ...interface{}) {
	l.Fatal(fmt.Sprintf(format, args...))
}

// SetLevel устанавливает уровень логирования
func (l *Logger) SetLevel(level LogLevel) {
	switch level {
	case DebugLevel:
		l.logger.SetLevel(log.DebugLevel)
	case InfoLevel:
		l.logger.SetLevel(log.InfoLevel)
	case WarnLevel:
		l.logger.SetLevel(log.WarnLevel)
	case ErrorLevel:
		l.logger.SetLevel(log.ErrorLevel)
	case FatalLevel:
		l.logger.SetLevel(log.FatalLevel)
	}
}

// Удобные функции для создания логгеров для разных слоев

// NewHandlerLogger создает логгер для слоя обработчиков
func NewHandlerLogger() *Logger {
	return NewLogger(HandlerLayer)
}

// NewServiceLogger создает логгер для слоя сервисов
func NewServiceLogger() *Logger {
	return NewLogger(ServiceLayer)
}

// NewRepositoryLogger создает логгер для слоя репозиториев
func NewRepositoryLogger() *Logger {
	return NewLogger(RepositoryLayer)
}

// NewMiddlewareLogger создает логгер для слоя промежуточного ПО
func NewMiddlewareLogger() *Logger {
	return NewLogger(MiddlewareLayer)
}

// NewDatabaseLogger создает логгер для слоя базы данных
func NewDatabaseLogger() *Logger {
	return NewLogger(DatabaseLayer)
}

// NewConfigLogger создает логгер для слоя конфигурации
func NewConfigLogger() *Logger {
	return NewLogger(ConfigLayer)
}

// NewUtilsLogger создает логгер для слоя утилит
func NewUtilsLogger() *Logger {
	return NewLogger(UtilsLayer)
}
