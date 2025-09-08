package models

import (
	"time"

	"github.com/google/uuid"
)

type User struct {
	ID        uuid.UUID `json:"id" db:"id"`
	Login     string    `json:"login" db:"login"`
	Password  string    `json:"-" db:"password"`
	Mail      *string   `json:"mail,omitempty" db:"mail"`
	IsActive  bool      `json:"is_active" db:"is_active"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

type UserCreate struct {
	Login    string  `json:"login" validate:"required,min=3,max=50" db:"login"`
	Password string  `json:"password" validate:"required,min=6" db:"password"`
	Mail     *string `json:"mail,omitempty" validate:"omitempty,email" db:"mail"`
}

type UserUpdate struct {
	Login    *string `json:"login,omitempty" validate:"omitempty,min=3,max=50"`
	Password *string `json:"password,omitempty" validate:"omitempty,min=6"`
	Mail     *string `json:"mail,omitempty" validate:"omitempty,email"`
	IsActive *bool   `json:"is_active,omitempty"`
}

type UserLogin struct {
	Login    string `json:"login" validate:"required"`
	Password string `json:"password" validate:"required"`
}
