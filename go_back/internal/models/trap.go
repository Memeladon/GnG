package models

import (
	"time"

	"github.com/google/uuid"
)

// Trap представляет ловушку на игровом поле
type Trap struct {
	ID          uuid.UUID  `json:"id" db:"id"`
	CellID      int        `json:"cell_id" db:"cell_id"`
	Name        string     `json:"name" db:"name"`
	Description string     `json:"description" db:"description"`
	EffectType  EffectType `json:"effect_type" db:"effect_type"`
	EffectValue string     `json:"effect_value" db:"effect_value"`
	IsActive    bool       `json:"is_active" db:"is_active"`
	TriggeredBy *uuid.UUID `json:"triggered_by,omitempty" db:"triggered_by"` // ID игрока, который активировал ловушку
	TriggeredAt *time.Time `json:"triggered_at,omitempty" db:"triggered_at"`
	CreatedAt   time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time  `json:"updated_at" db:"updated_at"`

	Cell   *Cell   `json:"cell,omitempty"`
	Player *Player `json:"player,omitempty"`
}

// TrapCreate представляет данные, необходимые для создания новой ловушки
type TrapCreate struct {
	CellID      int        `json:"cell_id" validate:"required,min=1"`
	Name        string     `json:"name" validate:"required,min=1,max=100"`
	Description string     `json:"description,omitempty"`
	EffectType  EffectType `json:"effect_type" validate:"required"`
	EffectValue string     `json:"effect_value,omitempty"`
	IsActive    bool       `json:"is_active"`
}

// TrapUpdate представляет данные, которые можно обновить для ловушки
type TrapUpdate struct {
	Name        *string     `json:"name,omitempty" validate:"omitempty,min=1,max=100"`
	Description *string     `json:"description,omitempty"`
	EffectType  *EffectType `json:"effect_type,omitempty"`
	EffectValue *string     `json:"effect_value,omitempty"`
	IsActive    *bool       `json:"is_active,omitempty"`
	TriggeredBy *uuid.UUID  `json:"triggered_by,omitempty"`
	TriggeredAt *time.Time  `json:"triggered_at,omitempty"`
}
