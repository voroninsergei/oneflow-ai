#!/bin/bash
set -e

LOG_DIR="logs"
RETENTION_DAYS=7

echo "Starting logs cleanup..."

# Создаём директорию если её нет
mkdir -p "$LOG_DIR"

# Удаляем старые логи
if [ -d "$LOG_DIR" ]; then
    find "$LOG_DIR" -name "*.log" -type f -mtime +$RETENTION_DAYS -delete
    find "$LOG_DIR" -name "*.log.gz" -type f -mtime +$RETENTION_DAYS -delete
    echo "Removed logs older than $RETENTION_DAYS days"
fi

# Очищаем текущие логи (опционально, раскомментируйте если нужно)
# echo "Clearing current logs..."
# > "$LOG_DIR/oneflow.log"

echo "Logs cleanup completed successfully"
