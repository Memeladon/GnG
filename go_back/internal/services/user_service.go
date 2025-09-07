package services

import (
	"context"
	"database/sql"

	"gng/internal/utils/logger"
)

type UserService struct {
	db     *sql.DB
	logger *logger.Logger
}

func NewUserService(db *sql.DB, logger *logger.Logger) *UserService {
	return &UserService{
		db:     db,
		logger: logger,
	}
}

func (s *UserService) GetByID(ctx context.Context, id interface{}) (interface{}, error) {
	return nil, nil
}

func (s *UserService) Create(ctx context.Context, data interface{}) (interface{}, error) {
	return nil, nil
}

func (s *UserService) Update(ctx context.Context, id interface{}, data interface{}) (interface{}, error) {
	return nil, nil
}

func (s *UserService) Delete(ctx context.Context, id interface{}) error {
	return nil
}

func (s *UserService) List(ctx context.Context, limit, offset int) ([]interface{}, error) {
	return nil, nil
}
