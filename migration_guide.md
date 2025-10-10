# Руководство по миграции на современное пакетирование

## 🎯 Цели миграции

1. **Декларативная конфигурация** — вся метаинформация в `pyproject.toml`
2. **Разделение зависимостей** — опциональные extras для гибкой установки
3. **Воспроизводимость** — lock-файлы для фиксации точных версий
4. **Современные инструменты** — соответствие PEP 621, PEP 517, PEP 518

---

## 📋 Текущая структура (устаревшая)

```
oneflow-ai/
├── setup.py                    # ❌ Старый способ
├── requirements.txt            # ❌ Монолитный файл
└── src/
    └── ...
```

### Проблемы текущего подхода:

- **setup.py** — императивная конфигурация, сложнее поддерживать
- **requirements.txt** — все зависимости в одном файле, нет разделения
- **Нет версионирования** — непонятно, какие версии точно используются
- **Нет extras** — невозможно установить только нужные компоненты

---

## ✨ Новая структура (современная)

```
oneflow-ai/
├── pyproject.toml              # ✅ Единая конфигурация
├── requirements-lock.txt       # ✅ Фиксированные версии (prod)
├── requirements-dev-lock.txt   # ✅ Фиксированные версии (dev)
├── .python-version             # ✅ Версия Python для pyenv/asdf
└── src/
    └── ...
```

---

## 🔧 Шаги миграции

### Шаг 1: Создать pyproject.toml

```bash
# Удалить старые файлы после тестирования
# rm setup.py
# rm requirements.txt
```

Создайте `pyproject.toml` на основе артефакта выше.

### Шаг 2: Установить pip-tools для lock-файлов

```bash
pip install pip-tools
```

### Шаг 3: Сгенерировать lock-файлы

```bash
# Production зависимости (core + api + web + db + auth)
pip-compile \
  --extra=prod \
  --output-file=requirements-lock.txt \
  pyproject.toml

# Development зависимости (все + dev инструменты)
pip-compile \
  --extra=all \
  --extra=dev \
  --output-file=requirements-dev-lock.txt \
  pyproject.toml
```

### Шаг 4: Обновить CI/CD и документацию

#### GitHub Actions пример:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install pip-tools
        run: pip install pip-tools
      
      - name: Install dependencies
        run: pip-sync requirements-dev-lock.txt
      
      - name: Run tests
        run: pytest
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

#### Dockerfile обновление:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка pip-tools
RUN pip install --no-cache-dir pip-tools

# Копирование lock-файла
COPY requirements-lock.txt .

# Синхронизация зависимостей
RUN pip-sync requirements-lock.txt

# Копирование кода
COPY . .

# Установка пакета
RUN pip install --no-deps -e .

CMD ["oneflow-server"]
```

---

## 📖 Новые способы установки

### Для пользователей:

```bash
# Базовая установка (минимум зависимостей)
pip install oneflow-ai

# С API провайдерами
pip install oneflow-ai[api]

# С веб-сервером
pip install oneflow-ai[web]

# Полная production установка
pip install oneflow-ai[prod]

# Абсолютно всё (включая dev-инструменты)
pip install oneflow-ai[all,dev]
```

### Для разработчиков:

```bash
# Клонировать репозиторий
git clone https://github.com/voroninsergei/oneflow-ai.git
cd oneflow-ai

# Установить pip-tools
pip install pip-tools

# Синхронизировать dev окружение
pip-sync requirements-dev-lock.txt

# Установить пакет в editable режиме
pip install -e .

# Установить pre-commit хуки
pre-commit install
```

---

## 🔄 Обновление зависимостей

### Добавление новой зависимости:

```bash
# 1. Добавить в pyproject.toml в нужную секцию
# [project.dependencies] или [project.optional-dependencies]

# 2. Перегенерировать lock-файлы
pip-compile --extra=prod -o requirements-lock.txt pyproject.toml
pip-compile --extra=all --extra=dev -o requirements-dev-lock.txt pyproject.toml

# 3. Применить изменения
pip-sync requirements-dev-lock.txt
```

### Обновление версий зависимостей:

```bash
# Обновить все до последних совместимых версий
pip-compile --upgrade --extra=prod -o requirements-lock.txt pyproject.toml

