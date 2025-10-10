#!/usr/bin/env python3
"""
API Key Rotation Script
Автоматическая ротация API ключей для пользователей OneFlow.AI
"""
import sys
import os
import argparse
from datetime import datetime, timedelta
from typing import Optional
import json

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth_v2 import (
    APIKeyManager,
    AuthDatabase,
    APIKey
)

import structlog

logger = structlog.get_logger()


class KeyRotationService:
    """Сервис для ротации API ключей"""
    
    def __init__(self, db: AuthDatabase):
        self.db = db
    
    def rotate_user_keys(
        self,
        user_id: str,
        grace_period_days: int = 7,
        notify: bool = True
    ) -> dict:
        """
        Ротация всех активных ключей пользователя
        
        Args:
            user_id: ID пользователя
            grace_period_days: Период действия старых ключей
            notify: Отправить уведомление пользователю
        
        Returns:
            Словарь с результатами ротации
        """
        user = self.db.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        results = {
            "user_id": user_id,
            "rotated_keys": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for api_key in user.api_keys:
            if api_key.is_active:
                try:
                    new_plain_key, new_api_key, old_expiry = APIKeyManager.rotate_key(
                        api_key,
                        grace_period_days
                    )
                    
                    # Сохранение нового ключа
                    self.db.store_api_key(new_api_key)
                    
                    # Обновление срока действия старого ключа
                    api_key.expires_at = old_expiry
                    
                    results["rotated_keys"].append({
                        "old_key_id": api_key.key_id,
                        "new_key_id": new_api_key.key_id,
                        "new_key": new_plain_key,
                        "old_key_expires_at": old_expiry.isoformat(),
                        "grace_period_days": grace_period_days
                    })
                    
                    logger.info(
                        "key_rotated_successfully",
                        user_id=user_id,
                        old_key_id=api_key.key_id,
                        new_key_id=new_api_key.key_id
                    )
                    
                except Exception as e:
                    logger.error(
                        "key_rotation_failed",
                        user_id=user_id,
                        key_id=api_key.key_id,
                        error=str(e)
                    )
                    results["rotated_keys"].append({
                        "old_key_id": api_key.key_id,
                        "error": str(e)
                    })
        
        # Отправка уведомления (заглушка)
        if notify and results["rotated_keys"]:
            self._send_notification(user, results)
        
        return results
    
    def rotate_expiring_keys(
        self,
        days_threshold: int = 30,
        grace_period_days: int = 7
    ) -> list:
        """
        Ротация всех ключей, которые истекают в ближайшие N дней
        
        Args:
            days_threshold: Количество дней до истечения
            grace_period_days: Grace period для старых ключей
        
        Returns:
            Список результатов ротации
        """
        threshold_date = datetime.utcnow() + timedelta(days=days_threshold)
        results = []
        
        for user in self.db.users.values():
            expiring_keys = [
                key for key in user.api_keys
                if key.is_active 
                and key.expires_at 
                and key.expires_at <= threshold_date
            ]
            
            if expiring_keys:
                logger.info(
                    "found_expiring_keys",
                    user_id=user.user_id,
                    count=len(expiring_keys)
                )
                
                result = self.rotate_user_keys(
                    user.user_id,
                    grace_period_days,
                    notify=True
                )
                results.append(result)
        
        return results
    
    def cleanup_expired_keys(self) -> int:
        """
        Удаление истекших ключей (grace period закончился)
        
        Returns:
            Количество удалённых ключей
        """
        now = datetime.utcnow()
        deleted_count = 0
        
        for user in self.db.users.values():
            expired_keys = [
                key for key in user.api_keys
                if key.expires_at and key.expires_at < now
            ]
            
            for key in expired_keys:
                key.is_active = False
                deleted_count += 1
                
                logger.info(
                    "expired_key_deactivated",
                    user_id=user.user_id,
                    key_id=key.key_id
                )
        
        return deleted_count
    
    def _send_notification(self, user, rotation_results: dict):
        """
        Отправка email уведомления пользователю
        
        В реальной реализации использовать SendGrid/SES/SMTP
        """
        logger.info(
            "notification_sent",
            user_id=user.user_id,
            email=user.email,
            rotated_count=len(rotation_results["rotated_keys"])
        )
        
        # Заглушка для отправки email
        print(f"\n📧 Email notification to {user.email}:")
        print(f"Subject: OneFlow.AI - API Keys Rotated")
        print(f"\nYour API keys have been rotated for security.")
        print(f"Number of keys rotated: {len(rotation_results['rotated_keys'])}")
        print(f"\nNew keys:")
        for key_info in rotation_results["rotated_keys"]:
            if "new_key" in key_info:
                print(f"  - {key_info['new_key']}")
                print(f"    (Old key valid until: {key_info['old_key_expires_at']})")


def generate_rotation_report(results: list, output_file: Optional[str] = None):
    """Генерация отчёта о ротации"""
    report = {
        "rotation_date": datetime.utcnow().isoformat(),
        "total_users": len(results),
        "total_keys_rotated": sum(len(r["rotated_keys"]) for r in results),
        "results": results
    }
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✅ Report saved to {output_file}")
    else:
        print(json.dumps(report, indent=2))
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description='OneFlow.AI API Key Rotation Tool'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Ротация для конкретного пользователя
    rotate_user = subparsers.add_parser(
        'rotate-user',
        help='Rotate API keys for specific user'
    )
    rotate_user.add_argument('user_id', help='User ID')
    rotate_user.add_argument(
        '--grace-period',
        type=int,
        default=7,
        help='Grace period in days (default: 7)'
    )
    rotate_user.add_argument(
        '--no-notify',
        action='store_true',
        help='Do not send notification'
    )
    
    # Ротация истекающих ключей
    rotate_expiring = subparsers.add_parser(
        'rotate-expiring',
        help='Rotate all keys expiring soon'
    )
    rotate_expiring.add_argument(
        '--days',
        type=int,
        default=30,
        help='Rotate keys expiring in N days (default: 30)'
    )
    rotate_expiring.add_argument(
        '--grace-period',
        type=int,
        default=7,
        help='Grace period in days (default: 7)'
    )
    rotate_expiring.add_argument(
        '--output',
        help='Save report to file'
    )
    
    # Очистка истекших ключей
    cleanup = subparsers.add_parser(
        'cleanup',
        help='Deactivate expired keys'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Инициализация (в продакшене - подключение к реальной БД)
    db = AuthDatabase()
    service = KeyRotationService(db)
    
    # Выполнение команды
    if args.command == 'rotate-user':
        print(f"🔄 Rotating keys for user: {args.user_id}")
        
        result = service.rotate_user_keys(
            args.user_id,
            grace_period_days=args.grace_period,
            notify=not args.no_notify
        )
        
        print(f"✅ Rotated {len(result['rotated_keys'])} key(s)")
        print(json.dumps(result, indent=2))
    
    elif args.command == 'rotate-expiring':
        print(f"🔄 Rotating keys expiring in {args.days} days...")
        
        results = service.rotate_expiring_keys(
            days_threshold=args.days,
            grace_period_days=args.grace_period
        )
        
        report = generate_rotation_report(results, args.output)
        
        print(f"\n✅ Rotation complete!")
        print(f"   Users affected: {report['total_users']}")
        print(f"   Keys rotated: {report['total_keys_rotated']}")
    
    elif args.command == 'cleanup':
        print("🧹 Cleaning up expired keys...")
        
        deleted = service.cleanup_expired_keys()
        
        print(f"✅ Deactivated {deleted} expired key(s)")


if __name__ == "__main__":
    main()
