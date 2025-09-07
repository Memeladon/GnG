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

// SessionRepository определяет интерфейс для операций с сессиями
type SessionRepository interface {
	BaseRepository
	CloseSession(ctx context.Context, sessionID uuid.UUID) (*models.Session, error)
	IsSessionExpired(ctx context.Context, sessionID uuid.UUID) (bool, error)
	GetSessionsByUserID(ctx context.Context, userID uuid.UUID) ([]*models.Session, error)
}

// SessionRepositoryImpl предоставляет реализацию для операций с сессиями
type SessionRepositoryImpl struct {
	*BaseRepositoryImpl
}

// NewSessionRepository создает новый репозиторий сессий
func NewSessionRepository(db *sql.DB) *SessionRepositoryImpl {
	return &SessionRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "sessions", reflect.TypeOf(models.Session{})),
	}
}

// CloseSession закрывает игровую сессию: устанавливает is_active в false
func (repo *SessionRepositoryImpl) CloseSession(ctx context.Context, sessionID uuid.UUID) (*models.Session, error) {
	sessionInterface, err := repo.GetOne(ctx, sessionID)
	if err != nil {
		return nil, fmt.Errorf("error getting session: %w", err)
	}
	if sessionInterface == nil {
		log.Printf("CloseSession: Session %s not found", sessionID)
		return nil, fmt.Errorf("session not found")
	}

	log.Printf("CloseSession: Closing session %s", sessionID)

	updateData := map[string]interface{}{
		"id":        sessionID,
		"is_active": false,
	}

	updatedSessionInterface, err := repo.UpdateOne(ctx, updateData)
	if err != nil {
		return nil, fmt.Errorf("error updating session: %w", err)
	}

	updatedSession, ok := updatedSessionInterface.(*models.Session)
	if !ok {
		sessionValue := reflect.ValueOf(updatedSessionInterface)
		if sessionValue.Kind() == reflect.Ptr {
			sessionValue = sessionValue.Elem()
		}
		updatedSession = sessionValue.Addr().Interface().(*models.Session)
	}

	return updatedSession, nil
}

// IsSessionExpired проверяет, истекла ли игровая сессия, проверяя, активна ли она
func (repo *SessionRepositoryImpl) IsSessionExpired(ctx context.Context, sessionID uuid.UUID) (bool, error) {
	sessionInterface, err := repo.GetOne(ctx, sessionID)
	if err != nil {
		return false, fmt.Errorf("error getting session: %w", err)
	}
	if sessionInterface == nil {
		return true, nil
	}

	session, ok := sessionInterface.(*models.Session)
	if !ok {
		sessionValue := reflect.ValueOf(sessionInterface)
		if sessionValue.Kind() == reflect.Ptr {
			sessionValue = sessionValue.Elem()
		}
		session = sessionValue.Addr().Interface().(*models.Session)
	}

	// Session is expired if it's not active
	return !session.IsActive, nil
}

// GetSessionsByUserID возвращает все игровые сессии, в которых участвует пользователь
// Использует связь через SessionUser
func (repo *SessionRepositoryImpl) GetSessionsByUserID(ctx context.Context, userID uuid.UUID) ([]*models.Session, error) {

	log.Printf("GetSessionsByUserID: Getting sessions for user %s", userID)

	// На данный момент вернем пустой срез, так как это сложный запрос
	// TODO: Реализовать правильный JOIN запрос с таблицей SessionUser
	return []*models.Session{}, nil
}
