package models

import (
	"time"

	"github.com/google/uuid"
)

// Player представляет игрового персонажа пользователя
type Player struct {
	ID             uuid.UUID  `json:"id" db:"id"`
	CellID         int        `json:"cell_id" db:"cell_id"`
	UserID         uuid.UUID  `json:"user_id" db:"user_id"`
	Username       string     `json:"username" db:"username"`
	ProfileImage   string     `json:"profile_image" db:"profile_image"`
	Role           UserRights `json:"role" db:"role"`
	LastDiceValue  int        `json:"last_dice_value" db:"last_dice_value"`
	PreviousCellID int        `json:"previous_cell_id" db:"previous_cell_id"`
	CreatedAt      time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at" db:"updated_at"`

	User      *User           `json:"user,omitempty"`
	Cell      *Cell           `json:"cell,omitempty"`
	Stats     *PlayerStats    `json:"stats,omitempty"`
	Inventory *Inventory      `json:"inventory,omitempty"`
	Effects   []PlayerEffects `json:"effects,omitempty"`
	Games     []Game          `json:"games,omitempty"`
}

// PlayerCreate представляет данные, необходимые для создания нового игрока
type PlayerCreate struct {
	UserID       uuid.UUID  `json:"user_id" validate:"required"`
	Username     string     `json:"username" validate:"required,min=3,max=50"`
	ProfileImage string     `json:"profile_image,omitempty"`
	Role         UserRights `json:"role" validate:"required"`
	CellID       int        `json:"cell_id" validate:"required,min=0"`
}

// PlayerUpdate представляет данные, которые можно обновить для игрока
type PlayerUpdate struct {
	Username       *string     `json:"username,omitempty" validate:"omitempty,min=3,max=50"`
	ProfileImage   *string     `json:"profile_image,omitempty"`
	Role           *UserRights `json:"role,omitempty"`
	CellID         *int        `json:"cell_id,omitempty" validate:"omitempty,min=0"`
	LastDiceValue  *int        `json:"last_dice_value,omitempty"`
	PreviousCellID *int        `json:"previous_cell_id,omitempty"`
}
