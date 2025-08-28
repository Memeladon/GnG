package models

import (
	"time"

	"github.com/google/uuid"
)

// Inventory представляет инвентарь игрока
type Inventory struct {
	ID        uuid.UUID `json:"id" db:"id"`
	PlayerID  uuid.UUID `json:"player_id" db:"player_id"`
	Capacity  int       `json:"capacity" db:"capacity"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`

	Player        *Player        `json:"player,omitempty"`
	ItemInstances []ItemInstance `json:"item_instances,omitempty"`
}

// InventoryCreate представляет данные, необходимые для создания нового инвентаря
type InventoryCreate struct {
	PlayerID uuid.UUID `json:"player_id" validate:"required"`
	Capacity int       `json:"capacity" validate:"required,min=1"`
}

// InventoryUpdate представляет данные, которые можно обновить для инвентаря
type InventoryUpdate struct {
	Capacity *int `json:"capacity,omitempty" validate:"omitempty,min=1"`
}
