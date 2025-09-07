# Repository Layer

### BaseRepository
`BaseRepository` - это базовый интерфейс, который определяет все основные CRUD операции:
- `CreateOne` - создание одной записи
- `CreateMany` - создание нескольких записей
- `GetOne` - получение записи по ID
- `GetAll` - получение всех записей
- `UpdateOne` - обновление записи по ID
- `UpdateBy` - обновление записей по фильтрам
- `DeleteOne` - удаление записи по ID
- `DeleteBy` - удаление записей по фильтрам
- `DeleteAll` - удаление всех записей
- `FindBy` - поиск записей по фильтрам
- `FindOneBy` - поиск одной записи по фильтрам
- `GetPaginated` - получение записей с пагинацией
- `Count` - подсчет записей
- `Exists` - проверка существования записи по ID
- `ExistsBy` - проверка существования записи по фильтрам

### BaseRepositoryImpl
`BaseRepositoryImpl` предоставляет базовую реализацию всех методов `BaseRepository`. Он использует reflection для работы с различными типами моделей.

### CellRepository
Расширяет `BaseRepository` методами для работы с клетками игрового поля:
- `AddTrapToCell` - добавление ловушки в клетку
- `RemoveTrapFromCell` - удаление ловушки из клетки
- `GetCellTraps` - получение списка ловушек клетки

### ItemInstanceRepository
Расширяет `BaseRepository` методами для работы с экземплярами предметов:
- `UseItem` - использование предмета (отметка как использованного)

### InventoryRepository
Расширяет `BaseRepository` методами для работы с инвентарем:
- `IsInventoryFull` - проверка заполненности инвентаря
- `AddItemToInventory` - добавление предмета в инвентарь
- `ReplaceItemInInventory` - замена предмета в инвентаре
- `SearchItemsInInventory` - поиск предметов в инвентаре

### PlayerRepository
Расширяет `BaseRepository` методами для работы с игроками:
- `CreatePlayerFirstTime` - создание первого игрока для пользователя
- `UpdatePlayerProfile` - обновление профиля игрока
- `GetPlayersBySessionID` - получение игроков по ID сессии

### PlayerStatsRepository
Расширяет `BaseRepository` методами для работы со статистикой игроков:
- `IncrementStats` - увеличение значений статистики

### SessionRepository
Расширяет `BaseRepository` методами для работы с игровыми сессиями:
- `CloseSession` - закрытие сессии
- `IsSessionExpired` - проверка истечения сессии
- `GetSessionsByUserID` - получение сессий пользователя

### SessionUserRepository
Расширяет `BaseRepository` методами для работы со связями пользователей и сессий:
- `AddUserToSession` - добавление пользователя в сессию
- `GetSessionUsersWithUserData` - получение пользователей сессии с данными

### UserRepository
Расширяет `BaseRepository` методами для работы с пользователями:
- `CreateUserUnique` - создание пользователя с проверкой уникальности логина

### GameRepository, ItemRepository, PlayerEffectsRepository
Базовые репозитории без дополнительных методов.

## Использование

### Создание репозитория
```go
// Создание базового репозитория
cellRepo := repositories.NewCellRepository(db)

// Создание репозитория с зависимостями
itemInstanceRepo := repositories.NewItemInstanceRepository(db)
inventoryRepo := repositories.NewInventoryRepository(db, itemInstanceRepo)
```

```go
// Создание клетки
cellData := &models.CellCreate{
    Position: 1,
    CellType: models.CellTypeStart,
    Title: "Start",
}
cell, err := cellRepo.CreateOne(ctx, cellData)

// Добавление ловушки
trapData := map[string]interface{}{
    "type": "jail",
    "duration": 3,
}
updatedCell, err := cellRepo.AddTrapToCell(ctx, cell.ID, trapData)

// Поиск клеток
cells, err := cellRepo.FindBy(ctx, map[string]interface{}{
    "cell_type": models.CellTypeTrap,
})
```

## TODO

- Реализовать сложные JOIN запросы для методов, требующих связей между таблицами
- Добавить кэширование для часто используемых запросов
- Реализовать пул соединений для оптимизации производительности
