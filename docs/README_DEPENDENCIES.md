# Управление зависимостями OneFlow.AI

Проект использует **pip-tools** для управления зависимостями с фиксацией версий.

## Структура файлов

```
requirements.in          # Исходные production зависимости
requirements.txt         # Зафиксированные production зависимости (генерируется автоматически)
requirements-dev.in      # Исходные dev зависимости
requirements-dev.txt     # Зафиксированные dev зависимости (генерируется автоматически)
```

## Быстрый старт

### 1. Установка зависимостей

**Production окружение:**
```bash
make install
# или
pip install -r requirements.txt
```

**Development окружение:**
```bash
make install-dev
# или
pip install -r requirements-dev.txt
```

### 2. Добавление новой зависимости

1. Добавьте зависимость в `requirements.in` (для production) или `requirements-dev.in` (для dev)
2. Перекомпилируйте:
   ```bash
   make compile-deps
   ```
3. Синхронизируйте окружение:
   ```bash
   make sync-dev  # для dev окружения
   # или
   make sync-deps  # для production окружения
   ```

### 3. Обновление зависимостей

**Обновить все до последних версий:**
```bash
make update-deps
```

**Обновить конкретную зависимость:**
```bash
pip-compile --upgrade-package requests requirements.in -o requirements.txt
```

## Команды Makefile

| Команда | Описание |
|---------|----------|
| `make install` | Установить production зависимости |
| `make install-dev` | Установить dev зависимости |
| `make compile-deps` | Скомпилировать .in файлы в .txt |
| `make update-deps` | Обновить все зависимости |
| `make sync-deps` | Синхронизировать production окружение |
| `make sync-dev` | Синхронизировать dev окружение |
| `make clean-deps` | Удалить скомпилированные файлы |

## Ручное использование pip-tools

**Установка pip-tools:**
```bash
pip install pip-tools
```

**Компиляция зависимостей:**
```bash
pip-compile requirements.in -o requirements.txt
pip-compile requirements-dev.in -o requirements-dev.txt
```

**Синхронизация окружения:**
```bash
pip-sync requirements-dev.txt  # установит только то, что в файле
```

**Обновление зависимостей:**
```bash
pip-compile --upgrade requirements.in -o requirements.txt
```

## Важные замечания

- ✅ **requirements.txt** и **requirements-dev.txt** генерируются автоматически - НЕ редактируйте их вручную
- ✅ Все изменения вносите в `.in` файлы
- ✅ Используйте `pip-sync` для точной синхронизации (удаляет лишние пакеты)
- ✅ `requirements-dev.in` содержит `-c requirements.txt` для совместимости версий
- ❌ Старые файлы `requirements_lock.txt` и `requirements/` удалены

## CI/CD Integration

**В GitHub Actions / GitLab CI:**
```yaml
- name: Install dependencies
  run: |
    pip install pip-tools
    pip-sync requirements.txt  # для production
    # или
    pip-sync requirements-dev.txt  # для тестов
```

## Troubleshooting

**Конфликты версий:**
```bash
pip-compile --resolver=backtracking requirements.in -o requirements.txt
```

**Очистка и переустановка:**
```bash
make clean-deps
make install-dev
```

**Проверка устаревших пакетов:**
```bash
pip list --outdated
```
