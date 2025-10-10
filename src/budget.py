"""
Расширенная система квот и бюджета
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Literal
from enum import Enum

class QuotaPeriod(Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class QuotaAction(Enum):
    HARD_STOP = "hard_stop"  # Полная остановка
    SOFT_DEGRADE = "soft_degrade"  # Снижение качества
    WARN_ONLY = "warn_only"  # Только предупреждение

@dataclass
class Quota:
    """Квота для использования"""
    limit: float
    period: QuotaPeriod
    action: QuotaAction
    current_usage: float = 0.0
    reset_at: Optional[datetime] = None
    
    def is_exceeded(self) -> bool:
        """Проверка превышения квоты"""
        return self.current_usage >= self.limit
    
    def remaining(self) -> float:
        """Оставшаяся квота"""
        return max(0, self.limit - self.current_usage)
    
    def usage_percent(self) -> float:
        """Процент использования"""
        return (self.current_usage / self.limit) * 100 if self.limit > 0 else 0

@dataclass
class BudgetPolicy:
    """Политика бюджета"""
    # Глобальные лимиты
    daily_limit: Optional[float] = None
    weekly_limit: Optional[float] = None
    monthly_limit: Optional[float] = None
    
    # Per-endpoint лимиты
    endpoint_limits: Dict[str, float] = None
    
    # Per-team лимиты
    team_limits: Dict[str, float] = None
    
    # Per-project лимиты
    project_limits: Dict[str, float] = None
    
    # Действие при исчерпании
    default_action: QuotaAction = QuotaAction.HARD_STOP
    
    # Порог предупреждения (%)
    warning_threshold: float = 80.0

class BudgetManager:
    """Менеджер бюджета с детальными квотами"""
    
    def __init__(self, policy: BudgetPolicy):
        self.policy = policy
        self.quotas: Dict[str, Quota] = {}
        self._initialize_quotas()
    
    def _initialize_quotas(self):
        """Инициализация квот"""
        if self.policy.daily_limit:
            self.quotas["global_daily"] = Quota(
                limit=self.policy.daily_limit,
                period=QuotaPeriod.DAILY,
                action=self.policy.default_action
            )
        
        if self.policy.weekly_limit:
            self.quotas["global_weekly"] = Quota(
                limit=self.policy.weekly_limit,
                period=QuotaPeriod.WEEKLY,
                action=self.policy.default_action
            )
        
        # Инициализация endpoint квот
        if self.policy.endpoint_limits:
            for endpoint, limit in self.policy.endpoint_limits.items():
                self.quotas[f"endpoint_{endpoint}"] = Quota(
                    limit=limit,
                    period=QuotaPeriod.DAILY,
                    action=self.policy.default_action
                )
    
    def check_quota(
        self,
        cost: float,
        endpoint: Optional[str] = None,
        team: Optional[str] = None,
        project: Optional[str] = None
    ) -> tuple[bool, Optional[str], QuotaAction]:
        """
        Проверка квоты перед запросом
        
        Returns:
            (allowed, reason, action)
        """
        # Проверка глобальных квот
        for quota_name, quota in self.quotas.items():
            if quota.is_exceeded():
                return False, f"Quota '{quota_name}' exceeded", quota.action
            
            # Предупреждение при приближении к лимиту
            if quota.usage_percent() >= self.policy.warning_threshold:
                # Логирование предупреждения
                pass
        
        # Проверка endpoint квоты
        if endpoint and f"endpoint_{endpoint}" in self.quotas:
            endpoint_quota = self.quotas[f"endpoint_{endpoint}"]
            if endpoint_quota.is_exceeded():
                return False, f"Endpoint '{endpoint}' quota exceeded", endpoint_quota.action
        
        # Проверка team квоты
        if team and f"team_{team}" in self.quotas:
            team_quota = self.quotas[f"team_{team}"]
            if team_quota.is_exceeded():
                return False, f"Team '{team}' quota exceeded", team_quota.action
        
        # Проверка project квоты
        if project and f"project_{project}" in self.quotas:
            project_quota = self.quotas[f"project_{project}"]
            if project_quota.is_exceeded():
                return False, f"Project '{project}' quota exceeded", project_quota.action
        
        return True, None, QuotaAction.WARN_ONLY
    
    def consume_quota(
        self,
        cost: float,
        endpoint: Optional[str] = None,
        team: Optional[str] = None,
        project: Optional[str] = None
    ):
        """Потребление квоты после выполнения запроса"""
        # Обновление всех применимых квот
        for quota_name in self.quotas:
            if quota_name.startswith("global_"):
                self.quotas[quota_name].current_usage += cost
            
            if endpoint and quota_name == f"endpoint_{endpoint}":
                self.quotas[quota_name].current_usage += cost
            
            if team and quota_name == f"team_{team}":
                self.quotas[quota_name].current_usage += cost
            
            if project and quota_name == f"project_{project}":
                self.quotas[quota_name].current_usage += cost
    
    def reset_expired_quotas(self):
        """Сброс истекших квот"""
        now = datetime.utcnow()
        
        for quota in self.quotas.values():
            if quota.reset_at and now >= quota.reset_at:
                quota.current_usage = 0.0
                quota.reset_at = self._calculate_next_reset(quota.period)
    
    def _calculate_next_reset(self, period: QuotaPeriod) -> datetime:
        """Расчет времени следующего сброса"""
        now = datetime.utcnow()
        
        if period == QuotaPeriod.HOURLY:
            return now + timedelta(hours=1)
        elif period == QuotaPeriod.DAILY:
            return now.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        elif period == QuotaPeriod.WEEKLY:
            days_until_monday = (7 - now.weekday()) % 7
            return now + timedelta(days=days_until_monday)
        elif period == QuotaPeriod.MONTHLY:
            if now.month == 12:
                return now.replace(year=now.year + 1, month=1, day=1)
            else:
                return now.replace(month=now.month + 1, day=1)
    
    def get_status(self) -> Dict:
        """Получение статуса всех квот"""
        return {
            name: {
                "limit": quota.limit,
                "used": quota.current_usage,
                "remaining": quota.remaining(),
                "usage_percent": quota.usage_percent(),
                "action": quota.action.value
            }
            for name, quota in self.quotas.items()
        }
