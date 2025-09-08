package services

import (
	"context"

	"gng/internal/database/postgres/repositories"
	"gng/internal/models"
	"gng/internal/utils/logger"
)

type UserService struct {
	logger         *logger.Logger
	userRepository repositories.UserRepository
}

func NewUserService(logger *logger.Logger, userRepository repositories.UserRepository) *UserService {
	return &UserService{
		logger:         logger,
		userRepository: userRepository,
	}
}

func (s *UserService) GetByID(ctx context.Context, id any) (*models.User, error) {
	return nil, nil
}

func (s *UserService) Create(ctx context.Context, data any) (*models.User, error) {
	user, err := s.userRepository.CreateUserUnique(ctx, data)
	if err != nil {
		return nil, err
	}

	return user, nil
}

func (s *UserService) Update(ctx context.Context, id any, data any) (*models.User, error) {
	return nil, nil
}

func (s *UserService) Delete(ctx context.Context, id any) error {
	return nil
}

func (s *UserService) List(ctx context.Context, limit, offset int) ([]*models.User, error) {
	return nil, nil
}
