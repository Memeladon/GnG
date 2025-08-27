package models

import (
	"time"

	"github.com/google/uuid"
)

// User represents a user in the system
type User struct {
	ID        uuid.UUID `json:"id" db:"id"`
	Login     string    `json:"login" db:"login"`
	Password  string    `json:"-" db:"password"` // Hidden from JSON for security
	Mail      *string   `json:"mail,omitempty" db:"mail"`
	IsActive  bool      `json:"is_active" db:"is_active"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`

	// Relations
	SessionUser *SessionUser `json:"session_user,omitempty"`
	Player      *Player      `json:"player,omitempty"`
}

// UserCreate represents data needed to create a new user
type UserCreate struct {
	Login    string  `json:"login" validate:"required,min=3,max=50"`
	Password string  `json:"password" validate:"required,min=6"`
	Mail     *string `json:"mail,omitempty" validate:"omitempty,email"`
}

// UserUpdate represents data that can be updated for a user
type UserUpdate struct {
	Login    *string `json:"login,omitempty" validate:"omitempty,min=3,max=50"`
	Password *string `json:"password,omitempty" validate:"omitempty,min=6"`
	Mail     *string `json:"mail,omitempty" validate:"omitempty,email"`
	IsActive *bool   `json:"is_active,omitempty"`
}

// UserLogin represents login credentials
type UserLogin struct {
	Login    string `json:"login" validate:"required"`
	Password string `json:"password" validate:"required"`
}
