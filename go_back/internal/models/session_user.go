package models

import (
	"time"

	"github.com/google/uuid"
)

// SessionUser represents a user's session
type SessionUser struct {
	ID        uuid.UUID `json:"id" db:"id"`
	UserID    uuid.UUID `json:"user_id" db:"user_id"`
	SessionID uuid.UUID `json:"session_id" db:"session_id"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`

	// Relations
	User    *User    `json:"user,omitempty"`
	Session *Session `json:"session,omitempty"`
}

// SessionUserCreate represents data needed to create a new session user
type SessionUserCreate struct {
	UserID    uuid.UUID `json:"user_id" validate:"required"`
	SessionID uuid.UUID `json:"session_id" validate:"required"`
}
