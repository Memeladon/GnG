package repositories

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"reflect"
	"strings"
)

// BaseRepository определяет интерфейс для всех операций репозитория
type BaseRepository interface {
	// Базовые CRUD операции
	CreateOne(ctx context.Context, data interface{}) (interface{}, error)
	CreateMany(ctx context.Context, dataList []interface{}) ([]interface{}, error)
	GetOne(ctx context.Context, recordID interface{}) (interface{}, error)
	GetAll(ctx context.Context) ([]interface{}, error)
	UpdateOne(ctx context.Context, data interface{}) (interface{}, error)
	UpdateBy(ctx context.Context, filters map[string]interface{}, updateData map[string]interface{}) (int, error)
	DeleteOne(ctx context.Context, recordID interface{}) (bool, error)
	DeleteBy(ctx context.Context, filters map[string]interface{}) (int, error)
	DeleteAll(ctx context.Context) (int, error)

	// Более сложные запросы
	FindBy(ctx context.Context, filters map[string]interface{}) ([]interface{}, error)
	FindOneBy(ctx context.Context, filters map[string]interface{}) (interface{}, error)
	GetPaginated(ctx context.Context, offset, limit int, orderBy string, descOrder bool) ([]interface{}, error)
	Count(ctx context.Context, filters map[string]interface{}) (int, error)
	Exists(ctx context.Context, recordID interface{}) (bool, error)
	ExistsBy(ctx context.Context, filters map[string]interface{}) (bool, error)

	// Утилиты
	GetTableName() string
	GetDB() *sql.DB
}

// BaseRepositoryImpl предоставляет общую реализацию для операций репозитория
type BaseRepositoryImpl struct {
	db        *sql.DB
	tableName string
	modelType reflect.Type
}

// NewBaseRepository создает новый базовый репозиторий
func NewBaseRepository(db *sql.DB, tableName string, modelType reflect.Type) *BaseRepositoryImpl {
	return &BaseRepositoryImpl{
		db:        db,
		tableName: tableName,
		modelType: modelType,
	}
}

// GetDB возвращает соединение с базой данных
func (repo *BaseRepositoryImpl) GetDB() *sql.DB {
	return repo.db
}

// GetTableName возвращает название таблицы
func (repo *BaseRepositoryImpl) GetTableName() string {
	return repo.tableName
}

// CreateOne создает новую запись
func (repo *BaseRepositoryImpl) CreateOne(ctx context.Context, data interface{}) (interface{}, error) {
	dataMap, err := repo.structToMap(data)
	if err != nil {
		return nil, fmt.Errorf("error converting data to map: %w", err)
	}

	columns := make([]string, 0, len(dataMap))
	values := make([]interface{}, 0, len(dataMap))
	placeholders := make([]string, 0, len(dataMap))

	i := 1
	for column, value := range dataMap {
		columns = append(columns, column)
		values = append(values, value)
		placeholders = append(placeholders, fmt.Sprintf("$%d", i))
		i++
	}

	query := fmt.Sprintf(
		"INSERT INTO %s (%s) VALUES (%s) RETURNING *",
		repo.tableName,
		strings.Join(columns, ", "),
		strings.Join(placeholders, ", "),
	)

	row := repo.db.QueryRowContext(ctx, query, values...)

	// Create a new instance of the model
	result := reflect.New(repo.modelType).Interface()

	// Get the value and scan into it
	val := reflect.ValueOf(result).Elem()
	scanArgs := make([]interface{}, val.NumField())

	for i := 0; i < val.NumField(); i++ {
		scanArgs[i] = val.Field(i).Addr().Interface()
	}

	err = row.Scan(scanArgs...)
	if err != nil {
		return nil, fmt.Errorf("error creating record: %w", err)
	}

	log.Printf("CreateOne: %s -> CREATED", repo.tableName)
	return result, nil
}

