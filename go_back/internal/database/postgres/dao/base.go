package dao

import (
	"context"
	"database/sql"
)

// BaseDAO provides common database operations
type BaseDAO interface {
	// GetByID retrieves a record by ID
	GetByID(ctx context.Context, id interface{}) (interface{}, error)

	// Create creates a new record
	Create(ctx context.Context, data interface{}) (interface{}, error)

	// Update updates an existing record
	Update(ctx context.Context, id interface{}, data interface{}) (interface{}, error)

	// Delete deletes a record by ID
	Delete(ctx context.Context, id interface{}) error

	// List retrieves multiple records with optional filtering
	List(ctx context.Context, limit, offset int) ([]interface{}, error)
}

// BaseDAOImpl provides common implementation for DAO operations
type BaseDAOImpl struct {
	db *sql.DB
}

// NewBaseDAO creates a new base DAO
func NewBaseDAO(db *sql.DB) *BaseDAOImpl {
	return &BaseDAOImpl{db: db}
}

// GetDB returns the database connection
func (dao *BaseDAOImpl) GetDB() *sql.DB {
	return dao.db
}
