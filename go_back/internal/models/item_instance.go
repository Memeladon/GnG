package models

import (
	"time"

	"github.com/google/uuid"
)

// ItemInstance представляет экземпляр предмета в инвентаре игрока
type ItemInstance struct {
	ID          int  `json:"id" db:"id"`
	ItemID      uuid.UUID  `json:"item_id" db:"item_id"`
	InventoryID uuid.UUID  `json:"inventory_id" db:"inventory_id"`
	IsUsed      bool       `json:"is_used" db:"is_used"`
	UsedAt      *time.Time `json:"used_at,omitempty" db:"used_at"`
	CreatedAt   time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time  `json:"updated_at" db:"updated_at"`

	Item      *Item      `json:"item,omitempty"`
	Inventory *Inventory `json:"inventory,omitempty"`
}

// ItemInstanceCreate представляет данные, необходимые для создания нового экземпляра предмета
type ItemInstanceCreate struct {
	ItemID      uuid.UUID `json:"item_id" validate:"required"`
	InventoryID uuid.UUID `json:"inventory_id" validate:"required"`
}

// ItemInstanceUpdate представляет данные, которые можно обновить для экземпляра предмета
type ItemInstanceUpdate struct {
	IsUsed *bool      `json:"is_used,omitempty"`
	UsedAt *time.Time `json:"used_at,omitempty"`
}
