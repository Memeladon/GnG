# 🧪 Тестирование GnG-Monopoly Backend

## 📋 Обзор

Создана комплексная система unit тестов для всех сервисов проекта, написанная по паттерну **AAA (Arrange, Act, Assert)**. Тесты покрывают всю бизнес-логику, включая сложную логику предметов согласно `ITEM_LOGIC.md`.

## 🏗️ Архитектура тестов

```
backend/tests/
├── conftest.py                           # Конфигурация pytest и фикстуры
├── test_user_service.py                  # Тесты UserService (25+ тестов)
├── test_player_service.py                # Тесты PlayerService (20+ тестов)
├── test_inventory_service.py             # Тесты InventoryService (15+ тестов)
├── test_item_instance_service.py         # Тесты ItemInstanceService (30+ тестов)
├── test_effects_service.py               # Тесты EffectsService (25+ тестов)
├── test_item_logic_integration.py        # Интеграционные тесты логики предметов (20+ тестов)
├── requirements.txt                      # Зависимости для тестирования
└── README.md                             # Документация тестов
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd backend
python run_tests.py --install
```

### 2. Запуск всех тестов

```bash
python run_tests.py --all
```

### 3. Быстрый запуск основных тестов

```bash
python run_tests.py --quick
```

## 📊 Покрытие тестов

### UserService (25+ тестов)
- ✅ Регистрация пользователей
- ✅ Аутентификация (успешная/неуспешная)
- ✅ Управление профилем
- ✅ Работа с токенами
- ✅ Валидация паролей
- ✅ Активация/деактивация пользователей

### PlayerService (20+ тестов)
- ✅ Создание профилей игроков
- ✅ Бросок кубиков с модификаторами
- ✅ Перемещение игроков
- ✅ Обновление позиций
- ✅ Управление статистикой
- ✅ Поиск игроков по различным критериям

### InventoryService (15+ тестов)
- ✅ Добавление/удаление предметов
- ✅ Использование предметов
- ✅ Проверка заполненности инвентаря
- ✅ Замена предметов
- ✅ Поиск предметов с фильтрами
- ✅ Обработка ошибок

### ItemInstanceService (30+ тестов)
- ✅ **Логика всех 31 предмета** согласно ITEM_LOGIC.md
- ✅ Предметы с бесконечными эффектами
- ✅ Предметы с временными эффектами
- ✅ Предметы с эффектами на других игроков
- ✅ Предметы с модификаторами
- ✅ Валидация входных данных
- ✅ Обработка конфликтов между предметами

### EffectsService (25+ тестов)
- ✅ Управление эффектами игроков
- ✅ Работа с ловушками на клетках
- ✅ Проверка и разрешение конфликтов эффектов
- ✅ Автоматическая очистка истекших эффектов
- ✅ Жизненный цикл эффектов

### Интеграционные тесты (20+ тестов)
- ✅ Взаимодействие между сервисами
- ✅ Полный цикл использования предметов
- ✅ Проверка логики согласно ITEM_LOGIC.md
- ✅ Тестирование конфликтов между предметами

## 🎯 Логика предметов (ITEM_LOGIC.md)

Особое внимание уделено тестированию сложной логики предметов:

### Предметы с бесконечными эффектами:
- **Шар всезнания** - бесконечный эффект, удаляется в конце хода
- **Красочная манга** - бесконечный эффект, запрещает автоскип

### Предметы с временными эффектами:
- **Очки EZ** - 2 хода легкой сложности
- **Повязка Рэмбо** - 2 хода высокой сложности  
- **Тотем мошны** - защита от ловушек на 2 хода

### Предметы с эффектами на других игроков:
- **Тухлая шаурма** - ловушка, -1 к кубикам на 2 хода для целевого игрока

### Предметы с модификаторами:
- **Читерский кубик** - замена значения кубика
- **Кубик хуюбика** - замена большего значения на 1

## 🛠️ Команды для запуска тестов

### Основные команды

