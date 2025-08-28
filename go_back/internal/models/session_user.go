package models

import (
	"time"

	"github.com/google/uuid"
)

// SessionUser представляет сессию пользователя
type SessionUser struct {
	ID        uuid.UUID `json:"id" db:"id"`
	UserID    uuid.UUID `json:"user_id" db:"user_id"`
	SessionID uuid.UUID `json:"session_id" db:"session_id"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`

	User    *User    `json:"user,omitempty"`
	Session *Session `json:"session,omitempty"`
}

// SessionUserCreate представляет данные, необходимые для создания нового пользователя сессии
type SessionUserCreate struct {
	UserID    uuid.UUID `json:"user_id" validate:"required"`
	SessionID uuid.UUID `json:"session_id" validate:"required"`
}
