package models

// UserRights represents user role in the system
type UserRights string

const (
	UserRightsUndefined UserRights = "Неопределен"
	UserRightsAdmin     UserRights = "Администратор"
	UserRightsModerator UserRights = "Модерация"
	UserRightsPlayer    UserRights = "Участник"
)

// ItemType represents type of item
type ItemType string

const (
	ItemTypeBuff    ItemType = "Бафф"
	ItemTypeDebuff  ItemType = "Дебафф"
	ItemTypeTrap    ItemType = "Ловушка"
	ItemTypeNeutral ItemType = "Нейтралка"
)

// GameStatus represents game status
type GameStatus string

const (
	GameStatusProgress  GameStatus = "Играется"
	GameStatusDrop      GameStatus = "Дроп"
	GameStatusRerolled  GameStatus = "Реролл"
	GameStatusCompleted GameStatus = "Пройдена"
)

// CellType represents type of cell on game board
type CellType string

const (
	CellTypeStart    CellType = "Старт"
	CellTypeJail     CellType = "Тюрьма"
	CellTypeAuction  CellType = "Аукошная"
	CellTypeLottery  CellType = "Лотерея"
	CellTypeGame     CellType = "Игровая"
	CellTypeTrap     CellType = "Подлянка"
	CellTypeQuestion CellType = "Вопрос"
)

// GameConditions represents game conditions
type GameConditions string

const (
	GameConditionsMain  GameConditions = "Основное"
	GameConditionsGenre GameConditions = "Жанровое"
)

// DiceModifier represents dice modifier type
type DiceModifier string

const (
	DiceModifierCheat  DiceModifier = "Читерский кубик"
	DiceModifierHuybic DiceModifier = "Кубик хуюбика"
)

// GameModifier represents game modifier type
type GameModifier string

const (
	GameModifierEZ    GameModifier = "Очки EZ"
	GameModifierRambo GameModifier = "Повязка Рэмбо"
)

// EffectType represents type of item effect
type EffectType string

const (
	EffectTypePassive EffectType = "Пассивный"  // Работает пока в инвентаре
	EffectTypeActive  EffectType = "Активный"   // Используется игроком
	EffectTypeTarget  EffectType = "Целевой"    // Используется на других игроков
	EffectTypeInstant EffectType = "Мгновенный" // Применяется сразу при выпадении
	EffectTypeTrap    EffectType = "Ловушка"    // Оставляет след на клетке
)

// EffectCategory represents category of effect
type EffectCategory string

const (
	EffectCategoryDiceModifier      EffectCategory = "Модификатор кубиков"
	EffectCategoryGameDifficulty    EffectCategory = "Сложность игры"
	EffectCategoryMovement          EffectCategory = "Передвижение"
	EffectCategoryTimeModifier      EffectCategory = "Модификатор времени"
	EffectCategoryPointsModifier    EffectCategory = "Модификатор очков"
	EffectCategoryInventoryModifier EffectCategory = "Модификатор инвентаря"
	EffectCategoryProtection        EffectCategory = "Защита"
	EffectCategoryTrap              EffectCategory = "Ловушка"
	EffectCategorySpecial           EffectCategory = "Специальный"
)
