package models

import (
	"time"

	"github.com/google/uuid"
)

// PlayerEffects represents effects applied to a player
type PlayerEffects struct {
	ID             uuid.UUID      `json:"id" db:"id"`
	PlayerID       uuid.UUID      `json:"player_id" db:"player_id"`
	EffectType     EffectType     `json:"effect_type" db:"effect_type"`
	EffectCategory EffectCategory `json:"effect_category" db:"effect_category"`
	EffectValue    string         `json:"effect_value" db:"effect_value"`
	Duration       int            `json:"duration" db:"duration"` // Duration in turns, -1 for permanent
	IsActive       bool           `json:"is_active" db:"is_active"`
	CreatedAt      time.Time      `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time      `json:"updated_at" db:"updated_at"`

	// Relations
	Player *Player `json:"player,omitempty"`
}

// PlayerEffectsCreate represents data needed to create new player effects
type PlayerEffectsCreate struct {
	PlayerID       uuid.UUID      `json:"player_id" validate:"required"`
	EffectType     EffectType     `json:"effect_type" validate:"required"`
	EffectCategory EffectCategory `json:"effect_category" validate:"required"`
	EffectValue    string         `json:"effect_value,omitempty"`
	Duration       int            `json:"duration" validate:"min=-1"`
	IsActive       bool           `json:"is_active"`
}

// PlayerEffectsUpdate represents data that can be updated for player effects
type PlayerEffectsUpdate struct {
	EffectType     *EffectType     `json:"effect_type,omitempty"`
	EffectCategory *EffectCategory `json:"effect_category,omitempty"`
	EffectValue    *string         `json:"effect_value,omitempty"`
	Duration       *int            `json:"duration,omitempty" validate:"omitempty,min=-1"`
	IsActive       *bool           `json:"is_active,omitempty"`
}
