package repositories

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"reflect"

	"gng/internal/models"

	"github.com/google/uuid"
)

// SessionUserRepository определяет интерфейс для операций с пользователями сессий
type SessionUserRepository interface {
	BaseRepository
	AddUserToSession(ctx context.Context, data map[string]any) (*models.SessionUser, error)
	GetSessionUsersWithUserData(ctx context.Context, sessionID uuid.UUID) ([]map[string]any, error)
}

// SessionUserRepositoryImpl предоставляет реализацию для операций с пользователями сессий
type SessionUserRepositoryImpl struct {
	*BaseRepositoryImpl
}

// NewSessionUserRepository создает новый репозиторий пользователей сессий
func NewSessionUserRepository(db *sql.DB) *SessionUserRepositoryImpl {
	return &SessionUserRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "session_users", reflect.TypeOf(models.SessionUser{})),
	}
}

// AddUserToSession добавляет пользователя в игровую сессию через промежуточную таблицу SessionUser
// Проверяет, что пользователь еще не в этой сессии
func (repo *SessionUserRepositoryImpl) AddUserToSession(ctx context.Context, data map[string]any) (*models.SessionUser, error) {
	sessionID, ok := data["session_id"].(uuid.UUID)
	if !ok {
		return nil, fmt.Errorf("session_id is required and must be uuid.UUID")
	}

	userID, ok := data["user_id"].(uuid.UUID)
	if !ok {
		return nil, fmt.Errorf("user_id is required and must be uuid.UUID")
	}

	exists, err := repo.ExistsBy(ctx, map[string]any{
		"session_id": sessionID,
		"user_id":    userID,
	})
	if err != nil {
		return nil, fmt.Errorf("error checking if user is in session: %w", err)
	}
	if exists {
		log.Printf("AddUserToSession: User %s already in session %s", userID, sessionID)
		return nil, fmt.Errorf("user is already in this session")
	}

	log.Printf("AddUserToSession: Adding user %s to session %s", userID, sessionID)

	sessionUserData := &models.SessionUserCreate{
		SessionID: sessionID,
		UserID:    userID,
	}

	sessionUserInterface, err := repo.CreateOne(ctx, sessionUserData)
	if err != nil {
		return nil, fmt.Errorf("error creating session user: %w", err)
	}

	sessionUser, ok := sessionUserInterface.(*models.SessionUser)
	if !ok {
		sessionUserValue := reflect.ValueOf(sessionUserInterface)
		if sessionUserValue.Kind() == reflect.Ptr {
			sessionUserValue = sessionUserValue.Elem()
		}
		sessionUser = sessionUserValue.Addr().Interface().(*models.SessionUser)
	}

	return sessionUser, nil
}

// GetSessionUsersWithUserData возвращает список пользователей и их связей для заданной игровой сессии
func (repo *SessionUserRepositoryImpl) GetSessionUsersWithUserData(ctx context.Context, sessionID uuid.UUID) ([]map[string]any, error) {
	log.Printf("GetSessionUsersWithUserData: Getting session users for session %s", sessionID)

	return []map[string]any{}, nil
}
