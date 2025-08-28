package repositories

// Файл экспортирует все типы и интерфейсы репозиториев
// чтобы сделать их доступными для импорта из других пакетов

// Базовый репозиторий
type BaseRepository = BaseRepository
type BaseRepositoryImpl = BaseRepositoryImpl

// Cell repository
type CellRepository = CellRepository
type CellRepositoryImpl = CellRepositoryImpl

// Game repository
type GameRepository = GameRepository
type GameRepositoryImpl = GameRepositoryImpl

// Item repository
type ItemRepository = ItemRepository
type ItemRepositoryImpl = ItemRepositoryImpl

// ItemInstance repository
type ItemInstanceRepository = ItemInstanceRepository
type ItemInstanceRepositoryImpl = ItemInstanceRepositoryImpl

// Inventory repository
type InventoryRepository = InventoryRepository
type InventoryRepositoryImpl = InventoryRepositoryImpl

// Player repository
type PlayerRepository = PlayerRepository
type PlayerRepositoryImpl = PlayerRepositoryImpl

// PlayerStats repository
type PlayerStatsRepository = PlayerStatsRepository
type PlayerStatsRepositoryImpl = PlayerStatsRepositoryImpl

// Session repository
type SessionRepository = SessionRepository
type SessionRepositoryImpl = SessionRepositoryImpl

// SessionUser repository
type SessionUserRepository = SessionUserRepository
type SessionUserRepositoryImpl = SessionUserRepositoryImpl

// User repository
type UserRepository = UserRepository
type UserRepositoryImpl = UserRepositoryImpl

// PlayerEffects repository
type PlayerEffectsRepository = PlayerEffectsRepository
type PlayerEffectsRepositoryImpl = PlayerEffectsRepositoryImpl