// CreateMany создает несколько записей
func (repo *BaseRepositoryImpl) CreateMany(ctx context.Context, dataList []interface{}) ([]interface{}, error) {
	if len(dataList) == 0 {
		return []interface{}{}, nil
	}

	tx, err := repo.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("error beginning transaction: %w", err)
	}
	defer tx.Rollback()

	var results []interface{}

	for _, data := range dataList {
		dataMap, err := repo.structToMap(data)
		if err != nil {
			return nil, fmt.Errorf("error converting data to map: %w", err)
		}

		columns := make([]string, 0, len(dataMap))
		values := make([]interface{}, 0, len(dataMap))
		placeholders := make([]string, 0, len(dataMap))

		i := 1
		for column, value := range dataMap {
			columns = append(columns, column)
			values = append(values, value)
			placeholders = append(placeholders, fmt.Sprintf("$%d", i))
			i++
		}

		query := fmt.Sprintf(
			"INSERT INTO %s (%s) VALUES (%s) RETURNING *",
			repo.tableName,
			strings.Join(columns, ", "),
			strings.Join(placeholders, ", "),
		)

		row := tx.QueryRowContext(ctx, query, values...)

		result := reflect.New(repo.modelType).Interface()

		val := reflect.ValueOf(result).Elem()
		scanArgs := make([]interface{}, val.NumField())

		for i := 0; i < val.NumField(); i++ {
			scanArgs[i] = val.Field(i).Addr().Interface()
		}

		err = row.Scan(scanArgs...)
		if err != nil {
			return nil, fmt.Errorf("error creating record: %w", err)
		}

		results = append(results, result)
	}

	if err := tx.Commit(); err != nil {
		return nil, fmt.Errorf("error committing transaction: %w", err)
	}

	log.Printf("CreateMany: %s %d items -> CREATED", repo.tableName, len(dataList))
	return results, nil
}

// GetOne получает запись по ID
func (repo *BaseRepositoryImpl) GetOne(ctx context.Context, recordID interface{}) (interface{}, error) {
	query := fmt.Sprintf("SELECT * FROM %s WHERE id = $1", repo.tableName)

	row := repo.db.QueryRowContext(ctx, query, recordID)

	result := reflect.New(repo.modelType).Interface()

	val := reflect.ValueOf(result).Elem()
	scanArgs := make([]interface{}, val.NumField())

	for i := 0; i < val.NumField(); i++ {
		scanArgs[i] = val.Field(i).Addr().Interface()
	}

	err := row.Scan(scanArgs...)
	if err != nil {
		if err == sql.ErrNoRows {
			log.Printf("GetOne: %s id=%v -> NOT FOUND", repo.tableName, recordID)
			return nil, nil
		}
		return nil, fmt.Errorf("error getting record by ID: %w", err)
	}

	log.Printf("GetOne: %s id=%v -> FOUND", repo.tableName, recordID)
	return result, nil
}

// GetAll получает все записи
func (repo *BaseRepositoryImpl) GetAll(ctx context.Context) ([]interface{}, error) {
	query := fmt.Sprintf("SELECT * FROM %s", repo.tableName)

	rows, err := repo.db.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("error listing records: %w", err)
	}
	defer rows.Close()

	var results []interface{}
	for rows.Next() {
		result := reflect.New(repo.modelType).Interface()

		val := reflect.ValueOf(result).Elem()
		scanArgs := make([]interface{}, val.NumField())

		for i := 0; i < val.NumField(); i++ {
			scanArgs[i] = val.Field(i).Addr().Interface()
		}

		if err := rows.Scan(scanArgs...); err != nil {
			return nil, fmt.Errorf("error scanning record: %w", err)
		}
		results = append(results, result)
	}

	log.Printf("GetAll: %s -> %d items", repo.tableName, len(results))
	return results, nil
}

