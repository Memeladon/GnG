package models

import (
	"time"

	"github.com/google/uuid"
)

// PlayerEffects представляет эффекты, примененные к игроку
type PlayerEffects struct {
	ID             uuid.UUID      `json:"id" db:"id"`
	PlayerID       uuid.UUID      `json:"player_id" db:"player_id"`
	EffectType     EffectType     `json:"effect_type" db:"effect_type"`
	EffectCategory EffectCategory `json:"effect_category" db:"effect_category"`
	EffectValue    string         `json:"effect_value" db:"effect_value"`
	Duration       int            `json:"duration" db:"duration"`
	IsActive       bool           `json:"is_active" db:"is_active"`
	CreatedAt      time.Time      `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time      `json:"updated_at" db:"updated_at"`

	Player *Player `json:"player,omitempty"`
}

// PlayerEffectsCreate представляет данные, необходимые для создания новых эффектов игрока
type PlayerEffectsCreate struct {
	PlayerID       uuid.UUID      `json:"player_id" validate:"required"`
	EffectType     EffectType     `json:"effect_type" validate:"required"`
	EffectCategory EffectCategory `json:"effect_category" validate:"required"`
	EffectValue    string         `json:"effect_value,omitempty"`
	Duration       int            `json:"duration" validate:"min=-1"`
	IsActive       bool           `json:"is_active"`
}

// PlayerEffectsUpdate представляет данные, которые можно обновить для эффектов игрока
type PlayerEffectsUpdate struct {
	EffectType     *EffectType     `json:"effect_type,omitempty"`
	EffectCategory *EffectCategory `json:"effect_category,omitempty"`
	EffectValue    *string         `json:"effect_value,omitempty"`
	Duration       *int            `json:"duration,omitempty" validate:"omitempty,min=-1"`
	IsActive       *bool           `json:"is_active,omitempty"`
}
