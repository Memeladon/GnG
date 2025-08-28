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

// InventoryRepository определяет интерфейс для операций с инвентарем
type InventoryRepository interface {
	BaseRepository
	IsInventoryFull(ctx context.Context, inventoryID uuid.UUID) (bool, error)
	AddItemToInventory(ctx context.Context, data map[string]interface{}) (*models.ItemInstance, error)
	ReplaceItemInInventory(ctx context.Context, data map[string]interface{}) (*models.ItemInstance, error)
	SearchItemsInInventory(ctx context.Context, inventoryID uuid.UUID, itemName string) ([]*models.ItemInstance, error)
}

// InventoryRepositoryImpl предоставляет реализацию для операций с инвентарем
type InventoryRepositoryImpl struct {
	*BaseRepositoryImpl
	itemInstanceRepo ItemInstanceRepository
}

// NewInventoryRepository создает новый репозиторий инвентаря
func NewInventoryRepository(db *sql.DB, itemInstanceRepo ItemInstanceRepository) *InventoryRepositoryImpl {
	return &InventoryRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "inventories", reflect.TypeOf(models.Inventory{})),
		itemInstanceRepo:   itemInstanceRepo,
	}
}

// IsInventoryFull проверяет, заполнен ли инвентарь игрока
// Максимальное количество предметов в инвентаре - 6
func (repo *InventoryRepositoryImpl) IsInventoryFull(ctx context.Context, inventoryID uuid.UUID) (bool, error) {
	count, err := repo.Count(ctx, map[string]interface{}{"inventory_id": inventoryID})
	if err != nil {
		return false, fmt.Errorf("error counting items: %w", err)
	}

	full := count >= 6
	if full {
		log.Printf("IsInventoryFull: Inventory %s is full (%d items)", inventoryID, count)
	}
	return full, nil
}

// AddItemToInventory добавляет новый экземпляр предмета в инвентарь игрока
// Проверяет, что инвентарь не заполнен
func (repo *InventoryRepositoryImpl) AddItemToInventory(ctx context.Context, data map[string]interface{}) (*models.ItemInstance, error) {
	inventoryID, ok := data["inventory_id"].(uuid.UUID)
	if !ok {
		return nil, fmt.Errorf("inventory_id is required and must be uuid.UUID")
	}

	if isFull, err := repo.IsInventoryFull(ctx, inventoryID); err != nil {
		return nil, fmt.Errorf("error checking inventory fullness: %w", err)
	} else if isFull {
		log.Printf("AddItemToInventory: Inventory %s is full, cannot add item", inventoryID)
		return nil, fmt.Errorf("inventory is full (max 6 items)")
	}

	log.Printf("AddItemToInventory: Adding item %v to inventory %s", data["item_id"], inventoryID)

	itemInstanceData := &models.ItemInstanceCreate{
		ItemID:      data["item_id"].(uuid.UUID),
		InventoryID: inventoryID,
	}

	itemInstanceInterface, err := repo.itemInstanceRepo.CreateOne(ctx, itemInstanceData)
	if err != nil {
		return nil, fmt.Errorf("error creating item instance: %w", err)
	}

	itemInstance, ok := itemInstanceInterface.(*models.ItemInstance)
	if !ok {
		itemValue := reflect.ValueOf(itemInstanceInterface)
		if itemValue.Kind() == reflect.Ptr {
			itemValue = itemValue.Elem()
		}
		itemInstance = itemValue.Addr().Interface().(*models.ItemInstance)
	}

	return itemInstance, nil
}

// ReplaceItemInInventory заменяет существующий экземпляр предмета в инвентаре новым
// Старый экземпляр удаляется, создается новый с указанными параметрами
func (repo *InventoryRepositoryImpl) ReplaceItemInInventory(ctx context.Context, data map[string]interface{}) (*models.ItemInstance, error) {
	oldItemInstanceID, ok := data["old_item_instance_id"].(uuid.UUID)
	if !ok {
		return nil, fmt.Errorf("old_item_instance_id is required and must be uuid.UUID")
	}

	inventoryID, ok := data["inventory_id"].(uuid.UUID)
	if !ok {
		return nil, fmt.Errorf("inventory_id is required and must be uuid.UUID")
	}

	oldItemInterface, err := repo.itemInstanceRepo.GetOne(ctx, oldItemInstanceID)
	if err != nil {
		return nil, fmt.Errorf("error getting old item instance: %w", err)
	}
	if oldItemInterface == nil {
		log.Printf("ReplaceItemInInventory: ItemInstance %s not found in inventory %s", oldItemInstanceID, inventoryID)
		return nil, fmt.Errorf("item instance not found in this inventory")
	}

	oldItem, ok := oldItemInterface.(*models.ItemInstance)
	if !ok {
		itemValue := reflect.ValueOf(oldItemInterface)
		if itemValue.Kind() == reflect.Ptr {
			itemValue = itemValue.Elem()
		}
		oldItem = itemValue.Addr().Interface().(*models.ItemInstance)
	}

	if oldItem.InventoryID != inventoryID {
		log.Printf("ReplaceItemInInventory: ItemInstance %s not found in inventory %s", oldItemInstanceID, inventoryID)
		return nil, fmt.Errorf("item instance not found in this inventory")
	}

	log.Printf("ReplaceItemInInventory: Replacing ItemInstance %s in inventory %s", oldItemInstanceID, inventoryID)

	_, err = repo.itemInstanceRepo.DeleteOne(ctx, oldItemInstanceID)
	if err != nil {
		return nil, fmt.Errorf("error deleting old item instance: %w", err)
	}

	newItemID := oldItem.ItemID
	if newItemIDFromData, ok := data["new_item_id"].(uuid.UUID); ok {
		newItemID = newItemIDFromData
	}

	newItemInstanceData := &models.ItemInstanceCreate{
		ItemID:      newItemID,
		InventoryID: inventoryID,
	}

	newItemInstanceInterface, err := repo.itemInstanceRepo.CreateOne(ctx, newItemInstanceData)
	if err != nil {
		return nil, fmt.Errorf("error creating new item instance: %w", err)
	}

	newItemInstance, ok := newItemInstanceInterface.(*models.ItemInstance)
	if !ok {
		itemValue := reflect.ValueOf(newItemInstanceInterface)
		if itemValue.Kind() == reflect.Ptr {
			itemValue = itemValue.Elem()
		}
		newItemInstance = itemValue.Addr().Interface().(*models.ItemInstance)
	}

	return newItemInstance, nil
}

// SearchItemsInInventory ищет экземпляры предметов в инвентаре игрока по названию предмета
// Если название не указано, возвращает все предметы в инвентаре
func (repo *InventoryRepositoryImpl) SearchItemsInInventory(ctx context.Context, inventoryID uuid.UUID, itemName string) ([]*models.ItemInstance, error) {
	filters := map[string]interface{}{"inventory_id": inventoryID}

	itemInstancesInterface, err := repo.itemInstanceRepo.FindBy(ctx, filters)
	if err != nil {
		return nil, fmt.Errorf("error finding item instances: %w", err)
	}

	var itemInstances []*models.ItemInstance
	for _, itemInterface := range itemInstancesInterface {
		itemInstance, ok := itemInterface.(*models.ItemInstance)
		if !ok {
			itemValue := reflect.ValueOf(itemInterface)
			if itemValue.Kind() == reflect.Ptr {
				itemValue = itemValue.Elem()
			}
			itemInstance = itemValue.Addr().Interface().(*models.ItemInstance)
		}
		itemInstances = append(itemInstances, itemInstance)
	}

	return itemInstances, nil
}