// UpdateOne обновляет существующую запись по ID
func (repo *BaseRepositoryImpl) UpdateOne(ctx context.Context, data interface{}) (interface{}, error) {
	dataMap, err := repo.structToMap(data)
	if err != nil {
		return nil, fmt.Errorf("error converting data to map: %w", err)
	}

	recordID := dataMap["id"]
	if recordID == nil {
		return nil, fmt.Errorf("ID is required for UpdateOne")
	}

	// Remove id from update data
	delete(dataMap, "id")

	if len(dataMap) == 0 {
		return nil, fmt.Errorf("no data to update")
	}

	setClauses := make([]string, 0, len(dataMap))
	values := make([]interface{}, 0, len(dataMap)+1)

	i := 1
	for column, value := range dataMap {
		setClauses = append(setClauses, fmt.Sprintf("%s = $%d", column, i))
		values = append(values, value)
		i++
	}
	values = append(values, recordID) // ID for WHERE clause

	query := fmt.Sprintf(
		"UPDATE %s SET %s WHERE id = $%d RETURNING *",
		repo.tableName,
		strings.Join(setClauses, ", "),
		i,
	)

	row := repo.db.QueryRowContext(ctx, query, values...)

	// Create a new instance of the model
	result := reflect.New(repo.modelType).Interface()

	// Get the value and scan into it
	val := reflect.ValueOf(result).Elem()
	scanArgs := make([]interface{}, val.NumField())

	for i := 0; i < val.NumField(); i++ {
		scanArgs[i] = val.Field(i).Addr().Interface()
	}

	err = row.Scan(scanArgs...)
	if err != nil {
		if err == sql.ErrNoRows {
			log.Printf("UpdateOne: %s id=%v -> NOT FOUND", repo.tableName, recordID)
			return nil, nil
		}
		return nil, fmt.Errorf("error updating record: %w", err)
	}

	log.Printf("UpdateOne: %s id=%v -> UPDATED", repo.tableName, recordID)
	return result, nil
}

// UpdateBy обновляет записи по фильтрам
func (repo *BaseRepositoryImpl) UpdateBy(ctx context.Context, filters map[string]interface{}, updateData map[string]interface{}) (int, error) {
	if len(filters) == 0 {
		return 0, fmt.Errorf("filters cannot be empty for UpdateBy")
	}

	// Build SET clause
	setClauses := make([]string, 0, len(updateData))
	values := make([]interface{}, 0, len(updateData)+len(filters))

	i := 1
	for column, value := range updateData {
		setClauses = append(setClauses, fmt.Sprintf("%s = $%d", column, i))
		values = append(values, value)
		i++
	}

	// Build WHERE clause
	whereClauses := make([]string, 0, len(filters))
	for column, value := range filters {
		whereClauses = append(whereClauses, fmt.Sprintf("%s = $%d", column, i))
		values = append(values, value)
		i++
	}

	query := fmt.Sprintf(
		"UPDATE %s SET %s WHERE %s",
		repo.tableName,
		strings.Join(setClauses, ", "),
		strings.Join(whereClauses, " AND "),
	)

	result, err := repo.db.ExecContext(ctx, query, values...)
	if err != nil {
		return 0, fmt.Errorf("error updating records: %w", err)
	}

	rowsAffected, _ := result.RowsAffected()
	log.Printf("UpdateBy: %s %v -> %d rows updated", repo.tableName, filters, rowsAffected)
	return int(rowsAffected), nil
}

// DeleteOne удаляет запись по ID
func (repo *BaseRepositoryImpl) DeleteOne(ctx context.Context, recordID interface{}) (bool, error) {
	query := fmt.Sprintf("DELETE FROM %s WHERE id = $1", repo.tableName)

	result, err := repo.db.ExecContext(ctx, query, recordID)
	if err != nil {
		return false, fmt.Errorf("error deleting record: %w", err)
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		log.Printf("DeleteOne: %s id=%v -> NOT FOUND", repo.tableName, recordID)
		return false, nil
	}

	log.Printf("DeleteOne: %s id=%v -> DELETED", repo.tableName, recordID)
	return true, nil
}

// DeleteBy удаляет записи по фильтрам
func (repo *BaseRepositoryImpl) DeleteBy(ctx context.Context, filters map[string]interface{}) (int, error) {
	if len(filters) == 0 {
		return 0, fmt.Errorf("filters cannot be empty for DeleteBy")
	}

 
	whereClauses := make([]string, 0, len(filters))
	values := make([]interface{}, 0, len(filters))

	i := 1
	for column, value := range filters {
		whereClauses = append(whereClauses, fmt.Sprintf("%s = $%d", column, i))
		values = append(values, value)
		i++
	}

	query := fmt.Sprintf(
		"DELETE FROM %s WHERE %s",
		repo.tableName,
		strings.Join(whereClauses, " AND "),
	)

	result, err := repo.db.ExecContext(ctx, query, values...)
	if err != nil {
		return 0, fmt.Errorf("error deleting records: %w", err)
	}

	rowsAffected, _ := result.RowsAffected()
	log.Printf("DeleteBy: %s %v -> %d rows deleted", repo.tableName, filters, rowsAffected)
	return int(rowsAffected), nil
}

