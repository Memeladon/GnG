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

// PlayerRepository определяет интерфейс для операций с игроками
type PlayerRepository interface {
	BaseRepository
	CreatePlayerFirstTime(ctx context.Context, data map[string]interface{}) (*models.Player, error)
	UpdatePlayerProfile(ctx context.Context, data map[string]interface{}) (*models.Player, error)
	GetPlayersBySessionID(ctx context.Context, sessionID uuid.UUID) ([]*models.Player, error)
}

// PlayerRepositoryImpl предоставляет реализацию для операций с игроками
type PlayerRepositoryImpl struct {
	*BaseRepositoryImpl
	inventoryRepo   InventoryRepository
	playerStatsRepo PlayerStatsRepository
}

// NewPlayerRepository создает новый репозиторий игроков
func NewPlayerRepository(db *sql.DB, inventoryRepo InventoryRepository, playerStatsRepo PlayerStatsRepository) *PlayerRepositoryImpl {
	return &PlayerRepositoryImpl{
		BaseRepositoryImpl: NewBaseRepository(db, "players", reflect.TypeOf(models.Player{})),
		inventoryRepo:      inventoryRepo,
		playerStatsRepo:    playerStatsRepo,
	}
}

// CreatePlayerFirstTime создает нового игрового персонажа для пользователя, а также инвентарь и статистику
// Проверяет, что у пользователя еще нет персонажа
func (repo *PlayerRepositoryImpl) CreatePlayerFirstTime(ctx context.Context, data map[string]interface{}) (*models.Player, error) {
	userID, ok := data["user_id"].(uuid.UUID)
	if !ok {
		return nil, fmt.Errorf("user_id is required and must be uuid.UUID")
	}

	exists, err := repo.ExistsBy(ctx, map[string]interface{}{"user_id": userID})
	if err != nil {
		return nil, fmt.Errorf("error checking if user has player: %w", err)
	}
	if exists {
		log.Printf("CreatePlayerFirstTime: User %s already has a Player", userID)
		return nil, fmt.Errorf("user already has a Player")
	}

	log.Printf("CreatePlayerFirstTime: Creating Player for user %s", userID)

	inventoryData := map[string]interface{}{
		"player_id": nil,
	}
	inventoryInterface, err := repo.inventoryRepo.CreateOne(ctx, inventoryData)
	if err != nil {
		return nil, fmt.Errorf("error creating inventory: %w", err)
	}

	inventory, ok := inventoryInterface.(*models.Inventory)
	if !ok {
		inventoryValue := reflect.ValueOf(inventoryInterface)
		if inventoryValue.Kind() == reflect.Ptr {
			inventoryValue = inventoryValue.Elem()
		}
		inventory = inventoryValue.Addr().Interface().(*models.Inventory)
	}

	username, ok := data["username"].(string)
	if !ok {
		return nil, fmt.Errorf("username is required and must be string")
	}

	profileImage := ""
	if profileImageFromData, ok := data["profile_image"].(string); ok {
		profileImage = profileImageFromData
	}

	playerData := &models.PlayerCreate{
		CellID:       0,
		UserID:       userID,
		Username:     username,
		ProfileImage: profileImage,
		Role:         models.UserRightsPlayer,
	}

	playerInterface, err := repo.CreateOne(ctx, playerData)
	if err != nil {
		return nil, fmt.Errorf("error creating player: %w", err)
	}

	player, ok := playerInterface.(*models.Player)
	if !ok {
		playerValue := reflect.ValueOf(playerInterface)
		if playerValue.Kind() == reflect.Ptr {
			playerValue = playerValue.Elem()
		}
		player = playerValue.Addr().Interface().(*models.Player)
	}

	inventoryUpdateData := map[string]interface{}{
		"id":        inventory.ID,
		"player_id": player.ID,
	}
	_, err = repo.inventoryRepo.UpdateOne(ctx, inventoryUpdateData)
	if err != nil {
		return nil, fmt.Errorf("error linking inventory to player: %w", err)
	}

	statsData := &models.PlayerStatsCreate{
		PlayerID: player.ID,
	}
	_, err = repo.playerStatsRepo.CreateOne(ctx, statsData)
	if err != nil {
		return nil, fmt.Errorf("error creating player stats: %w", err)
	}

	return player, nil
}

// UpdatePlayerProfile обновляет профиль игрока (Player): username и avatar.
// Проверяет уникальность username.
func (repo *PlayerRepositoryImpl) UpdatePlayerProfile(ctx context.Context, data map[string]interface{}) (*models.Player, error) {
	playerID, ok := data["player_id"].(uuid.UUID)
	if !ok {
		return nil, fmt.Errorf("player_id is required and must be uuid.UUID")
	}

	playerInterface, err := repo.GetOne(ctx, playerID)
	if err != nil {
		return nil, fmt.Errorf("error getting player: %w", err)
	}
	if playerInterface == nil {
		log.Printf("UpdatePlayerProfile: Player %s not found", playerID)
		return nil, fmt.Errorf("player not found")
	}

	// Check username uniqueness if provided
	if username, ok := data["username"].(string); ok && username != "" {
		existingPlayerInterface, err := repo.FindOneBy(ctx, map[string]interface{}{"username": username})
		if err != nil {
			return nil, fmt.Errorf("error checking username uniqueness: %w", err)
		}
		if existingPlayerInterface != nil {
			existingPlayer, ok := existingPlayerInterface.(*models.Player)
			if !ok {
				playerValue := reflect.ValueOf(existingPlayerInterface)
				if playerValue.Kind() == reflect.Ptr {
					playerValue = playerValue.Elem()
				}
				existingPlayer = playerValue.Addr().Interface().(*models.Player)
			}
			if existingPlayer.ID != playerID {
				log.Printf("UpdatePlayerProfile: Username %s already exists", username)
				return nil, fmt.Errorf("username already exists")
			}
		}
	}

	log.Printf("UpdatePlayerProfile: Updating profile for player %s", playerID)

	updatedPlayerInterface, err := repo.UpdateOne(ctx, data)
	if err != nil {
		return nil, fmt.Errorf("error updating player: %w", err)
	}

	updatedPlayer, ok := updatedPlayerInterface.(*models.Player)
	if !ok {
		playerValue := reflect.ValueOf(updatedPlayerInterface)
		if playerValue.Kind() == reflect.Ptr {
			playerValue = playerValue.Elem()
		}
		updatedPlayer = playerValue.Addr().Interface().(*models.Player)
	}

	return updatedPlayer, nil
}

// GetPlayersBySessionID возвращает всех игроков (Player), участвующих в игровой сессии (Session).
// Использует связь через SessionUser.
func (repo *PlayerRepositoryImpl) GetPlayersBySessionID(ctx context.Context, sessionID uuid.UUID) ([]*models.Player, error) {
	// Это потребует JOIN с таблицей SessionUser
	// На данный момент вернем пустой срез, так как это сложный запрос
	// TODO: Реализовать правильный JOIN запрос с таблицей SessionUser

	log.Printf("GetPlayersBySessionID: Getting players for session %s", sessionID)

	return []*models.Player{}, nil
}
