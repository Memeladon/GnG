package models

// UserRights представляет роль пользователя в системе
type UserRights string

const (
	UserRightsUndefined UserRights = "Неопределен"
	UserRightsAdmin     UserRights = "Администратор"
	UserRightsModerator UserRights = "Модерация"
	UserRightsPlayer    UserRights = "Участник"
)

// ItemType представляет тип предмета
type ItemType string

const (
	ItemTypeBuff    ItemType = "Бафф"
	ItemTypeDebuff  ItemType = "Дебафф"
	ItemTypeTrap    ItemType = "Ловушка"
	ItemTypeNeutral ItemType = "Нейтралка"
)

// GameStatus представляет статус игры
type GameStatus string

const (
	GameStatusProgress  GameStatus = "Играется"
	GameStatusDrop      GameStatus = "Дроп"
	GameStatusRerolled  GameStatus = "Реролл"
	GameStatusCompleted GameStatus = "Пройдена"
)

// CellType представляет тип клетки на игровом поле
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

// GameConditions представляет игровые условия
type GameConditions string

const (
	GameConditionsMain  GameConditions = "Основное"
	GameConditionsGenre GameConditions = "Жанровое"
)

// DiceModifier представляет тип модификатора кубика
type DiceModifier string

const (
	DiceModifierCheat  DiceModifier = "Читерский кубик"
	DiceModifierHuybic DiceModifier = "Кубик хуюбика"
)

// GameModifier представляет тип игрового модификатора
type GameModifier string

const (
	GameModifierEZ    GameModifier = "Очки EZ"
	GameModifierRambo GameModifier = "Повязка Рэмбо"
)

// EffectType представляет тип эффекта предмета
type EffectType string

const (
	EffectTypePassive EffectType = "Пассивный"
	EffectTypeActive  EffectType = "Активный"
	EffectTypeTarget  EffectType = "Целевой"
	EffectTypeInstant EffectType = "Мгновенный"
	EffectTypeTrap    EffectType = "Ловушка"
)

// EffectCategory представляет категорию эффекта
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
