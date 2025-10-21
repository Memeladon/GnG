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

// TrapRepository определяет интерфейс для операций с ловушками
type TrapRepository interface {
	BaseRepository
	GetByCellID(ctx context.Context, cellID int) ([]*models.Trap, error)
	GetActiveByCellID(ctx context.Context, cellID int) ([]*models.Trap, error)
	TriggerTrap(ctx context.Context, id uuid.UUID, playerID uuid.UUID) (*models.Trap, error)
	GetTriggeredTraps(ctx context.Context, playerID uuid.UUID) ([]*models.Trap, error)
}

// TrapRepositoryImpl предоставляет реализацию для операций с ловушками
type TrapRepositoryImpl struct {
	*BaseRepositoryImpl
}

// NewTrapRepository создает новый репозиторий ловушек
func NewTrapRepository(db *sql.DB) *TrapRepositoryImpl {
	return &TrapRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "traps", reflect.TypeOf(models.Trap{})),
	}
}

// GetByCellID получает все ловушки для определенной клетки
func (repo *TrapRepositoryImpl) GetByCellID(ctx context.Context, cellID int) ([]*models.Trap, error) {
	results, err := repo.FindBy(ctx, map[string]interface{}{"cell_id": cellID})
	if err != nil {
		return nil, fmt.Errorf("error getting traps by cell ID: %w", err)
	}

	var traps []*models.Trap
	for _, result := range results {
		if trap, ok := result.(*models.Trap); ok {
			traps = append(traps, trap)
		} else {
			// Handle the case where result is not a pointer
			trapValue := reflect.ValueOf(result)
			if trapValue.Kind() == reflect.Ptr {
				trapValue = trapValue.Elem()
			}
			trap := trapValue.Addr().Interface().(*models.Trap)
			traps = append(traps, trap)
		}
	}

	log.Printf("GetByCellID: cell_id=%d -> %d traps", cellID, len(traps))
	return traps, nil
}

// GetActiveByCellID получает только активные ловушки для определенной клетки
func (repo *TrapRepositoryImpl) GetActiveByCellID(ctx context.Context, cellID int) ([]*models.Trap, error) {
	results, err := repo.FindBy(ctx, map[string]interface{}{
		"cell_id":   cellID,
		"is_active": true,
	})
	if err != nil {
		return nil, fmt.Errorf("error getting active traps by cell ID: %w", err)
	}

	var traps []*models.Trap
	for _, result := range results {
		if trap, ok := result.(*models.Trap); ok {
			traps = append(traps, trap)
		} else {
			// Handle the case where result is not a pointer
			trapValue := reflect.ValueOf(result)
			if trapValue.Kind() == reflect.Ptr {
				trapValue = trapValue.Elem()
			}
			trap := trapValue.Addr().Interface().(*models.Trap)
			traps = append(traps, trap)
		}
	}

	log.Printf("GetActiveByCellID: cell_id=%d -> %d active traps", cellID, len(traps))
	return traps, nil
}

// TriggerTrap активирует ловушку (устанавливает triggered_by и triggered_at)
func (repo *TrapRepositoryImpl) TriggerTrap(ctx context.Context, id uuid.UUID, playerID uuid.UUID) (*models.Trap, error) {
	exists, err := repo.Exists(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("error checking trap existence: %w", err)
	}
	if !exists {
		return nil, fmt.Errorf("trap not found")
	}

	updateData := map[string]interface{}{
		"id":           id,
		"triggered_by": playerID,
		"triggered_at": "NOW()",
	}

	result, err := repo.UpdateOne(ctx, updateData)
	if err != nil {
		return nil, fmt.Errorf("error triggering trap: %w", err)
	}

	if result == nil {
		return nil, fmt.Errorf("trap not found or already triggered")
	}

	trap, ok := result.(*models.Trap)
	if !ok {
		trapValue := reflect.ValueOf(result)
		if trapValue.Kind() == reflect.Ptr {
			trapValue = trapValue.Elem()
		}
		trap = trapValue.Addr().Interface().(*models.Trap)
	}

	log.Printf("TriggerTrap: trap %s triggered by player %s", id, playerID)
	return trap, nil
}

// GetTriggeredTraps получает все сработавшие ловушки для игрока
func (repo *TrapRepositoryImpl) GetTriggeredTraps(ctx context.Context, playerID uuid.UUID) ([]*models.Trap, error) {
	results, err := repo.FindBy(ctx, map[string]interface{}{"triggered_by": playerID})
	if err != nil {
		return nil, fmt.Errorf("error getting triggered traps: %w", err)
	}

	var traps []*models.Trap
	for _, result := range results {
		if trap, ok := result.(*models.Trap); ok {
			traps = append(traps, trap)
		} else {
			// Handle the case where result is not a pointer
			trapValue := reflect.ValueOf(result)
			if trapValue.Kind() == reflect.Ptr {
				trapValue = trapValue.Elem()
			}
			trap := trapValue.Addr().Interface().(*models.Trap)
			traps = append(traps, trap)
		}
	}

	log.Printf("GetTriggeredTraps: player %s -> %d triggered traps", playerID, len(traps))
	return traps, nil
}
