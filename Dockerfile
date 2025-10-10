# Multi-stage build для оптимизации размера образа
FROM python:3.11-slim as builder

WORKDIR /app

# Установка зависимостей сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt

# Production stage
FROM python:3.11-slim

# Метаданные
LABEL maintainer="voroninsergeiai@gmail.com"
LABEL version="2.0"
LABEL description="OneFlow.AI - Production Ready"

# Создание non-root пользователя
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

WORKDIR /app

# Копирование установленных зависимостей из builder
COPY --from=builder /root/.local /home/appuser/.local

# Копирование исходного кода с правильными правами
COPY --chown=appuser:appuser . .

# Переключение на non-root пользователя
USER appuser

# Обновление PATH для использования локальных пакетов
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Healthcheck для Docker
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Expose порта
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "web_server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
