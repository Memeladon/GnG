package postgres

import (
	"database/sql"
	"fmt"
	"os"
	"time"

	logger "gng/internal/utils"

	_ "github.com/lib/pq"
)

// DB представляет соединение с базой данных
type DB struct {
	*sql.DB
}

// Config представляет конфигурацию базы данных
type Config struct {
	Host     string
	Port     string
	User     string
	Password string
	DBName   string
	SSLMode  string
}

// NewConnection создает новое соединение с базой данных
func NewConnection(log *logger.Logger) (*DB, error) {
	config := getConfig()

	if config == nil {
		return nil, fmt.Errorf("database configuration is incomplete: missing required environment variables (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)")
	}

	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		config.Host, config.Port, config.User, config.Password, config.DBName, config.SSLMode)

	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(25)
	db.SetConnMaxLifetime(5 * time.Minute)

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	log.Info("Successfully connected to PostgreSQL database")
	return &DB{db}, nil
}

// getConfig возвращает конфигурацию базы данных из переменных окружения
func getConfig() *Config {
	config := &Config{
		Host:     os.Getenv("DB_HOST"),
		Port:     os.Getenv("DB_PORT"),
		User:     os.Getenv("DB_USER"),
		Password: os.Getenv("DB_PASSWORD"),
		DBName:   os.Getenv("DB_NAME"),
		SSLMode:  os.Getenv("DB_SSLMODE"),
	}

	// Проверяем, что все обязательные переменные установлены
	if config.Host == "" || config.Port == "" || config.User == "" ||
		config.Password == "" || config.DBName == "" {
		return nil
	}

	// Устанавливаем SSLMode по умолчанию, если не указан
	if config.SSLMode == "" {
		config.SSLMode = "disable"
	}

	return config
}

// Close закрывает соединение с базой данных
func (db *DB) Close() error {
	return db.DB.Close()
}
