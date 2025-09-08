package repositories

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"reflect"

	"gng/internal/models"
)

type UserRepository interface {
	BaseRepository
	CreateUserUnique(ctx context.Context, data any) (*models.User, error)
}

type UserRepositoryImpl struct {
	*BaseRepositoryImpl
}

func NewUserRepository(db *sql.DB) *UserRepositoryImpl {
	return &UserRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "users", reflect.TypeOf(models.User{})),
	}
}

func (repo *UserRepositoryImpl) CreateUserUnique(ctx context.Context, data any) (*models.User, error) {
	dMap, err := repo.structToMap(data)
	if err != nil {
		return nil, fmt.Errorf("wrong data format")
	}

	login, ok := dMap["login"].(string)
	if !ok {
		return nil, fmt.Errorf("login is required and must be string")
	}

	exists, err := repo.ExistsBy(ctx, map[string]any{"login": login})
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
		Password: dMap["password"].(string),
	}

	if mail, ok := dMap["mail"].(string); ok {
		userData.Mail = &mail
	}

	userInterface, err := repo.CreateOne(ctx, userData)
	if err != nil {
		return nil, fmt.Errorf("error creating user: %w", err)
	}

	user, ok := userInterface.(*models.User)
	if !ok {
		userValue := reflect.ValueOf(userInterface)
		if userValue.Kind() == reflect.Pointer {
			userValue = userValue.Elem()
		}
		user = userValue.Addr().Interface().(*models.User)
	}

	return user, nil
}
