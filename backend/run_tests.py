#!/usr/bin/env python3
"""
Скрипт для запуска тестов GnG-Monopoly Backend
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Запуск команды с выводом описания."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Выполняется команда: {command}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"\n✅ {description} - УСПЕШНО")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - ОШИБКА (код: {e.returncode})")
        return False


def install_dependencies():
    """Установка зависимостей для тестирования."""
    commands = [
        ("uv add pytest pytest-asyncio pytest-mock aiosqlite", "Установка pytest и зависимостей"),
        ("uv add pytest-cov", "Установка pytest-cov для покрытия кода"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True


def run_all_tests():
    """Запуск всех тестов."""
    return run_command("uv run pytest tests/ -v", "Запуск всех тестов")


def run_specific_test_file(test_file):
    """Запуск конкретного файла тестов."""
    return run_command(f"uv run pytest tests/{test_file} -v", f"Запуск тестов из {test_file}")


def run_specific_test(test_path):
    """Запуск конкретного теста."""
    return run_command(f"uv run pytest {test_path} -v", f"Запуск теста {test_path}")


def run_tests_with_coverage():
    """Запуск тестов с покрытием кода."""
    return run_command(
        "uv run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing",
        "Запуск тестов с покрытием кода"
    )


def run_tests_with_parallel():
    """Запуск тестов в параллельном режиме."""
    return run_command(
        "uv run pytest tests/ -n auto -v",
        "Запуск тестов в параллельном режиме"
    )


def run_failed_tests():
    """Запуск только упавших тестов."""
    return run_command(
        "uv run pytest tests/ --lf -v",
        "Запуск только упавших тестов"
    )


def run_tests_with_verbose():
    """Запуск тестов с подробным выводом."""
    return run_command(
        "uv run pytest tests/ -vvv --tb=long",
        "Запуск тестов с подробным выводом"
    )


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Скрипт для запуска тестов GnG-Monopoly Backend")
    parser.add_argument(
        "--install", 
        action="store_true", 
        help="Установить зависимости для тестирования"
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Запустить все тесты"
    )
    parser.add_argument(
        "--file", 
        type=str, 
        help="Запустить тесты из конкретного файла (например: test_user_service.py)"
    )
    parser.add_argument(
        "--test", 
        type=str, 
        help="Запустить конкретный тест (например: tests/test_user_service.py::TestUserService::test_register_user_success)"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Запустить тесты с покрытием кода"
    )
    parser.add_argument(
        "--parallel", 
        action="store_true", 
        help="Запустить тесты в параллельном режиме"
    )
    parser.add_argument(
        "--failed", 
        action="store_true", 
        help="Запустить только упавшие тесты"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Запустить тесты с подробным выводом"
    )
    parser.add_argument(
        "--quick", 
        action="store_true", 
        help="Быстрый запуск основных тестов"
    )

    args = parser.parse_args()

    # Проверяем, что мы в правильной директории
    if not Path("tests").exists():
        print("❌ Ошибка: Директория tests не найдена. Убедитесь, что вы находитесь в backend/")
        sys.exit(1)

    success = True

    # Установка зависимостей
    if args.install:
        success = install_dependencies() and success

    # Запуск тестов
    if args.all:
        success = run_all_tests() and success
    elif args.file:
        success = run_specific_test_file(args.file) and success
    elif args.test:
        success = run_specific_test(args.test) and success
    elif args.coverage:
        success = run_tests_with_coverage() and success
    elif args.parallel:
        success = run_tests_with_parallel() and success
    elif args.failed:
        success = run_failed_tests() and success
    elif args.verbose:
        success = run_tests_with_verbose() and success
    elif args.quick:
        # Быстрый запуск основных тестов
        print("🚀 Быстрый запуск основных тестов...")
        success = run_command("uv run pytest tests/test_user_service.py tests/test_player_service.py -v", "Быстрый запуск") and success
    else:
        # По умолчанию запускаем все тесты
        success = run_all_tests() and success

    # Итоговый результат
    print(f"\n{'='*60}")
    if success:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Система готова к работе")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ")
        print("🔧 Проверьте логи выше для исправления ошибок")
    print(f"{'='*60}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