// DeleteAll удаляет все записи
func (repo *BaseRepositoryImpl) DeleteAll(ctx context.Context) (int, error) {
	query := fmt.Sprintf("DELETE FROM %s", repo.tableName)

	result, err := repo.db.ExecContext(ctx, query)
	if err != nil {
		return 0, fmt.Errorf("error deleting all records: %w", err)
	}

	rowsAffected, _ := result.RowsAffected()
	log.Printf("DeleteAll: %s -> %d rows deleted", repo.tableName, rowsAffected)
	return int(rowsAffected), nil
}

// FindBy находит записи по фильтрам
func (repo *BaseRepositoryImpl) FindBy(ctx context.Context, filters map[string]interface{}) ([]interface{}, error) {
	if len(filters) == 0 {
		return repo.GetAll(ctx)
	}

	// Build WHERE clause
	whereClauses := make([]string, 0, len(filters))
	values := make([]interface{}, 0, len(filters))

	i := 1
	for column, value := range filters {
		whereClauses = append(whereClauses, fmt.Sprintf("%s = $%d", column, i))
		values = append(values, value)
		i++
	}

	query := fmt.Sprintf(
		"SELECT * FROM %s WHERE %s",
		repo.tableName,
		strings.Join(whereClauses, " AND "),
	)

	rows, err := repo.db.QueryContext(ctx, query, values...)
	if err != nil {
		return nil, fmt.Errorf("error finding records: %w", err)
	}
	defer rows.Close()

	var results []interface{}
	for rows.Next() {
		// Create a new instance of the model
		result := reflect.New(repo.modelType).Interface()

		// Get the value and scan into it
		val := reflect.ValueOf(result).Elem()
		scanArgs := make([]interface{}, val.NumField())

		for i := 0; i < val.NumField(); i++ {
			scanArgs[i] = val.Field(i).Addr().Interface()
		}

		if err := rows.Scan(scanArgs...); err != nil {
			return nil, fmt.Errorf("error scanning record: %w", err)
		}
		results = append(results, result)
	}

	log.Printf("FindBy: %s %v -> %d items", repo.tableName, filters, len(results))
	return results, nil
}

// FindOneBy находит одну запись по фильтрам
func (repo *BaseRepositoryImpl) FindOneBy(ctx context.Context, filters map[string]interface{}) (interface{}, error) {
	if len(filters) == 0 {
		return nil, fmt.Errorf("filters cannot be empty for FindOneBy")
	}

	whereClauses := make([]string, 0, len(filters))
	values := make([]interface{}, 0, len(filters))

	i := 1
	for column, value := range filters {
		whereClauses = append(whereClauses, fmt.Sprintf("%s = $%d", column, i))
		values = append(values, value)
		i++
	}

	query := fmt.Sprintf(
		"SELECT * FROM %s WHERE %s LIMIT 1",
		repo.tableName,
		strings.Join(whereClauses, " AND "),
	)

	row := repo.db.QueryRowContext(ctx, query, values...)

	result := reflect.New(repo.modelType).Interface()

	val := reflect.ValueOf(result).Elem()
	scanArgs := make([]interface{}, val.NumField())

	for i := 0; i < val.NumField(); i++ {
		scanArgs[i] = val.Field(i).Addr().Interface()
	}

	err := row.Scan(scanArgs...)
	if err != nil {
		if err == sql.ErrNoRows {
			log.Printf("FindOneBy: %s %v -> NOT FOUND", repo.tableName, filters)
			return nil, nil
		}
		return nil, fmt.Errorf("error finding record: %w", err)
	}

	log.Printf("FindOneBy: %s %v -> FOUND", repo.tableName, filters)
	return result, nil
}

