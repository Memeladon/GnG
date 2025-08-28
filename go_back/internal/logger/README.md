# Logger Utility

Удобный и красивый логгер для Go приложения, построенный на базе библиотеки `github.com/charmbracelet/log`.

### Создание логгера для конкретного слоя

```go
import "gng/internal/utils"

// Для handlers
logger := utils.NewHandlerLogger()

// Для services
logger := utils.NewServiceLogger()

// Для repositories
logger := utils.NewRepositoryLogger()

// Для middleware
logger := utils.NewMiddlewareLogger()

// Для database операций
logger := utils.NewDatabaseLogger()
```

### Базовое логирование

```go
logger := utils.NewServiceLogger()

logger.Debug("Debug message")
logger.Info("Info message")
logger.Warn("Warning message")
logger.Error("Error message")
logger.Fatal("Fatal message") // Завершает программу
```

### Логирование с дополнительными полями

```go
logger := utils.NewHandlerLogger()

// Одиночное поле
logger.WithField("user_id", "12345").Info("User request received")

// Множественные поля
logger.Info("Request processed", 
    "method", "GET",
    "path", "/api/users",
    "status", 200,
    "duration", "150ms",
)

// Контекст как map
logger.WithContext(map[string]interface{}{
    "table": "users",
    "query": "SELECT * FROM users",
    "params": []interface{}{12345},
}).Debug("Executing database query")
```

### Форматированное логирование

```go
logger := utils.NewServiceLogger()

logger.Infof("Processing request %s for user %s", "GET", "12345")
logger.Errorf("Failed to connect to database: %v", err)
```

## Уровни логирования

```go
// Установка уровня логирования
logger := utils.NewServiceLogger()
logger.SetLevel(utils.DebugLevel)  // Показывает все логи
logger.SetLevel(utils.InfoLevel)   // Показывает Info, Warn, Error, Fatal
logger.SetLevel(utils.WarnLevel)   // Показывает Warn, Error, Fatal
logger.SetLevel(utils.ErrorLevel)  // Показывает только Error, Fatal
logger.SetLevel(utils.FatalLevel)  // Показывает только Fatal
```

## Конфигурация логгера

### Через код

```go
config := &utils.LoggerConfig{
    Level:      utils.DebugLevel,
    Output:     "stdout",
    ShowCaller: true,
    ShowTime:   true,
    Prefix:     "🚀",
    Colors:     true,
}

logger := utils.NewServiceLoggerWithConfig(config)
```

### Через переменные окружения

```bash
# Уровень логирования
export LOG_LEVEL=DEBUG

# Вывод (stdout, stderr, file)
export LOG_OUTPUT=stdout

# Файл для логирования (если LOG_OUTPUT=file)
export LOG_FILE=/var/log/app.log

# Префикс
export LOG_PREFIX="🎯"

# Цвета (true/false)
export LOG_COLORS=true
```

### Автоматическая конфигурация из переменных окружения

```go
config := utils.ConfigFromEnv()
logger := utils.NewServiceLoggerWithConfig(config)
```

## Примеры использования в разных слоях

### Handlers

```go
func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
    logger := utils.NewHandlerLogger()
    
    logger.Info("GetUser handler called", 
        "method", r.Method,
        "path", r.URL.Path,
        "user_agent", r.UserAgent(),
    )
    
    // ... логика обработки
    
    logger.Info("User retrieved successfully", "user_id", userID)
}
```

### Services

```go
func (s *UserService) CreateUser(ctx context.Context, user *models.User) error {
    logger := utils.NewServiceLogger()
    
    logger.Info("Creating new user", 
        "email", user.Email,
        "username", user.Username,
    )
    
    // ... логика создания пользователя
    
    if err != nil {
        logger.WithField("error", err.Error()).Error("Failed to create user")
        return err
    }
    
    logger.Info("User created successfully", "user_id", user.ID)
    return nil
}
```

### Repositories

```go
func (r *UserRepository) FindByID(ctx context.Context, id string) (*models.User, error) {
    logger := utils.NewRepositoryLogger()
    
    logger.Debug("Executing FindByID query", 
        "table", "users",
        "user_id", id,
    )
    
    // ... выполнение запроса
    
    if err != nil {
        logger.WithField("error", err.Error()).Error("Database query failed")
        return nil, err
    }
    
    logger.Debug("User found", "user_id", id)
    return user, nil
}
```

### Middleware

```go
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        logger := utils.NewMiddlewareLogger()
        
        start := time.Now()
        
        logger.Debug("Request started", 
            "method", r.Method,
            "path", r.URL.Path,
            "ip", r.RemoteAddr,
        )
        
        next.ServeHTTP(w, r)
        
        duration := time.Since(start)
        logger.Info("Request completed", 
            "method", r.Method,
            "path", r.URL.Path,
            "duration", duration.String(),
        )
    })
}
```

## Структура лога

Каждый лог содержит следующую информацию:

```
[LEVEL] Message
  layer: LAYER_NAME
  file: filename.go
  line: 42
  function: FunctionName
  additional_field: value
  ...
```

## Демонстрация

Запустите демо программу:
```bash
go run ./cmd/logger_demo
```