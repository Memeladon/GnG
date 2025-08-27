package dao

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"gng/internal/models"

	"github.com/google/uuid"
)

// UserDAO provides database operations for users
type UserDAO struct {
	*BaseDAOImpl
}

// NewUserDAO creates a new user DAO
func NewUserDAO(db *sql.DB) *UserDAO {
	return &UserDAO{BaseDAOImpl: NewBaseDAO(db)}
}

// GetByID retrieves a user by ID
func (dao *UserDAO) GetByID(ctx context.Context, id interface{}) (*models.User, error) {
	userID, ok := id.(uuid.UUID)
	if !ok {
		return nil, fmt.Errorf("invalid user ID type")
	}

	query := `
		SELECT id, login, password, mail, is_active, created_at, updated_at
		FROM users
		WHERE id = $1
	`

	user := &models.User{}
	err := dao.db.QueryRowContext(ctx, query, userID).Scan(
		&user.ID,
		&user.Login,
		&user.Password,
		&user.Mail,
		&user.IsActive,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("user not found")
		}
		return nil, fmt.Errorf("failed to get user: %w", err)
	}

	return user, nil
}

// GetByLogin retrieves a user by login
func (dao *UserDAO) GetByLogin(ctx context.Context, login string) (*models.User, error) {
	query := `
		SELECT id, login, password, mail, is_active, created_at, updated_at
		FROM users
		WHERE login = $1
	`

	user := &models.User{}
	err := dao.db.QueryRowContext(ctx, query, login).Scan(
		&user.ID,
		&user.Login,
		&user.Password,
		&user.Mail,
		&user.IsActive,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("user not found")
		}
		return nil, fmt.Errorf("failed to get user by login: %w", err)
	}

	return user, nil
}

// Create creates a new user
func (dao *UserDAO) Create(ctx context.Context, data interface{}) (*models.User, error) {
	userData, ok := data.(*models.UserCreate)
	if !ok {
		return nil, fmt.Errorf("invalid user data type")
	}

	query := `
		INSERT INTO users (id, login, password, mail, is_active, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING id, login, password, mail, is_active, created_at, updated_at
	`

	now := time.Now()
	userID := uuid.New()

	user := &models.User{}
	err := dao.db.QueryRowContext(ctx, query,
		userID,
		userData.Login,
		userData.Password,
		userData.Mail,
		true, // is_active default to true
		now,
		now,
	).Scan(
		&user.ID,
		&user.Login,
		&user.Password,
		&user.Mail,
		&user.IsActive,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err != nil {
		return nil, fmt.Errorf("failed to create user: %w", err)
	}

	return user, nil
}

// Update updates an existing user
func (dao *UserDAO) Update(ctx context.Context, id interface{}, data interface{}) (*models.User, error) {
	userID, ok := id.(uuid.UUID)
	if !ok {
		return nil, fmt.Errorf("invalid user ID type")
	}

	userData, ok := data.(*models.UserUpdate)
	if !ok {
		return nil, fmt.Errorf("invalid user update data type")
	}

	// Build dynamic query based on provided fields
	query := "UPDATE users SET updated_at = $1"
	args := []interface{}{time.Now()}
	argIndex := 2

	if userData.Login != nil {
		query += fmt.Sprintf(", login = $%d", argIndex)
		args = append(args, *userData.Login)
		argIndex++
	}

	if userData.Password != nil {
		query += fmt.Sprintf(", password = $%d", argIndex)
		args = append(args, *userData.Password)
		argIndex++
	}

	if userData.Mail != nil {
		query += fmt.Sprintf(", mail = $%d", argIndex)
		args = append(args, *userData.Mail)
		argIndex++
	}

	if userData.IsActive != nil {
		query += fmt.Sprintf(", is_active = $%d", argIndex)
		args = append(args, *userData.IsActive)
		argIndex++
	}

	query += fmt.Sprintf(" WHERE id = $%d", argIndex)
	args = append(args, userID)

	query += " RETURNING id, login, password, mail, is_active, created_at, updated_at"

	user := &models.User{}
	err := dao.db.QueryRowContext(ctx, query, args...).Scan(
		&user.ID,
		&user.Login,
		&user.Password,
		&user.Mail,
		&user.IsActive,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("user not found")
		}
		return nil, fmt.Errorf("failed to update user: %w", err)
	}

	return user, nil
}

// Delete deletes a user by ID
func (dao *UserDAO) Delete(ctx context.Context, id interface{}) error {
	userID, ok := id.(uuid.UUID)
	if !ok {
		return fmt.Errorf("invalid user ID type")
	}

	query := "DELETE FROM users WHERE id = $1"
	result, err := dao.db.ExecContext(ctx, query, userID)
	if err != nil {
		return fmt.Errorf("failed to delete user: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("user not found")
	}

	return nil
}

// List retrieves multiple users with pagination
func (dao *UserDAO) List(ctx context.Context, limit, offset int) ([]*models.User, error) {
	query := `
		SELECT id, login, password, mail, is_active, created_at, updated_at
		FROM users
		ORDER BY created_at DESC
		LIMIT $1 OFFSET $2
	`

	rows, err := dao.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query users: %w", err)
	}
	defer rows.Close()

	var users []*models.User
	for rows.Next() {
		user := &models.User{}
		err := rows.Scan(
			&user.ID,
			&user.Login,
			&user.Password,
			&user.Mail,
			&user.IsActive,
			&user.CreatedAt,
			&user.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan user: %w", err)
		}
		users = append(users, user)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating users: %w", err)
	}

	return users, nil
}
