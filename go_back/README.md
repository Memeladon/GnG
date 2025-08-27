# GnG Backend (Go)

Это Go версия бэкенда для игры GnG, перенесенная с Python.

## Структура проекта

```
go_back/
├── cmd/
│   └── server/          # Основной сервер
├── internal/
│   ├── database/        # Работа с базой данных
│   │   ├── postgres/    # PostgreSQL
│   │   └── redis/       # Redis
│   ├── models/          # Модели данных
│   ├── handlers/        # HTTP обработчики
│   ├── services/        # Бизнес-логика
│   └── middleware/      # Промежуточное ПО
├── migrations/          # Миграции базы данных (goose)
├── configs/            # Конфигурационные файлы
└── go.mod              # Зависимости Go
```

## Требования

- Go 1.21+
- PostgreSQL 12+
- Redis (опционально)

## Установка и запуск

1. Клонируйте репозиторий и перейдите в папку `go_back`:
```bash
cd go_back
```

2. Установите зависимости:
```bash
go mod tidy
```

3. Скопируйте файл с переменными окружения:
```bash
cp env_template.env .env
```

4. Настройте переменные окружения в файле `.env`

5. Запустите миграции базы данных:
```bash
goose -dir migrations postgres "host=localhost port=5432 user=postgres password=password dbname=gng_db sslmode=disable" up
```

6. Запустите сервер:
```bash
go run cmd/server/main.go
```

## Миграции

Для работы с миграциями используется [goose](https://github.com/pressly/goose).

### Создание новой миграции:
```bash
goose -dir migrations create migration_name sql
```

### Применение миграций:
```bash
goose -dir migrations postgres "connection_string" up
```

### Откат миграций:
```bash
goose -dir migrations postgres "connection_string" down
```

## API Endpoints

### Пользователи
- `GET /api/v1/users` - Список пользователей
- `GET /api/v1/users/{id}` - Получить пользователя
- `POST /api/v1/users` - Создать пользователя
- `PUT /api/v1/users/{id}` - Обновить пользователя
- `DELETE /api/v1/users/{id}` - Удалить пользователя

### Игры
- `GET /api/v1/games` - Список игр
- `GET /api/v1/games/{id}` - Получить игру
- `POST /api/v1/games` - Создать игру
- `PUT /api/v1/games/{id}` - Обновить игру

### Предметы
- `GET /api/v1/items` - Список предметов
- `GET /api/v1/items/{id}` - Получить предмет
- `POST /api/v1/items` - Создать предмет
- `PUT /api/v1/items/{id}` - Обновить предмет

## Разработка

### Добавление новых моделей

1. Создайте модель в `internal/models/`
2. Создайте DAO в `internal/database/postgres/dao/`
3. Создайте сервис в `internal/services/`
4. Создайте обработчик в `internal/handlers/`
5. Добавьте маршруты в `cmd/server/main.go`

### Тестирование

```bash
go test ./...
```

## Лицензия

MIT
