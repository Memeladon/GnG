package repositories

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"reflect"

	"gng/internal/models"

	"github.com/google/uuid"
)

// PlayerStatsRepository определяет интерфейс для операций со статистикой игроков
type PlayerStatsRepository interface {
	BaseRepository
	IncrementStats(ctx context.Context, data map[string]interface{}) (*models.PlayerStats, error)
}

// PlayerStatsRepositoryImpl предоставляет реализацию для операций со статистикой игроков
type PlayerStatsRepositoryImpl struct {
	*BaseRepositoryImpl
}

// NewPlayerStatsRepository создает новый репозиторий статистики игроков
func NewPlayerStatsRepository(db *sql.DB) *PlayerStatsRepositoryImpl {
	return &PlayerStatsRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "player_stats", reflect.TypeOf(models.PlayerStats{})),
	}
}

// IncrementStats увеличивает значения статистики игрока на указанные величины
// Неизменяемые поля могут быть опущены
func (repo *PlayerStatsRepositoryImpl) IncrementStats(ctx context.Context, data map[string]interface{}) (*models.PlayerStats, error) {
	playerID, ok := data["player_id"].(uuid.UUID)
	if !ok {
		return nil, fmt.Errorf("player_id is required and must be uuid.UUID")
	}

	statsInterface, err := repo.GetOne(ctx, playerID)
	if err != nil {
		return nil, fmt.Errorf("error getting player stats: %w", err)
	}
	if statsInterface == nil {
		log.Printf("IncrementStats: PlayerStats for player %s not found", playerID)
		return nil, fmt.Errorf("PlayerStats not found")
	}

	stats, ok := statsInterface.(*models.PlayerStats)
	if !ok {
		statsValue := reflect.ValueOf(statsInterface)
		if statsValue.Kind() == reflect.Ptr {
			statsValue = statsValue.Elem()
		}
		stats = statsValue.Addr().Interface().(*models.PlayerStats)
	}

	log.Printf("IncrementStats: Incrementing stats for player %s: %v", playerID, data)

	for field, increment := range data {
		if field != "player_id" {
			switch field {
			case "games_played":
				stats.GamesPlayed += increment.(int)
			case "games_won":
				stats.GamesWon += increment.(int)
			case "games_lost":
				stats.GamesLost += increment.(int)
			case "total_points":
				stats.TotalPoints += increment.(int)
			case "total_dice_rolls":
				stats.TotalDiceRolls += increment.(int)
			case "items_collected":
				stats.ItemsCollected += increment.(int)
			case "items_used":
				stats.ItemsUsed += increment.(int)
			case "traps_triggered":
				stats.TrapsTriggered += increment.(int)
			case "jail_time":
				stats.JailTime += increment.(int)
			}
		}
	}

	updateData := map[string]interface{}{
		"id":               stats.ID,
		"games_played":     stats.GamesPlayed,
		"games_won":        stats.GamesWon,
		"games_lost":       stats.GamesLost,
		"total_points":     stats.TotalPoints,
		"total_dice_rolls": stats.TotalDiceRolls,
		"items_collected":  stats.ItemsCollected,
		"items_used":       stats.ItemsUsed,
		"traps_triggered":  stats.TrapsTriggered,
		"jail_time":        stats.JailTime,
	}

	updatedStatsInterface, err := repo.UpdateOne(ctx, updateData)
	if err != nil {
		return nil, fmt.Errorf("error updating player stats: %w", err)
	}

	updatedStats, ok := updatedStatsInterface.(*models.PlayerStats)
	if !ok {
		statsValue := reflect.ValueOf(updatedStatsInterface)
		if statsValue.Kind() == reflect.Ptr {
			statsValue = statsValue.Elem()
		}
		updatedStats = statsValue.Addr().Interface().(*models.PlayerStats)
	}

	return updatedStats, nil
}
