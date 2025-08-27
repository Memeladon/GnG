-- +goose Up
-- +goose StatementBegin

-- Create UserRights enum
CREATE TYPE user_rights AS ENUM (
    'Неопределен',
    'Администратор',
    'Модерация',
    'Участник'
);

-- Create ItemType enum
CREATE TYPE item_type AS ENUM (
    'Бафф',
    'Дебафф',
    'Ловушка',
    'Нейтралка'
);

-- Create GameStatus enum
CREATE TYPE game_status AS ENUM (
    'Играется',
    'Дроп',
    'Реролл',
    'Пройдена'
);

-- Create CellType enum
CREATE TYPE cell_type AS ENUM (
    'Старт',
    'Тюрьма',
    'Аукошная',
    'Лотерея',
    'Игровая',
    'Подлянка',
    'Вопрос'
);

-- Create GameConditions enum
CREATE TYPE game_conditions AS ENUM (
    'Основное',
    'Жанровое'
);

-- Create DiceModifier enum
CREATE TYPE dice_modifier AS ENUM (
    'Читерский кубик',
    'Кубик хуюбика'
);

-- Create GameModifier enum
CREATE TYPE game_modifier AS ENUM (
    'Очки EZ',
    'Повязка Рэмбо'
);

-- Create EffectType enum
CREATE TYPE effect_type AS ENUM (
    'Пассивный',
    'Активный',
    'Целевой',
    'Мгновенный',
    'Ловушка'
);

-- Create EffectCategory enum
CREATE TYPE effect_category AS ENUM (
    'Модификатор кубиков',
    'Сложность игры',
    'Передвижение',
    'Модификатор времени',
    'Модификатор очков',
    'Модификатор инвентаря',
    'Защита',
    'Ловушка',
    'Специальный'
);

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TYPE IF EXISTS effect_category;
DROP TYPE IF EXISTS effect_type;
DROP TYPE IF EXISTS game_modifier;
DROP TYPE IF EXISTS dice_modifier;
DROP TYPE IF EXISTS game_conditions;
DROP TYPE IF EXISTS cell_type;
DROP TYPE IF EXISTS game_status;
DROP TYPE IF EXISTS item_type;
DROP TYPE IF EXISTS user_rights;
-- +goose StatementEnd
