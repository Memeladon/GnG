package repositories

import (
	"context"
	"database/sql"
	"fmt"
	"reflect"

	"gng/internal/models"
)

// CellRepository определяет интерфейс для операций с клетками
type CellRepository interface {
	BaseRepository
	AddTrapToCell(ctx context.Context, cellID int, trapData map[string]any) (*models.Cell, error)
	RemoveTrapFromCell(ctx context.Context, cellID int, trapIndex int) (*models.Cell, error)
	GetCellTraps(ctx context.Context, cellID int) ([]map[string]any, error)
}

// CellRepositoryImpl предоставляет реализацию для операций с клетками
type CellRepositoryImpl struct {
	*BaseRepositoryImpl
}

// NewCellRepository создает новый репозиторий клеток
func NewCellRepository(db *sql.DB) *CellRepositoryImpl {
	return &CellRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "cells", reflect.TypeOf(models.Cell{})),
	}
}

// AddTrapToCell добавляет ловушку в JSON поле traps ячейки
func (repo *CellRepositoryImpl) AddTrapToCell(ctx context.Context, cellID int, trapData map[string]any) (*models.Cell, error) {
	cellInterface, err := repo.GetOne(ctx, cellID)
	if err != nil {
		return nil, fmt.Errorf("failed to create cell: %w", err)
	}

	cellResult, ok := cellInterface.(*models.Cell)
	if !ok {
		cellValue := reflect.ValueOf(cellInterface)
		if cellValue.Kind() == reflect.Ptr {
			cellValue = cellValue.Elem()
		}
		cellResult = cellValue.Addr().Interface().(*models.Cell)
	}

	if cellResult.Traps == nil {
		cellResult.Traps = make([]models.Trap, 0)
	}
	// Convert trapData to models.Trap
	trap := models.Trap{}
	// Map trapData fields to trap struct fields as needed
	cellResult.Traps = append(cellResult.Traps, trap)

	updateData := map[string]any{
		"id":    cellID,
		"traps": cellResult.Traps,
	}

	updatedInterface, err := repo.UpdateOne(ctx, updateData)
	if err != nil {
		return nil, fmt.Errorf("failed to get cell: %w", err)
	}

	if updatedInterface == nil {
		return nil, fmt.Errorf("cell not found")
	}

	cell, ok := updatedInterface.(*models.Cell)
	if !ok {
		cellValue := reflect.ValueOf(updatedInterface)
		if cellValue.Kind() == reflect.Ptr {
			cellValue = cellValue.Elem()
		}
		cell = cellValue.Addr().Interface().(*models.Cell)
	}

	return cell, nil
}

// GetByPosition получает клетку по позиции
func (r *CellRepositoryImpl) GetByPosition(ctx context.Context, position int) (*models.Cell, error) {
	result, err := r.FindOneBy(ctx, map[string]interface{}{"position": position})
	if err != nil {
		return nil, fmt.Errorf("failed to get cell by position: %w", err)
	}

	if result == nil {
		return nil, fmt.Errorf("cell not found")
	}

	cell, ok := result.(*models.Cell)
	if !ok {
		cellValue := reflect.ValueOf(result)
		if cellValue.Kind() == reflect.Ptr {
			cellValue = cellValue.Elem()
		}
		cell = cellValue.Addr().Interface().(*models.Cell)
	}

	return cell, nil
}

// RemoveTrapFromCell удаляет ловушку из JSON поля traps ячейки
func (repo *CellRepositoryImpl) RemoveTrapFromCell(ctx context.Context, cellID int, trapIndex int) (*models.Cell, error) {
	cellInterface, err := repo.GetOne(ctx, cellID)
	if err != nil {
		return nil, fmt.Errorf("failed to get cell: %w", err)
	}

	cellResult, ok := cellInterface.(*models.Cell)
	if !ok {
		cellValue := reflect.ValueOf(cellInterface)
		if cellValue.Kind() == reflect.Ptr {
			cellValue = cellValue.Elem()
		}
		cellResult = cellValue.Addr().Interface().(*models.Cell)
	}

	// Удаляем ловушку из массива traps
	if cellResult.Traps != nil && trapIndex >= 0 && trapIndex < len(cellResult.Traps) {
		cellResult.Traps = append(cellResult.Traps[:trapIndex], cellResult.Traps[trapIndex+1:]...)
	}

	updateData := map[string]any{
		"id":    cellID,
		"traps": cellResult.Traps,
	}

	updatedInterface, err := repo.UpdateOne(ctx, updateData)
	if err != nil {
		return nil, fmt.Errorf("failed to update cell: %w", err)
	}

	if updatedInterface == nil {
		return nil, fmt.Errorf("cell not found")
	}

	cell, ok := updatedInterface.(*models.Cell)
	if !ok {
		cellValue := reflect.ValueOf(updatedInterface)
		if cellValue.Kind() == reflect.Ptr {
			cellValue = cellValue.Elem()
		}
		cell = cellValue.Addr().Interface().(*models.Cell)
	}

	return cell, nil
}

// GetCellTraps получает список ловушек для ячейки
func (repo *CellRepositoryImpl) GetCellTraps(ctx context.Context, cellID int) ([]map[string]any, error) {
	cellInterface, err := repo.GetOne(ctx, cellID)
	if err != nil {
		return nil, fmt.Errorf("failed to get cell: %w", err)
	}
	if cellInterface == nil {
		return []map[string]any{}, nil
	}

	cell, ok := cellInterface.(*models.Cell)
	if !ok {
		cellValue := reflect.ValueOf(cellInterface)
		if cellValue.Kind() == reflect.Ptr {
			cellValue = cellValue.Elem()
		}
		cell = cellValue.Addr().Interface().(*models.Cell)
	}

	if cell.Traps == nil {
		return []map[string]any{}, nil
	}

	// Convert []models.Trap to []map[string]any
	traps := make([]map[string]any, len(cell.Traps))
	for i, trap := range cell.Traps {
		// Convert trap to map - you may need to implement proper field mapping
		traps[i] = map[string]any{
			"id":           trap.ID,
			"name":         trap.Name,
			"description":  trap.Description,
			"effect_type":  trap.EffectType,
			"effect_value": trap.EffectValue,
			"is_active":    trap.IsActive,
		}
	}

	return traps, nil
}
