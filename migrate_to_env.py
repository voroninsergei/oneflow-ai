#!/usr/bin/env python3
"""
Скрипт миграции API ключей с .api_keys.json на переменные окружения
Поддерживает экспорт в различные форматы для разных окружений
"""

import json
import os
import sys
import argparse
import secrets
from pathlib import Path
from typing import Dict, Optional


class SecretMigrator:
    """Класс для миграции секретов из JSON в различные форматы"""
    
    def __init__(self, source_file: str = '.api_keys.json'):
        self.source_file = Path(source_file)
        self.secrets: Dict[str, str] = {}
    
    def load_old_format(self) -> bool:
        """Загрузка ключей из старого .api_keys.json файла"""
        if not self.source_file.exists():
            print(f"❌ Файл {self.source_file} не найден")
            return False
        
        try:
            with open(self.source_file, 'r') as f:
                data = json.load(f)
            
            # Нормализация ключей
            self.secrets = {
                'openai_api_key': data.get('openai', ''),
                'anthropic_api_key': data.get('anthropic', ''),
                'stability_api_key': data.get('stability', ''),
                'elevenlabs_api_key': data.get('elevenlabs', ''),
            }
            
            print(f"✓ Загружено {len([k for k, v in self.secrets.items() if v])} ключей из {self.source_file}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ Ошибка чтения файла: {e}")
            return False
    
    def export_to_env_file(self, output_file: str = '.env') -> bool:
        """Экспорт в .env файл"""
        try:
            output_path = Path(output_file)
            
            # Проверка существования
            if output_path.exists():
                response = input(f"⚠️  Файл {output_file} уже существует. Перезаписать? (y/N): ")
                if response.lower() != 'y':
                    print("❌ Отменено пользователем")
                    return False
            
            # Генерация JWT secret
            jwt_secret = secrets.token_urlsafe(32)
            
            with open(output_path, 'w') as f:
                f.write("# ============================================\n")
                f.write("# OneFlow.AI - Environment Variables\n")
                f.write("# Автоматически сгенерировано migrate_to_env.py\n")
                f.write("# ============================================\n\n")
                
                f.write("# API Keys\n")
                for key, value in self.secrets.items():
                    f.write(f"{key.upper()}={value}\n")
                
                f.write("\n# Security\n")
                f.write(f"JWT_SECRET_KEY={jwt_secret}\n")
                f.write("JWT_ALGORITHM=HS256\n")
                f.write("ACCESS_TOKEN_EXPIRE_MINUTES=30\n")
                
                f.write("\n# Server\n")
                f.write("HOST=0.0.0.0\n")
                f.write("PORT=8000\n")
                f.write("DEBUG=False\n")
                f.write("LOG_LEVEL=INFO\n")
                
                f.write("\n# Database\n")
                f.write("DATABASE_URL=sqlite:///oneflow.db\n")
            
            # Установка прав доступа (только владелец)
            output_path.chmod(0o600)
            
            print(f"✓ Создан {output_file}")
            print(f"✓ JWT secret сгенерирован")
            print(f"✓ Установлены права 600 (только владелец)")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания .env: {e}")
            return False
    
    def export_to_bash(self, output_file: str = 'export_secrets.sh') -> bool:
        """Экспорт в bash скрипт"""
        try:
            with open(output_file, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write("# OneFlow.AI - Export secrets to environment\n")
                f.write("# Usage: source export_secrets.sh\n\n")
                
                for key, value in self.secrets.items():
                    if value:
                        f.write(f"export {key.upper()}='{value}'\n")
                
                f.write(f"\necho '✓ OneFlow.AI secrets exported to environment'\n")
            
            Path(output_file).chmod(0o700)
            print(f"✓ Создан {output_file}")
            print(f"  Использование: source {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания bash скрипта: {e}")
            return False
    
    def export_to_docker_compose(self, output_file: str = 'secrets.env') -> bool:
        """Экспорт для Docker Compose"""
        try:
            with open(output_file, 'w') as f:
                f.write("# OneFlow.AI - Docker Compose Secrets\n")
                for key, value in self.secrets.items():
                    if value:
                        f.write(f"{key.upper()}={value}\n")
            
            Path(output_file).chmod(0o600)
            print(f"✓ Создан {output_file}")
            print(f"  Добавьте в docker-compose.yml:")
            print(f"    env_file:")
            print(f"      - {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания Docker Compose файла: {e}")
            return False
    
    def export_to_kubernetes(self, output_file: str = 'k8s-secrets.yaml') -> bool:
        """Экспорт в Kubernetes Secret YAML"""
        try:
            import base64
            
            with open(output_file, 'w') as f:
                f.write("apiVersion: v1\n")
                f.write("kind: Secret\n")
                f.write("metadata:\n")
                f.write("  name: oneflow-api-keys\n")
                f.write("  namespace: oneflow\n")
                f.write("type: Opaque\n")
                f.write("data:\n")
                
                for key, value in self.secrets.items():
                    if value:
                        # Kubernetes требует base64
                        encoded = base64.b64encode(value.encode()).decode()
                        # Преобразование формата ключа
                        k8s_key = key.replace('_', '-')
                        f.write(f"  {k8s_key}: {encoded}\n")
            
            print(f"✓ Создан {output_file}")
            print(f"  Применить: kubectl apply -f {output_file}")
            print(f"  ⚠️  ВАЖНО: Удалите этот файл после применения!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания Kubernetes Secret: {e}")
            return False
    
    def export_to_aws_cli(self, output_file: str = 'aws_create_secret.sh') -> bool:
        """Экспорт AWS CLI команд для Secrets Manager"""
        try:
            with open(output_file, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write("# OneFlow.AI - Create AWS Secrets Manager secrets\n\n")
                
                f.write("SECRET_NAME='oneflow-ai/api-keys'\n")
                f.write("REGION='us-east-1'\n\n")
                
                # Создание JSON для секрета
                secret_json = json.dumps(self.secrets, indent=2)
                
                f.write("# Create secret\n")
                f.write(f"aws secretsmanager create-secret \\\n")
                f.write(f"  --name \"$SECRET_NAME\" \\\n")
                f.write(f"  --description 'OneFlow.AI API Keys' \\\n")
                f.write(f"  --region \"$REGION\" \\\n")
                f.write(f"  --secret-string '{secret_json}'\n\n")
                
                f.write("# Or update existing secret\n")
                f.write(f"# aws secretsmanager update-secret \\\n")
                f.write(f"#   --secret-id \"$SECRET_NAME\" \\\n")
                f.write(f"#   --region \"$REGION\" \\\n")
                f.write(f"#   --secret-string '{secret_json}'\n")
            
            Path(output_file).chmod(0o700)
            print(f"✓ Создан {output_file}")
            print(f"  Запустить: bash {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания AWS CLI скрипта: {e}")
            return False
    
    def backup_old_file(self) -> bool:
        """Создание резервной копии старого файла"""
        try:
            backup_file = f"{self.source_file}.backup"
            if Path(backup_file).exists():
                backup_file = f"{self.source_file}.backup.{secrets.token_hex(4)}"
            
            import shutil
            shutil.copy2(self.source_file, backup_file)
            Path(backup_file).chmod(0o600)
            
            print(f"✓ Создана резервная копия: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания резервной копии: {e}")
            return False
    
    def validate_secrets(self) -> bool:
        """Валидация загруженных секретов"""
        print("\n=== Валидация секретов ===")
        
        valid = True
        for key, value in self.secrets.items():
            status = "✓" if value else "✗"
            masked = self._mask_secret(value) if value else "отсутствует"
            print(f"{status} {key}: {masked}")
            if not value and key in ['openai_api_key', 'anthropic_api_key']:
                valid = False
        
        return valid
    
    @staticmethod
    def _mask_secret(secret: str) -> str:
        """Маскировка секрета для отображения"""
        if len(secret) < 8:
            return "***"
        return f"{secret[:4]}...{secret[-4:]}"


def main():
    parser = argparse.ArgumentParser(
        description='Миграция API ключей OneFlow.AI с .api_keys.json на переменные окружения',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  
  # Миграция в .env файл
  python migrate_to_env.py
  
  # Миграция во все форматы
  python migrate_to_env.py --all
  
  # Миграция только для Kubernetes
  python migrate_to_env.py --kubernetes
  
  # Указать другой исходный файл
  python migrate_to_env.py --source custom_keys.json
  
  # Без резервной копии
  python migrate_to_env.py --no-backup
        """
    )
    
    parser.add_argument(
        '--source',
        default='.api_keys.json',
        help='Исходный JSON файл с ключами (по умолчанию: .api_keys.json)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Экспорт во все форматы'
    )
    
    parser.add_argument(
        '--env',
        action='store_true',
        help='Экспорт в .env файл'
    )
    
    parser.add_argument(
        '--bash',
        action='store_true',
        help='Экспорт в bash скрипт'
    )
    
    parser.add_argument(
        '--docker',
        action='store_true',
        help='Экспорт для Docker Compose'
    )
    
    parser.add_argument(
        '--kubernetes',
        action='store_true',
        help='Экспорт в Kubernetes Secret'
    )
    
    parser.add_argument(
        '--aws',
        action='store_true',
        help='Экспорт в AWS Secrets Manager'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Не создавать резервную копию'
    )
    
    args = parser.parse_args()
    
    # Если не указаны флаги, экспорт в .env по умолчанию
    if not any([args.all, args.env, args.bash, args.docker, args.kubernetes, args.aws]):
        args.env = True
    
    print("=" * 60)
    print("OneFlow.AI - Миграция API ключей")
    print("=" * 60)
    
    # Создание мигратора
    migrator = SecretMigrator(args.source)
    
    # Загрузка старых ключей
    if not migrator.load_old_format():
        sys.exit(1)
    
    # Валидация
    if not migrator.validate_secrets():
        print("\n⚠️  Внимание: Некоторые обязательные ключи отсутствуют")
        response = input("Продолжить? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Резервная копия
    if not args.no_backup:
        print()
        if not migrator.backup_old_file():
            response = input("Продолжить без резервной копии? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    print("\n=== Экспорт ===")
    
    success = True
    
    # Экспорт в выбранные форматы
    if args.all or args.env:
        success &= migrator.export_to_env_file()
    
    if args.all or args.bash:
        success &= migrator.export_to_bash()
    
    if args.all or args.docker:
        success &= migrator.export_to_docker_compose()
    
    if args.all or args.kubernetes:
        success &= migrator.export_to_kubernetes()
    
    if args.all or args.aws:
        success &= migrator.export_to_aws_cli()
    
    # Итоги
    print("\n" + "=" * 60)
    if success:
        print("✓ Миграция завершена успешно!")
        print("\n📋 Следующие шаги:")
        print("1. Проверьте созданные файлы")
        print("2. Добавьте в .gitignore:")
        print("   echo '.env' >> .gitignore")
        print("   echo '.api_keys.json*' >> .gitignore")
        print("3. Удалите старый файл:")
        print(f"   rm {args.source}")
        print("4. Тестируйте приложение:")
        print("   python -m src.main --demo")
        print("\n⚠️  ВАЖНО: Удалите файлы с секретами после применения в production!")
    else:
        print("❌ Миграция завершена с ошибками")
        sys.exit(1)
    
    print("=" * 60)


if __name__ == '__main__':
    main()
