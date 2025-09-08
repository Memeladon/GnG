package logger

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"

	"github.com/charmbracelet/log"
)

type LogLevel string

const (
	DebugLevel LogLevel = "DEBUG"
	InfoLevel  LogLevel = "INFO"
	WarnLevel  LogLevel = "WARN"
	ErrorLevel LogLevel = "ERROR"
	FatalLevel LogLevel = "FATAL"
)

type Logger struct {
	logger *log.Logger
}

// NewLogger создает новый экземпляр логгера
func NewLogger() *Logger {
	l := log.NewWithOptions(os.Stderr, log.Options{
		ReportCaller:    true,
		ReportTimestamp: true,
		Level:           log.DebugLevel,
		Prefix:          "🎯",
	})

	l.SetStyles(log.DefaultStyles())

	return &Logger{
		logger: l,
	}
}

// NewLoggerWithLevel создает новый логгер с указанным уровнем
func NewLoggerWithLevel(level LogLevel) *Logger {
	l := NewLogger()
	l.SetLevel(level)
	return l
}

func (l *Logger) getCallerInfo() map[string]any {
	pc, file, line, ok := runtime.Caller(2)
	if !ok {
		return map[string]any{}
	}

	funcName := runtime.FuncForPC(pc).Name()
	parts := strings.Split(funcName, ".")
	shortFuncName := parts[len(parts)-1]

	return map[string]any{
		"file":     filepath.Base(file),
		"line":     line,
		"function": shortFuncName,
	}
}

func (l *Logger) logWithCaller(level log.Level, msg string, fields ...any) {
	callerInfo := l.getCallerInfo()

	allFields := []any{
		"file", callerInfo["file"],
		"line", callerInfo["line"],
		"function", callerInfo["function"],
	}

	allFields = append(allFields, fields...)

	l.logger.With(allFields...).Log(level, msg)
}

func (l *Logger) Debug(msg string, fields ...any) {
	l.logWithCaller(log.DebugLevel, msg, fields...)
}

func (l *Logger) Info(msg string, fields ...any) {
	l.logWithCaller(log.InfoLevel, msg, fields...)
}

func (l *Logger) Warn(msg string, fields ...any) {
	l.logWithCaller(log.WarnLevel, msg, fields...)
}

func (l *Logger) Error(msg string, fields ...any) {
	l.logWithCaller(log.ErrorLevel, msg, fields...)
}

func (l *Logger) Fatal(msg string, fields ...any) {
	l.logWithCaller(log.FatalLevel, msg, fields...)
	os.Exit(1)
}

func (l *Logger) Infof(format string, args ...any) {
	l.Info(fmt.Sprintf(format, args...))
}

func (l *Logger) Warnf(format string, args ...any) {
	l.Warn(fmt.Sprintf(format, args...))
}

func (l *Logger) Errorf(format string, args ...any) {
	l.Error(fmt.Sprintf(format, args...))
}

func (l *Logger) Fatalf(format string, args ...any) {
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

// WithField добавляет поле к логгеру
func (l *Logger) WithField(key string, value any) *Logger {
	newLogger := &Logger{
		logger: l.logger.With(key, value),
	}
	return newLogger
}

// WithFields добавляет несколько полей к логгеру
func (l *Logger) WithFields(fields map[string]any) *Logger {
	var args []any
	for k, v := range fields {
		args = append(args, k, v)
	}

	newLogger := &Logger{
		logger: l.logger.With(args...),
	}
	return newLogger
}
