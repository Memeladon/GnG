package models

import (
	"time"
)

// Cell представляет клетку на игровом поле
type Cell struct {
	ID          int       `json:"id" db:"id"`
	Position    int       `json:"position" db:"position"`
	CellType    CellType  `json:"cell_type" db:"cell_type"`
	Title       string    `json:"title" db:"title"`
	Description string    `json:"description" db:"description"`
	ImagePath   string    `json:"image_path" db:"image_path"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`

	Players []Player `json:"players,omitempty"`
	Traps   []Trap   `json:"traps,omitempty"`
}

// CellCreate представляет данные, необходимые для создания новой клетки
type CellCreate struct {
	Position    int      `json:"position" validate:"required,min=0"`
	CellType    CellType `json:"cell_type" validate:"required"`
	Title       string   `json:"title" validate:"required,min=1,max=100"`
	Description string   `json:"description,omitempty"`
	ImagePath   string   `json:"image_path,omitempty"`
}

// CellUpdate представляет данные, которые можно обновить для клетки
type CellUpdate struct {
	Position    *int      `json:"position,omitempty" validate:"omitempty,min=0"`
	CellType    *CellType `json:"cell_type,omitempty"`
	Title       *string   `json:"title,omitempty" validate:"omitempty,min=1,max=100"`
	Description *string   `json:"description,omitempty"`
	ImagePath   *string   `json:"image_path,omitempty"`
}