// GetPaginated получает записи с пагинацией и сортировкой
func (repo *BaseRepositoryImpl) GetPaginated(ctx context.Context, offset, limit int, orderBy string, descOrder bool) ([]interface{}, error) {
	query := fmt.Sprintf("SELECT * FROM %s", repo.tableName)

	if orderBy != "" {
		orderDirection := "ASC"
		if descOrder {
			orderDirection = "DESC"
		}
		query += fmt.Sprintf(" ORDER BY %s %s", orderBy, orderDirection)
	}

	query += fmt.Sprintf(" OFFSET %d LIMIT %d", offset, limit)

	rows, err := repo.db.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("error getting paginated records: %w", err)
	}
	defer rows.Close()

	var results []interface{}
	for rows.Next() {
		result := reflect.New(repo.modelType).Interface()

		val := reflect.ValueOf(result).Elem()
		scanArgs := make([]interface{}, val.NumField())

		for i := 0; i < val.NumField(); i++ {
			scanArgs[i] = val.Field(i).Addr().Interface()
		}

		if err := rows.Scan(scanArgs...); err != nil {
			return nil, fmt.Errorf("error scanning record: %w", err)
		}
		results = append(results, result)
	}

	log.Printf("GetPaginated: %s offset=%d limit=%d -> %d items", repo.tableName, offset, limit, len(results))
	return results, nil
}

// Count подсчитывает записи с опциональными фильтрами
func (repo *BaseRepositoryImpl) Count(ctx context.Context, filters map[string]interface{}) (int, error) {
	query := fmt.Sprintf("SELECT COUNT(*) FROM %s", repo.tableName)
	var values []interface{}

	if len(filters) > 0 {
		whereClauses := make([]string, 0, len(filters))
		i := 1
		for column, value := range filters {
			whereClauses = append(whereClauses, fmt.Sprintf("%s = $%d", column, i))
			values = append(values, value)
			i++
		}
		query += fmt.Sprintf(" WHERE %s", strings.Join(whereClauses, " AND "))
	}

	var count int
	err := repo.db.QueryRowContext(ctx, query, values...).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("error counting records: %w", err)
	}

	return count, nil
}

// Exists проверяет существование записи по ID
func (repo *BaseRepositoryImpl) Exists(ctx context.Context, recordID interface{}) (bool, error) {
	query := fmt.Sprintf("SELECT EXISTS(SELECT 1 FROM %s WHERE id = $1)", repo.tableName)

	var exists bool
	err := repo.db.QueryRowContext(ctx, query, recordID).Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("error checking existence: %w", err)
	}

	return exists, nil
}

// ExistsBy проверяет существование записи по фильтрам
func (repo *BaseRepositoryImpl) ExistsBy(ctx context.Context, filters map[string]interface{}) (bool, error) {
	if len(filters) == 0 {
		return false, fmt.Errorf("filters cannot be empty for ExistsBy")
	}

	whereClauses := make([]string, 0, len(filters))
	values := make([]interface{}, 0, len(filters))

	i := 1
	for column, value := range filters {
		whereClauses = append(whereClauses, fmt.Sprintf("%s = $%d", column, i))
		values = append(values, value)
		i++
	}

	query := fmt.Sprintf(
		"SELECT EXISTS(SELECT 1 FROM %s WHERE %s)",
		repo.tableName,
		strings.Join(whereClauses, " AND "),
	)

	var exists bool
	err := repo.db.QueryRowContext(ctx, query, values...).Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("error checking existence: %w", err)
	}

	return exists, nil
}

// Вспомогательный метод для преобразования структуры в карту
func (repo *BaseRepositoryImpl) structToMap(data interface{}) (map[string]interface{}, error) {
	result := make(map[string]interface{})

	val := reflect.ValueOf(data)
	if val.Kind() == reflect.Ptr {
		val = val.Elem()
	}

	if val.Kind() != reflect.Struct {
		return nil, fmt.Errorf("data должна быть структурой или указателем на структуру")
	}

	typ := val.Type()
	for i := 0; i < val.NumField(); i++ {
		field := val.Field(i)
		fieldType := typ.Field(i)

		dbTag := fieldType.Tag.Get("db")
		if dbTag == "" || dbTag == "-" {
			continue
		}

		if field.IsZero() && !fieldType.Type.Implements(reflect.TypeOf((*sql.NullString)(nil)).Elem()) {
			continue
		}

		result[dbTag] = field.Interface()
	}

	return result, nil
}
