package models

import (
	"time"

	"github.com/google/uuid"
)

// Session представляет игровую сессию
type Session struct {
	ID          uuid.UUID `json:"id" db:"id"`
	Name        string    `json:"name" db:"name"`
	Description string    `json:"description" db:"description"`
	IsActive    bool      `json:"is_active" db:"is_active"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`

	SessionUsers []SessionUser `json:"session_users,omitempty"`
}

// SessionCreate представляет данные, необходимые для создания новой сессии
type SessionCreate struct {
	Name        string `json:"name" validate:"required,min=1,max=100"`
	Description string `json:"description,omitempty"`
	IsActive    bool   `json:"is_active"`
}

// SessionUpdate представляет данные, которые можно обновить для сессии
type SessionUpdate struct {
	Name        *string `json:"name,omitempty" validate:"omitempty,min=1,max=100"`
	Description *string `json:"description,omitempty"`
	IsActive    *bool   `json:"is_active,omitempty"`
}
