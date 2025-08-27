package models

import (
	"time"
)

// Cell represents a cell on the game board
type Cell struct {
	ID          int       `json:"id" db:"id"`
	Name        string    `json:"name" db:"name"`
	Description string    `json:"description" db:"description"`
	CellType    CellType  `json:"cell_type" db:"cell_type"`
	ImagePath   string    `json:"image_path" db:"image_path"`
	Position    int       `json:"position" db:"position"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`

	// Relations
	Players []Player `json:"players,omitempty"`
}

// CellCreate represents data needed to create a new cell
type CellCreate struct {
	Name        string   `json:"name" validate:"required,min=1,max=100"`
	Description string   `json:"description,omitempty"`
	CellType    CellType `json:"cell_type" validate:"required"`
	ImagePath   string   `json:"image_path,omitempty"`
	Position    int      `json:"position" validate:"required,min=0"`
}

// CellUpdate represents data that can be updated for a cell
type CellUpdate struct {
	Name        *string   `json:"name,omitempty" validate:"omitempty,min=1,max=100"`
	Description *string   `json:"description,omitempty"`
	CellType    *CellType `json:"cell_type,omitempty"`
	ImagePath   *string   `json:"image_path,omitempty"`
	Position    *int      `json:"position,omitempty" validate:"omitempty,min=0"`
}
