package models

import (
	"time"

	"github.com/google/uuid"
)

// ItemInstance represents an instance of an item in a player's inventory
type ItemInstance struct {
	ID          uuid.UUID  `json:"id" db:"id"`
	ItemID      uuid.UUID  `json:"item_id" db:"item_id"`
	InventoryID uuid.UUID  `json:"inventory_id" db:"inventory_id"`
	IsUsed      bool       `json:"is_used" db:"is_used"`
	UsedAt      *time.Time `json:"used_at,omitempty" db:"used_at"`
	CreatedAt   time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time  `json:"updated_at" db:"updated_at"`

	// Relations
	Item      *Item      `json:"item,omitempty"`
	Inventory *Inventory `json:"inventory,omitempty"`
}

// ItemInstanceCreate represents data needed to create a new item instance
type ItemInstanceCreate struct {
	ItemID      uuid.UUID `json:"item_id" validate:"required"`
	InventoryID uuid.UUID `json:"inventory_id" validate:"required"`
}

// ItemInstanceUpdate represents data that can be updated for an item instance
type ItemInstanceUpdate struct {
	IsUsed *bool      `json:"is_used,omitempty"`
	UsedAt *time.Time `json:"used_at,omitempty"`
}
