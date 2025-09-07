package repositories

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"reflect"

	"gng/internal/models"
)

// CellRepository определяет интерфейс для операций с ячейками
type CellRepository interface {
	BaseRepository
	AddTrapToCell(ctx context.Context, cellID int, trapData map[string]interface{}) (*models.Cell, error)
	RemoveTrapFromCell(ctx context.Context, cellID int, trapIndex int) (*models.Cell, error)
	GetCellTraps(ctx context.Context, cellID int) ([]map[string]interface{}, error)
}

// CellRepositoryImpl предоставляет реализацию для операций с ячейками
type CellRepositoryImpl struct {
	*BaseRepositoryImpl
}

// NewCellRepository создает новый репозиторий ячеек
func NewCellRepository(db *sql.DB) *CellRepositoryImpl {
	return &CellRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "cells", reflect.TypeOf(models.Cell{})),
	}
}

// AddTrapToCell добавляет ловушку в JSON поле traps ячейки
func (repo *CellRepositoryImpl) AddTrapToCell(ctx context.Context, cellID int, trapData map[string]interface{}) (*models.Cell, error) {
	cellInterface, err := repo.GetOne(ctx, cellID)
	if err != nil {
		return nil, fmt.Errorf("error getting cell: %w", err)
	}
	if cellInterface == nil {
		return nil, fmt.Errorf("cell not found")
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
		cell.Traps = make([]map[string]interface{}, 0)
	}
	cell.Traps = append(cell.Traps, trapData)

	updateData := map[string]interface{}{
		"id":    cellID,
		"traps": cell.Traps,
	}

	updatedInterface, err := repo.UpdateOne(ctx, updateData)
	if err != nil {
		return nil, fmt.Errorf("error updating cell: %w", err)
	}

	updatedCell, ok := updatedInterface.(*models.Cell)
	if !ok {
		cellValue := reflect.ValueOf(updatedInterface)
		if cellValue.Kind() == reflect.Ptr {
			cellValue = cellValue.Elem()
		}
		updatedCell = cellValue.Addr().Interface().(*models.Cell)
	}

	log.Printf("AddTrapToCell: cell %d -> trap added", cellID)
	return updatedCell, nil
}

// RemoveTrapFromCell удаляет ловушку из JSON поля traps ячейки по индексу
func (repo *CellRepositoryImpl) RemoveTrapFromCell(ctx context.Context, cellID int, trapIndex int) (*models.Cell, error) {
	cellInterface, err := repo.GetOne(ctx, cellID)
	if err != nil {
		return nil, fmt.Errorf("error getting cell: %w", err)
	}
	if cellInterface == nil {
		return nil, fmt.Errorf("cell not found")
	}

	cell, ok := cellInterface.(*models.Cell)
	if !ok {
		// Пытаюсь преобразовать интерфейс в models.Cell
		cellValue := reflect.ValueOf(cellInterface)
		if cellValue.Kind() == reflect.Ptr {
			cellValue = cellValue.Elem()
		}
		cell = cellValue.Addr().Interface().(*models.Cell)
	}

	// Удаляем ловушку из массива traps
	if cell.Traps != nil && trapIndex >= 0 && trapIndex < len(cell.Traps) {
		cell.Traps = append(cell.Traps[:trapIndex], cell.Traps[trapIndex+1:]...)
	}

	updateData := map[string]interface{}{
		"id":    cellID,
		"traps": cell.Traps,
	}

	updatedInterface, err := repo.UpdateOne(ctx, updateData)
	if err != nil {
		return nil, fmt.Errorf("error updating cell: %w", err)
	}

	updatedCell, ok := updatedInterface.(*models.Cell)
	if !ok {
		// Пытаюсь преобразовать интерфейс в models.Cell
		cellValue := reflect.ValueOf(updatedInterface)
		if cellValue.Kind() == reflect.Ptr {
			cellValue = cellValue.Elem()
		}
		updatedCell = cellValue.Addr().Interface().(*models.Cell)
	}

	log.Printf("RemoveTrapFromCell: cell %d -> trap at index %d removed", cellID, trapIndex)
	return updatedCell, nil
}

// GetCellTraps получает список ловушек для ячейки
func (repo *CellRepositoryImpl) GetCellTraps(ctx context.Context, cellID int) ([]map[string]interface{}, error) {
	cellInterface, err := repo.GetOne(ctx, cellID)
	if err != nil {
		return nil, fmt.Errorf("error getting cell: %w", err)
	}
	if cellInterface == nil {
		return []map[string]interface{}{}, nil
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
		return []map[string]interface{}{}, nil
	}

	return cell.Traps, nil
}
