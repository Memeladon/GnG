package postgres

import (
	"database/sql"
	"fmt"
	"time"

	"gng/internal/utils/helpers"
	"gng/internal/utils/logger"

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
	return &Config{
		Host:     helpers.GetEnv("DB_HOST", "localhost"),
		Port:     helpers.GetEnv("DB_PORT", "5432"),
		User:     helpers.GetEnv("DB_USER", "postgres"),
		Password: helpers.GetEnv("DB_PASSWORD", "password"),
		DBName:   helpers.GetEnv("DB_NAME", "gng_db"),
		SSLMode:  helpers.GetEnv("DB_SSLMODE", "disable"),
	}
}

// Close закрывает соединение с базой данных
func (db *DB) Close() error {
	return db.DB.Close()
}
