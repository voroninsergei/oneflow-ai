#!/bin/bash
set -e

echo "Starting deployment..."

# Очистка логов перед развёртыванием
echo "Cleaning up logs..."
bash scripts/cleanup-logs.sh

# Остановка контейнеров
echo "Stopping containers..."
docker compose down

# Обновление образов
echo "Pulling latest images..."
docker compose pull

# Запуск контейнеров
echo "Starting containers..."
docker compose up -d

# Проверка статуса
echo "Checking container status..."
docker compose ps

echo "Deployment completed successfully"
