package repositories

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"reflect"
	"time"

	"gng/internal/models"

	"github.com/google/uuid"
)

// ItemInstanceRepository определяет интерфейс для операций с экземплярами предметов
type ItemInstanceRepository interface {
	BaseRepository
	UseItem(ctx context.Context, itemInstanceID uuid.UUID) (*models.ItemInstance, error)
}

// ItemInstanceRepositoryImpl предоставляет реализацию для операций с экземплярами предметов
type ItemInstanceRepositoryImpl struct {
	*BaseRepositoryImpl
}

// NewItemInstanceRepository создает новый репозиторий экземпляров предметов
func NewItemInstanceRepository(db *sql.DB) *ItemInstanceRepositoryImpl {
	return &ItemInstanceRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "item_instances", reflect.TypeOf(models.ItemInstance{})),
	}
}

// UseItem использует экземпляр предмета из инвентаря игрока:
// - Помечает предмет как использованный (IsUsed = true)
// - Устанавливает временную метку UsedAt
// - Экземпляр предмета остается в базе данных, но помечается как потребленный
func (repo *ItemInstanceRepositoryImpl) UseItem(ctx context.Context, itemInstanceID uuid.UUID) (*models.ItemInstance, error) {
	itemInstanceInterface, err := repo.GetOne(ctx, itemInstanceID)
	if err != nil {
		log.Printf("UseItem: ItemInstance %s -> error getting: %v", itemInstanceID, err)
		return nil, fmt.Errorf("error getting item instance: %w", err)
	}
	if itemInstanceInterface == nil {
		log.Printf("UseItem: ItemInstance %s -> not found", itemInstanceID)
		return nil, fmt.Errorf("item instance not found")
	}

	itemInstance, ok := itemInstanceInterface.(*models.ItemInstance)
	if !ok {
		itemValue := reflect.ValueOf(itemInstanceInterface)
		if itemValue.Kind() == reflect.Ptr {
			itemValue = itemValue.Elem()
		}
		itemInstance = itemValue.Addr().Interface().(*models.ItemInstance)
	}

	if itemInstance.IsUsed {
		log.Printf("UseItem: ItemInstance %s -> already used", itemInstanceID)
		return nil, fmt.Errorf("item instance already used")
	}

	log.Printf("UseItem: ItemInstance %s -> marking as used", itemInstanceID)

	now := time.Now()
	updateData := map[string]interface{}{
		"id":      itemInstanceID,
		"is_used": true,
		"used_at": &now,
	}

	updatedInterface, err := repo.UpdateOne(ctx, updateData)
	if err != nil {
		return nil, fmt.Errorf("error updating item instance: %w", err)
	}

	updatedItemInstance, ok := updatedInterface.(*models.ItemInstance)
	if !ok {
		itemValue := reflect.ValueOf(updatedInterface)
		if itemValue.Kind() == reflect.Ptr {
			itemValue = itemValue.Elem()
		}
		updatedItemInstance = itemValue.Addr().Interface().(*models.ItemInstance)
	}

	return updatedItemInstance, nil
}