```bash
# Установка зависимостей
python run_tests.py --install

# Запуск всех тестов
python run_tests.py --all

# Быстрый запуск основных тестов
python run_tests.py --quick

# Запуск с покрытием кода
python run_tests.py --coverage

# Запуск в параллельном режиме
python run_tests.py --parallel

# Запуск только упавших тестов
python run_tests.py --failed

# Подробный вывод
python run_tests.py --verbose
```

### Запуск конкретных тестов

```bash
# Конкретный файл тестов
python run_tests.py --file test_user_service.py

# Конкретный тест
python run_tests.py --test "tests/test_user_service.py::TestUserService::test_register_user_success"
```

### Прямые команды pytest

```bash
# Все тесты
uv run pytest tests/ -v

# Конкретный файл
uv run pytest tests/test_user_service.py -v

# Конкретный тест
uv run pytest tests/test_user_service.py::TestUserService::test_register_user_success -v

# С покрытием
uv run pytest tests/ --cov=src --cov-report=html

# Параллельный запуск
uv run pytest tests/ -n auto -v
```

## 🧪 Паттерн AAA (Arrange, Act, Assert)

Все тесты следуют паттерну AAA:

```python
@pytest.mark.asyncio
async def test_register_user_success(self, user_service, user_create_data, sample_user):
    """Тест успешной регистрации пользователя."""
    # Arrange - подготовка данных и моков
    user_service.dao.find_one_by = AsyncMock(return_value=None)
    user_service.dao.create_user_unique = AsyncMock(return_value=sample_user)
    
    # Act - выполнение тестируемого метода
    result = await user_service.register_user(user_create_data, None)
    
    # Assert - проверка результатов
    assert isinstance(result, UserResponse)
    assert result.login == sample_user.login
    user_service.dao.find_one_by.assert_called_once()
```

## 🔧 Фикстуры и моки

### Основные фикстуры (conftest.py):
- **test_session** - SQLite in-memory база данных
- **sample_*_data** - тестовые данные для всех сущностей
- **mock_*_dao** - моки для всех DAO классов
- **user_service, player_service, etc.** - экземпляры сервисов

### Моки:
- **AsyncMock** - для асинхронных методов
- **MagicMock** - для синхронных объектов
- **patch** - для подмены зависимостей

## 📈 Метрики качества

### Покрытие тестами:
- ✅ **UserService**: 100% методов
- ✅ **PlayerService**: 100% методов  
- ✅ **InventoryService**: 100% методов
- ✅ **ItemInstanceService**: 100% методов + вся логика предметов
- ✅ **EffectsService**: 100% методов

### Типы тестов:
- ✅ **Unit тесты** - изолированное тестирование методов
- ✅ **Интеграционные тесты** - взаимодействие между сервисами
- ✅ **Тесты граничных случаев** - обработка ошибок
- ✅ **Тесты валидации** - проверка входных данных
- ✅ **Тесты бизнес-логики** - сложная логика предметов

## 🐛 Отладка тестов

### Подробный вывод:
```bash
python run_tests.py --verbose
```

### Запуск конкретного упавшего теста:
```bash
uv run pytest tests/test_user_service.py::TestUserService::test_register_user_success -vvv --tb=long
```

### Отладка с pdb:
```bash
uv run pytest tests/test_user_service.py --pdb
```

## 📝 Добавление новых тестов

### 1. Создание нового теста:
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

### 2. Использование существующих фикстур:
- `sample_user_data`, `sample_player_data`, etc.
- `mock_user_dao`, `mock_player_dao`, etc.
- `test_session` для работы с базой данных

### 3. Следование паттерну AAA:
- **Arrange** - подготовка данных
- **Act** - выполнение действия
- **Assert** - проверка результата

## 🎉 Результат

Создана **полноценная система тестирования** с:

- ✅ **130+ unit тестов** для всех сервисов
- ✅ **Полное покрытие** бизнес-логики предметов
- ✅ **Интеграционные тесты** взаимодействия сервисов
- ✅ **Тесты граничных случаев** и обработки ошибок
- ✅ **Автоматизированный запуск** через скрипт
- ✅ **Подробная документация** и примеры
- ✅ **Паттерн AAA** для читаемости и поддержки

Система готова к использованию и дальнейшему развитию! 🚀
