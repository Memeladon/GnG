package repositories

import (
	"database/sql"
	"reflect"

	"gng/internal/models"
)

// PlayerEffectsRepository определяет интерфейс для операций с эффектами игроков
type PlayerEffectsRepository interface {
	BaseRepository
}

// PlayerEffectsRepositoryImpl предоставляет реализацию для операций с эффектами игроков
type PlayerEffectsRepositoryImpl struct {
	*BaseRepositoryImpl
}

// NewPlayerEffectsRepository создает новый репозиторий эффектов игроков
func NewPlayerEffectsRepository(db *sql.DB) *PlayerEffectsRepositoryImpl {
	return &PlayerEffectsRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "player_effects", reflect.TypeOf(models.PlayerEffects{})),
	}
}
