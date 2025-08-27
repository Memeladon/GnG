import enum

class UserRights(str, enum.Enum):
    UNDEFINED = "Неопределен"
    ADMIN = "Администратор"
    MODERATOR = "Модерация"
    PLAYER = "Участник"

class ItemType(str, enum.Enum):
    BUFF = "Бафф"
    DEBUFF = "Дебафф"
    TRAP = "Ловушка"
    NEUTRAL = "Нейтралка"

class GameStatus(str, enum.Enum):
    PROGRESS = "Играется"
    DROP = "Дроп"
    REROLLED = "Реролл"
    COMPLETED = "Пройдена"

class CellType(str, enum.Enum):
    START = "Старт"
    JAIL = "Тюрьма"
    AUCTION = "Аукошная"
    LOTTERY = "Лотерея"
    GAME = "Игровая"
    TRAP = "Подлянка"
    QUESTION = "Вопрос"

class GameConditions(str, enum.Enum):
    MAIN = "Основное"
    GENRE = "Жанровое"

class DiceModifier(str, enum.Enum):
    CHEAT = "Читерский кубик"
    HUYBIC = "Кубик хуюбика"

class GameModifier(str, enum.Enum):
    EZ = "Очки EZ"
    RAMBO = "Повязка Рэмбо"

class EffectType(str, enum.Enum):
    """Типы эффектов предметов"""
    PASSIVE = "Пассивный"  # Работает пока в инвентаре
    ACTIVE = "Активный"    # Используется игроком
    TARGET = "Целевой"     # Используется на других игроков
    INSTANT = "Мгновенный" # Применяется сразу при выпадении
    TRAP = "Ловушка"       # Оставляет след на клетке

class EffectCategory(str, enum.Enum):
    """Категории эффектов"""
    DICE_MODIFIER = "Модификатор кубиков"
    GAME_DIFFICULTY = "Сложность игры"
    MOVEMENT = "Передвижение"
    TIME_MODIFIER = "Модификатор времени"
    POINTS_MODIFIER = "Модификатор очков"
    INVENTORY_MODIFIER = "Модификатор инвентаря"
    PROTECTION = "Защита"
    TRAP = "Ловушка"
    SPECIAL = "Специальный"
