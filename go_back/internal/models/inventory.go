package models

import (
	"time"

	"github.com/google/uuid"
)

// Inventory represents a player's inventory
type Inventory struct {
	ID        uuid.UUID `json:"id" db:"id"`
	PlayerID  uuid.UUID `json:"player_id" db:"player_id"`
	Capacity  int       `json:"capacity" db:"capacity"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`

	// Relations
	Player        *Player        `json:"player,omitempty"`
	ItemInstances []ItemInstance `json:"item_instances,omitempty"`
}

// InventoryCreate represents data needed to create a new inventory
type InventoryCreate struct {
	PlayerID uuid.UUID `json:"player_id" validate:"required"`
	Capacity int       `json:"capacity" validate:"required,min=1"`
}

// InventoryUpdate represents data that can be updated for an inventory
type InventoryUpdate struct {
	Capacity *int `json:"capacity,omitempty" validate:"omitempty,min=1"`
}
