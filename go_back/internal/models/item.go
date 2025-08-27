package models

import (
	"time"

	"github.com/google/uuid"
)

// Item represents an item in the game
type Item struct {
	ID             uuid.UUID      `json:"id" db:"id"`
	Name           string         `json:"name" db:"name"`
	Description    string         `json:"description" db:"description"`
	ItemType       ItemType       `json:"item_type" db:"item_type"`
	ImagePath      string         `json:"image_path" db:"image_path"`
	EffectType     EffectType     `json:"effect_type" db:"effect_type"`
	EffectCategory EffectCategory `json:"effect_category" db:"effect_category"`
	EffectValue    string         `json:"effect_value" db:"effect_value"`
	Rarity         int            `json:"rarity" db:"rarity"`
	CreatedAt      time.Time      `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time      `json:"updated_at" db:"updated_at"`

	// Relations
	ItemInstances []ItemInstance `json:"item_instances,omitempty"`
}

// ItemCreate represents data needed to create a new item
type ItemCreate struct {
	Name           string         `json:"name" validate:"required,min=1,max=100"`
	Description    string         `json:"description,omitempty"`
	ItemType       ItemType       `json:"item_type" validate:"required"`
	ImagePath      string         `json:"image_path,omitempty"`
	EffectType     EffectType     `json:"effect_type" validate:"required"`
	EffectCategory EffectCategory `json:"effect_category" validate:"required"`
	EffectValue    string         `json:"effect_value,omitempty"`
	Rarity         int            `json:"rarity" validate:"required,min=1,max=10"`
}

// ItemUpdate represents data that can be updated for an item
type ItemUpdate struct {
	Name           *string         `json:"name,omitempty" validate:"omitempty,min=1,max=100"`
	Description    *string         `json:"description,omitempty"`
	ItemType       *ItemType       `json:"item_type,omitempty"`
	ImagePath      *string         `json:"image_path,omitempty"`
	EffectType     *EffectType     `json:"effect_type,omitempty"`
	EffectCategory *EffectCategory `json:"effect_category,omitempty"`
	EffectValue    *string         `json:"effect_value,omitempty"`
	Rarity         *int            `json:"rarity,omitempty" validate:"omitempty,min=1,max=10"`
}