# Обновить конкретную зависимость
pip-compile --upgrade-package=fastapi --extra=prod -o requirements-lock.txt pyproject.toml
```

---

## 🎨 Дополнительные улучшения

### 1. Pre-commit хуки

Создайте `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

### 2. Renovate Bot для автообновлений

Создайте `renovate.json`:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:base"],
  "schedule": ["before 6am on monday"],
  "packageRules": [
    {
      "matchPackagePatterns": ["*"],
      "matchUpdateTypes": ["minor", "patch"],
      "groupName": "all non-major dependencies",
      "groupSlug": "all-minor-patch"
    }
  ]
}
```

### 3. Makefile для удобства

Создайте `Makefile`:

```makefile
.PHONY: install dev-install update-deps test lint format clean

install:
	pip install -e .

dev-install:
	pip install pip-tools
	pip-sync requirements-dev-lock.txt
	pip install -e .
	pre-commit install

update-deps:
	pip-compile --extra=prod -o requirements-lock.txt pyproject.toml
	pip-compile --extra=all --extra=dev -o requirements-dev-lock.txt pyproject.toml

test:
	pytest

lint:
	ruff check src tests
	mypy src

format:
	black src tests
	ruff check --fix src tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov dist build *.egg-info
```

---

## ✅ Чек-лист миграции

- [ ] Создан `pyproject.toml` с правильной структурой
- [ ] Зависимости разделены на extras (api, web, db, auth, dev)
- [ ] Сгенерированы lock-файлы (`requirements-lock.txt`, `requirements-dev-lock.txt`)
- [ ] Настроены инструменты линтинга (black, ruff, mypy)
- [ ] Настроен pytest с покрытием кода
- [ ] Обновлена документация (README.md, CONTRIBUTING.md)
- [ ] Обновлены CI/CD пайплайны
- [ ] Обновлен Dockerfile (если есть)
- [ ] Настроен pre-commit
- [ ] Удалены `setup.py` и `requirements.txt` (после тестирования)
- [ ] Добавлен `.python-version` файл

---

## 📚 Преимущества нового подхода

### 1. **Гибкость установки**
```bash
# Только для API работы
pip install oneflow-ai[api]

# Для локальной разработки
pip install oneflow-ai[all,dev]
```

### 2. **Воспроизводимость**
```bash
# Точно те же версии на всех машинах
pip-sync requirements-lock.txt
```

### 3. **Простота обновления**
```bash
# Обновить все зависимости
pip-compile --upgrade pyproject.toml
```

### 4. **Соответствие стандартам**
- PEP 621 — декларативная конфигурация
- PEP 517/518 — современная сборка
- Совместимость с Poetry, PDM, Hatch

### 5. **Лучший Developer Experience**
- Один файл конфигурации
- Понятная структура зависимостей
- Быстрая установка нужных компонентов

---

## 🔗 Полезные ссылки

- [PEP 621](https://peps.python.org/pep-0621/) — Storing project metadata in pyproject.toml
- [pip-tools документация](https://pip-tools.readthedocs.io/)
- [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [pyproject.toml примеры](https://github.com/pypa/sampleproject)

---

## 💡 Дополнительные рекомендации

### Альтернативные инструменты:

Если `pip-tools` не подходит, рассмотрите:

1. **Poetry** — полноценный менеджер зависимостей
   ```bash
   poetry init
   poetry add fastapi
   poetry install
   ```

2. **PDM** — современный менеджер, использующий PEP 582
   ```bash
   pdm init
   pdm add fastapi
   pdm install
   ```

3. **Hatch** — универсальный инструмент для управления проектами
   ```bash
   hatch new oneflow-ai
   hatch env create
   ```

Все три инструмента автоматически работают с `pyproject.toml` и создают lock-файлы.

---

## 🎉 Итого

После миграции вы получите:
- ✅ Современную структуру пакета
- ✅ Гибкую установку зависимостей
- ✅ Воспроизводимое окружение
- ✅ Простое управление версиями
- ✅ Соответствие Python стандартам
- ✅ Лучший опыт разработки