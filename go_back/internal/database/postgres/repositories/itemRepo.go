package repositories

import (
	"database/sql"
	"reflect"

	"gng/internal/models"
)

// ItemRepository определяет интерфейс для операций с предметами
type ItemRepository interface {
	BaseRepository
}

// ItemRepositoryImpl предоставляет реализацию для операций с предметами
type ItemRepositoryImpl struct {
	*BaseRepositoryImpl
}

// NewItemRepository создает новый репозиторий предметов
func NewItemRepository(db *sql.DB) *ItemRepositoryImpl {
	return &ItemRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "items", reflect.TypeOf(models.Item{})),
	}
}
