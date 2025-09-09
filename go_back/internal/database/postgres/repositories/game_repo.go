package repositories

import (
	"database/sql"
	"reflect"

	"gng/internal/models"
)

// GameRepository определяет интерфейс для операций с играми
type GameRepository interface {
	BaseRepository
}

// GameRepositoryImpl предоставляет реализацию для операций с играми
type GameRepositoryImpl struct {
	*BaseRepositoryImpl
}

// NewGameRepository создает новый репозиторий игр
func NewGameRepository(db *sql.DB) *GameRepositoryImpl {
	return &GameRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "games", reflect.TypeOf(models.Game{})),
	}
}
