package models

import (
	"time"

	"github.com/google/uuid"
)

// PlayerStats представляет статистику игрока
type PlayerStats struct {
	ID             uuid.UUID `json:"id" db:"id"`
	PlayerID       uuid.UUID `json:"player_id" db:"player_id"`
	GamesPlayed    int       `json:"games_played" db:"games_played"`
	GamesWon       int       `json:"games_won" db:"games_won"`
	GamesLost      int       `json:"games_lost" db:"games_lost"`
	TotalPoints    int       `json:"total_points" db:"total_points"`
	TotalDiceRolls int       `json:"total_dice_rolls" db:"total_dice_rolls"`
	ItemsCollected int       `json:"items_collected" db:"items_collected"`
	ItemsUsed      int       `json:"items_used" db:"items_used"`
	TrapsTriggered int       `json:"traps_triggered" db:"traps_triggered"`
	JailTime       int       `json:"jail_time" db:"jail_time"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time `json:"updated_at" db:"updated_at"`

	Player *Player `json:"player,omitempty"`
}

// PlayerStatsCreate представляет данные, необходимые для создания новой статистики игрока
type PlayerStatsCreate struct {
	PlayerID uuid.UUID `json:"player_id" validate:"required"`
}

// PlayerStatsUpdate представляет данные, которые можно обновить для статистики игрока
type PlayerStatsUpdate struct {
	GamesPlayed    *int `json:"games_played,omitempty"`
	GamesWon       *int `json:"games_won,omitempty"`
	GamesLost      *int `json:"games_lost,omitempty"`
	TotalPoints    *int `json:"total_points,omitempty"`
	TotalDiceRolls *int `json:"total_dice_rolls,omitempty"`
	ItemsCollected *int `json:"items_collected,omitempty"`
	ItemsUsed      *int `json:"items_used,omitempty"`
	TrapsTriggered *int `json:"traps_triggered,omitempty"`
	JailTime       *int `json:"jail_time,omitempty"`
}
