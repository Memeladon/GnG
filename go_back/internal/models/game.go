package models

import (
	"time"

	"github.com/google/uuid"
)

// Game представляет игровую сессию для игрока
type Game struct {
	ID             int            `json:"id" db:"id"`
	PlayerID       uuid.UUID      `json:"player_id" db:"player_id"`
	Status         GameStatus     `json:"status" db:"status"`
	Score          int            `json:"score" db:"score"`
	GameConditions GameConditions `json:"game_conditions" db:"game_conditions"`
	DiceModifier   *DiceModifier  `json:"dice_modifier,omitempty" db:"dice_modifier"`
	GameModifier   *GameModifier  `json:"game_modifier,omitempty" db:"game_modifier"`
	StartedAt      time.Time      `json:"started_at" db:"started_at"`
	CompletedAt    *time.Time     `json:"completed_at,omitempty" db:"completed_at"`
	CreatedAt      time.Time      `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time      `json:"updated_at" db:"updated_at"`

	Player *Player `json:"player,omitempty"`
}

// GameCreate представляет данные, необходимые для создания новой игры
type GameCreate struct {
	PlayerID       uuid.UUID      `json:"player_id" validate:"required"`
	Status         GameStatus     `json:"status" validate:"required"`
	Score          int            `json:"score"`
	GameConditions GameConditions `json:"game_conditions" validate:"required"`
	DiceModifier   *DiceModifier  `json:"dice_modifier,omitempty"`
	GameModifier   *GameModifier  `json:"game_modifier,omitempty"`
}

// GameUpdate представляет данные, которые можно обновить для игры
type GameUpdate struct {
	Status         *GameStatus     `json:"status,omitempty"`
	Score          *int            `json:"score,omitempty"`
	GameConditions *GameConditions `json:"game_conditions,omitempty"`
	DiceModifier   *DiceModifier   `json:"dice_modifier,omitempty"`
	GameModifier   *GameModifier   `json:"game_modifier,omitempty"`
	CompletedAt    *time.Time      `json:"completed_at,omitempty"`
}
