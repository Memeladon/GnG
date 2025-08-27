# Тесты для GnG-Monopoly Backend

## Обзор

Этот каталог содержит комплексные unit тесты для всех сервисов проекта, написанные по паттерну AAA (Arrange, Act, Assert).

## Структура тестов

```
tests/
├── conftest.py                    # Конфигурация pytest и фикстуры
├── test_user_service.py          # Тесты UserService
├── test_player_service.py        # Тесты PlayerService
├── test_inventory_service.py     # Тесты InventoryService
├── test_item_instance_service.py # Тесты ItemInstanceService (логика предметов)
├── test_effects_service.py       # Тесты EffectsService
├── requirements.txt              # Зависимости для тестирования
└── README.md                     # Этот файл
```

## Паттерн AAA (Arrange, Act, Assert)

Все тесты следуют паттерну AAA:

- **Arrange** - подготовка данных и моков
- **Act** - выполнение тестируемого метода
- **Assert** - проверка результатов

### Пример:

```python
@pytest.mark.asyncio
async def test_register_user_success(self, user_service, user_create_data, sample_user):
    """Тест успешной регистрации пользователя."""
    # Arrange
    user_service.dao.find_one_by = AsyncMock(return_value=None)
    user_service.dao.create_user_unique = AsyncMock(return_value=sample_user)
    
    # Act
    result = await user_service.register_user(user_create_data, None)
    
    # Assert
    assert isinstance(result, UserResponse)
    assert result.login == sample_user.login
    user_service.dao.find_one_by.assert_called_once()
```

## Запуск тестов

### Установка зависимостей

```bash
cd backend
uv add pytest pytest-asyncio pytest-mock aiosqlite
```

### Запуск всех тестов

```bash
uv run pytest tests/ -v
```

### Запуск конкретного файла тестов

```bash
uv run pytest tests/test_user_service.py -v
```

### Запуск конкретного теста

```bash
uv run pytest tests/test_user_service.py::TestUserService::test_register_user_success -v
```

### Запуск с покрытием кода

```bash
uv add pytest-cov
uv run pytest tests/ --cov=src --cov-report=html
```

## Фикстуры

### Основные фикстуры в conftest.py:

- **test_session** - тестовая сессия базы данных (SQLite in-memory)
- **sample_user_data** - тестовые данные пользователя
- **sample_player_data** - тестовые данные игрока
- **sample_item_data** - тестовые данные предмета
- **sample_item_instance_data** - тестовые данные экземпляра предмета
- **mock_*_dao** - моки для всех DAO классов

## Тестируемые сервисы

### 1. UserService
- Регистрация пользователей
- Аутентификация
- Управление профилем
- Работа с токенами

### 2. PlayerService
- Создание профилей игроков
- Бросок кубиков
- Перемещение игроков
- Управление статистикой

### 3. InventoryService
- Добавление/удаление предметов
- Использование предметов
- Проверка заполненности инвентаря
- Замена предметов

### 4. ItemInstanceService
- Логика использования конкретных предметов (31 предмет)
- Обработка эффектов предметов
- Проверка конфликтов между предметами
- Управление жизненным циклом предметов

### 5. EffectsService
- Управление эффектами игроков
- Работа с ловушками на клетках
- Проверка и разрешение конфликтов эффектов
- Автоматическая очистка истекших эффектов

## Логика предметов

Особое внимание уделено тестированию логики предметов согласно `ITEM_LOGIC.md`:

### Предметы с бесконечными эффектами:
- Шар всезнания
- Красочная манга

### Предметы с временными эффектами:
- Очки EZ (2 хода легкой сложности)
- Повязка Рэмбо (2 хода высокой сложности)
- Тотем мошны (защита от ловушек)

### Предметы с эффектами на других игроков:
- Тухлая шаурма (ловушка)

### Предметы с модификаторами:
- Читерский кубик
- Кубик хуюбика

## Моки и изоляция

Все тесты используют моки для изоляции:
- **AsyncMock** для асинхронных методов
- **MagicMock** для синхронных объектов
- **patch** для подмены зависимостей

## База данных для тестов

Используется SQLite in-memory база данных:
- Быстрая работа
- Изоляция тестов
- Автоматическая очистка после каждого теста

## Покрытие тестов

Тесты покрывают:
- ✅ Успешные сценарии
- ✅ Обработку ошибок
- ✅ Граничные случаи
- ✅ Валидацию входных данных
- ✅ Бизнес-логику предметов
- ✅ Взаимодействие между сервисами

## Добавление новых тестов

При добавлении новых тестов следуйте:

1. **Паттерну AAA**
2. **Используйте существующие фикстуры**
3. **Мокайте внешние зависимости**
4. **Тестируйте как успешные, так и неуспешные сценарии**
5. **Добавляйте документацию к тестам**

### Пример нового теста:

```python
@pytest.mark.asyncio
async def test_new_feature_success(self, service_fixture, sample_data):
    """Тест новой функциональности."""
    # Arrange
    service_fixture.dao.method = AsyncMock(return_value=expected_result)
    
    # Act
    result = await service_fixture.new_method(sample_data, None)
    
    # Assert
    assert result.success is True
    assert result.data == expected_result
    service_fixture.dao.method.assert_called_once()
```
