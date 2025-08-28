package models

import (
	"time"

	"github.com/google/uuid"
)

// User представляет пользователя в системе
type User struct {
	ID        uuid.UUID `json:"id" db:"id"`
	Login     string    `json:"login" db:"login"`
	Password  string    `json:"-" db:"password"`
	Mail      *string   `json:"mail,omitempty" db:"mail"`
	IsActive  bool      `json:"is_active" db:"is_active"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`

	SessionUser *SessionUser `json:"session_user,omitempty"`
	Player      *Player      `json:"player,omitempty"`
}

// UserCreate представляет данные, необходимые для создания нового пользователя
type UserCreate struct {
	Login    string  `json:"login" validate:"required,min=3,max=50"`
	Password string  `json:"password" validate:"required,min=6"`
	Mail     *string `json:"mail,omitempty" validate:"omitempty,email"`
}

// UserUpdate представляет данные, которые можно обновить для пользователя
type UserUpdate struct {
	Login    *string `json:"login,omitempty" validate:"omitempty,min=3,max=50"`
	Password *string `json:"password,omitempty" validate:"omitempty,min=6"`
	Mail     *string `json:"mail,omitempty" validate:"omitempty,email"`
	IsActive *bool   `json:"is_active,omitempty"`
}

// UserLogin представляет учетные данные для входа
type UserLogin struct {
	Login    string `json:"login" validate:"required"`
	Password string `json:"password" validate:"required"`
}
