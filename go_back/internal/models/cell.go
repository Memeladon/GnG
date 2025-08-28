package models

import (
	"database/sql/driver"
	"encoding/json"
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
	Traps       JSONB     `json:"traps,omitempty" db:"traps"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`

	Players []Player `json:"players,omitempty"`
}

// JSONB представляет поле JSONB для PostgreSQL
type JSONB []map[string]interface{}

// Value реализует интерфейс driver.Valuer
func (j JSONB) Value() (driver.Value, error) {
	if j == nil {
		return nil, nil
	}
	return json.Marshal(j)
}

// Scan реализует интерфейс sql.Scanner
func (j *JSONB) Scan(value interface{}) error {
	if value == nil {
		*j = nil
		return nil
	}

	var bytes []byte
	switch v := value.(type) {
	case []byte:
		bytes = v
	case string:
		bytes = []byte(v)
	default:
		bytes, err := json.Marshal(value)
		if err != nil {
			return err
		}
		return json.Unmarshal(bytes, j)
	}

	return json.Unmarshal(bytes, j)
}

// CellCreate представляет данные, необходимые для создания новой клетки
type CellCreate struct {
	Position    int      `json:"position" validate:"required,min=0"`
	CellType    CellType `json:"cell_type" validate:"required"`
	Title       string   `json:"title" validate:"required,min=1,max=100"`
	Description string   `json:"description,omitempty"`
	ImagePath   string   `json:"image_path,omitempty"`
	Traps       JSONB    `json:"traps,omitempty"`
}

// CellUpdate представляет данные, которые можно обновить для клетки
type CellUpdate struct {
	Position    *int      `json:"position,omitempty" validate:"omitempty,min=0"`
	CellType    *CellType `json:"cell_type,omitempty"`
	Title       *string   `json:"title,omitempty" validate:"omitempty,min=1,max=100"`
	Description *string   `json:"description,omitempty"`
	ImagePath   *string   `json:"image_path,omitempty"`
	Traps       *JSONB    `json:"traps,omitempty"`
}
