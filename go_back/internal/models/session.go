package models

import (
	"time"

	"github.com/google/uuid"
)

// Session represents a game session
type Session struct {
	ID          uuid.UUID `json:"id" db:"id"`
	Name        string    `json:"name" db:"name"`
	Description string    `json:"description" db:"description"`
	IsActive    bool      `json:"is_active" db:"is_active"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`

	// Relations
	SessionUsers []SessionUser `json:"session_users,omitempty"`
}

// SessionCreate represents data needed to create a new session
type SessionCreate struct {
	Name        string `json:"name" validate:"required,min=1,max=100"`
	Description string `json:"description,omitempty"`
	IsActive    bool   `json:"is_active"`
}

// SessionUpdate represents data that can be updated for a session
type SessionUpdate struct {
	Name        *string `json:"name,omitempty" validate:"omitempty,min=1,max=100"`
	Description *string `json:"description,omitempty"`
	IsActive    *bool   `json:"is_active,omitempty"`
}
