package repositories

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"reflect"

	"gng/internal/models"
)

// UserRepository определяет интерфейс для операций с пользователями
type UserRepository interface {
	BaseRepository
	CreateUserUnique(ctx context.Context, data map[string]interface{}) (*models.User, error)
}

// UserRepositoryImpl предоставляет реализацию для операций с пользователями
type UserRepositoryImpl struct {
	*BaseRepositoryImpl
}

// NewUserRepository создает новый репозиторий пользователей
func NewUserRepository(db *sql.DB) *UserRepositoryImpl {
	return &UserRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "users", reflect.TypeOf(models.User{})),
	}
}

// CreateUserUnique создает нового пользователя с проверкой уникальности логина
func (repo *UserRepositoryImpl) CreateUserUnique(ctx context.Context, data map[string]interface{}) (*models.User, error) {
	login, ok := data["login"].(string)
	if !ok {
		return nil, fmt.Errorf("login is required and must be string")
	}

	exists, err := repo.ExistsBy(ctx, map[string]interface{}{"login": login})
	if err != nil {
		return nil, fmt.Errorf("error checking login uniqueness: %w", err)
	}
	if exists {
		log.Printf("CreateUserUnique: User with login %s already exists", login)
		return nil, fmt.Errorf("user with this login already exists")
	}

	log.Printf("CreateUserUnique: Creating User with login %s", login)

	userData := &models.UserCreate{
		Login:    login,
		Password: data["password"].(string),
	}

	if mail, ok := data["mail"].(string); ok {
		userData.Mail = &mail
	}

	userInterface, err := repo.CreateOne(ctx, userData)
	if err != nil {
		return nil, fmt.Errorf("error creating user: %w", err)
	}

	user, ok := userInterface.(*models.User)
	if !ok {
		userValue := reflect.ValueOf(userInterface)
		if userValue.Kind() == reflect.Ptr {
			userValue = userValue.Elem()
		}
		user = userValue.Addr().Interface().(*models.User)
	}

	return user, nil
}
